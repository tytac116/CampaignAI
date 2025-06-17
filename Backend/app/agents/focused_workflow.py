#!/usr/bin/env python3
"""
Focused Campaign Workflow

This workflow is specifically designed for simple campaign queries like:
"Show me the top 10 best performing campaigns"

It follows a simple path: Intent → Data → Response (no unnecessary steps)
"""

import os
import sys
import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add Backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# MCP imports
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

logger = logging.getLogger(__name__)

class FocusedWorkflowState(TypedDict):
    """Focused state for simple campaign queries."""
    workflow_id: str
    user_question: str
    current_step: str
    
    # Intent analysis
    intent_type: str  # "top_campaigns", "campaign_analysis", "campaign_action"
    needs_ranking: bool
    
    # Data
    raw_campaign_data: str
    processed_campaigns: List[Dict[str, Any]]
    
    # Response
    final_answer: str
    
    # Tracking
    tool_calls: List[str]
    errors: List[str]
    
    # Metadata
    started_at: str
    completed_at: Optional[str]
    status: str

class FocusedCampaignWorkflow:
    """Focused workflow for simple campaign queries."""
    
    def __init__(self):
        self.workflow_id = f"focused_workflow_{uuid.uuid4().hex[:8]}"
        self.mcp_server_path = os.path.join(backend_dir, "mcp_server.py")
        
        # Initialize LLM for intent analysis and response formatting
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        
        # Build the focused graph
        self.graph = self._build_focused_graph()
        
        logger.info(f"✅ Initialized Focused Campaign Workflow: {self.workflow_id}")
    
    def _build_focused_graph(self) -> StateGraph:
        """Build a simple, focused workflow graph."""
        workflow = StateGraph(FocusedWorkflowState)
        
        # Add only essential nodes
        workflow.add_node("analyze_intent", self._analyze_intent_node)
        workflow.add_node("get_campaign_data", self._get_campaign_data_node)
        workflow.add_node("process_and_respond", self._process_and_respond_node)
        
        # Set entry point
        workflow.set_entry_point("analyze_intent")
        
        # Simple linear flow - no branching to avoid getting stuck
        workflow.add_edge("analyze_intent", "get_campaign_data")
        workflow.add_edge("get_campaign_data", "process_and_respond")
        workflow.add_edge("process_and_respond", END)
        
        # Compile without memory to avoid state issues
        return workflow.compile()
    
    async def _analyze_intent_node(self, state: FocusedWorkflowState) -> FocusedWorkflowState:
        """Quick intent analysis - determine what the user wants."""
        logger.info(f"🧠 Analyzing intent: {state['user_question']}")
        
        try:
            # Simple keyword-based intent detection
            question_lower = state['user_question'].lower()
            
            if any(word in question_lower for word in ['top', 'best', 'performing', 'highest']):
                state['intent_type'] = 'top_campaigns'
                state['needs_ranking'] = True
                logger.info("📊 Intent: User wants top performing campaigns")
            elif any(word in question_lower for word in ['analyze', 'performance', 'how are']):
                state['intent_type'] = 'campaign_analysis' 
                state['needs_ranking'] = False
                logger.info("🔍 Intent: User wants campaign analysis")
            else:
                state['intent_type'] = 'campaign_action'
                state['needs_ranking'] = False
                logger.info("🎯 Intent: User wants to take action")
            
            state['current_step'] = 'intent_analyzed'
            logger.info(f"✅ Intent analysis completed: {state['intent_type']}")
            
        except Exception as e:
            logger.error(f"❌ Intent analysis failed: {str(e)}")
            state['errors'].append(f"Intent analysis error: {str(e)}")
            state['intent_type'] = 'unknown'
        
        return state
    
    async def _get_campaign_data_node(self, state: FocusedWorkflowState) -> FocusedWorkflowState:
        """Get campaign data via direct MCP call."""
        logger.info(f"📊 Getting campaign data for: {state['intent_type']}")
        
        try:
            # Direct MCP call to get campaign data
            server_params = StdioServerParameters(
                command="python3",
                args=[self.mcp_server_path],
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Get Facebook campaigns
                    logger.info("📱 Calling mcp_get_facebook_campaigns...")
                    fb_result = await session.call_tool('mcp_get_facebook_campaigns', {'limit': 20})
                    fb_data = fb_result.content[0].text
                    
                    state['raw_campaign_data'] = fb_data
                    state['tool_calls'].append('mcp_get_facebook_campaigns')
                    
                    logger.info(f"✅ Got {len(fb_data)} characters of campaign data")
                    
                    # If user wants top campaigns, also get Instagram data
                    if state['intent_type'] == 'top_campaigns':
                        logger.info("📱 Also getting Instagram campaigns...")
                        ig_result = await session.call_tool('mcp_get_instagram_campaigns', {'limit': 10})
                        ig_data = ig_result.content[0].text
                        
                        state['raw_campaign_data'] += "\n\n" + ig_data
                        state['tool_calls'].append('mcp_get_instagram_campaigns')
                        
                        logger.info(f"✅ Added Instagram data")
            
            state['current_step'] = 'data_collected'
            logger.info(f"✅ Campaign data collection completed")
            
        except Exception as e:
            logger.error(f"❌ Campaign data collection failed: {str(e)}")
            state['errors'].append(f"Data collection error: {str(e)}")
            state['raw_campaign_data'] = ""
        
        return state
    
    async def _process_and_respond_node(self, state: FocusedWorkflowState) -> FocusedWorkflowState:
        """Process the data and create a focused response."""
        logger.info(f"🔄 Processing data and creating response")
        
        try:
            # Use LLM to process the campaign data and create a focused response
            if state['intent_type'] == 'top_campaigns':
                response_prompt = f"""
                You are a campaign performance analyst. The user asked: "{state['user_question']}"
                
                Here is the campaign data:
                {state['raw_campaign_data'][:2000]}
                
                Create a clear, concise response that:
                1. Lists the top 10 best performing campaigns
                2. Shows key metrics (ROAS, CTR, conversions, etc.)
                3. Ranks them by performance
                4. Uses a friendly, conversational tone
                
                Format as a chatbot response - clear and easy to read.
                """
            else:
                response_prompt = f"""
                You are a campaign performance analyst. The user asked: "{state['user_question']}"
                
                Here is the campaign data:
                {state['raw_campaign_data'][:2000]}
                
                Create a clear, helpful response that directly answers their question.
                Use a friendly, conversational tone like a chatbot.
                """
            
            # Get LLM response
            response = await self.llm.ainvoke([HumanMessage(content=response_prompt)])
            final_answer = response.content
            
            # Clean up and format the response
            state['final_answer'] = self._format_final_response(final_answer, state)
            state['current_step'] = 'response_ready'
            state['status'] = 'completed'
            state['completed_at'] = datetime.now().isoformat()
            
            logger.info(f"✅ Response generated: {len(state['final_answer'])} characters")
            
        except Exception as e:
            logger.error(f"❌ Response generation failed: {str(e)}")
            state['errors'].append(f"Response generation error: {str(e)}")
            state['final_answer'] = f"I apologize, but I encountered an error while processing your request: {str(e)}"
            state['status'] = 'failed'
        
        return state
    
    def _format_final_response(self, llm_response: str, state: FocusedWorkflowState) -> str:
        """Format the final response to be chatbot-friendly."""
        
        # Add execution metadata
        execution_time = (datetime.now() - datetime.fromisoformat(state['started_at'])).total_seconds()
        
        formatted_response = f"""🤖 **Campaign AI Assistant**

{llm_response}

---
📊 *Analysis completed in {execution_time:.1f}s using {len(state['tool_calls'])} data sources*
"""
        
        return formatted_response
    
    async def ask_question(self, user_question: str) -> str:
        """Main method to ask a question and get an answer."""
        logger.info(f"❓ User question: {user_question}")
        
        # Create initial state
        initial_state = {
            "workflow_id": self.workflow_id,
            "user_question": user_question,
            "current_step": "starting",
            "intent_type": "",
            "needs_ranking": False,
            "raw_campaign_data": "",
            "processed_campaigns": [],
            "final_answer": "",
            "tool_calls": [],
            "errors": [],
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "status": "running"
        }
        
        try:
            # Run the workflow
            final_state = await self.graph.ainvoke(initial_state)
            
            if final_state['status'] == 'completed':
                logger.info(f"✅ Question answered successfully")
                return final_state['final_answer']
            else:
                logger.error(f"❌ Workflow failed: {final_state.get('errors', [])}")
                return f"I apologize, but I couldn't process your question due to technical issues."
                
        except Exception as e:
            logger.error(f"❌ Workflow execution failed: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"

# Factory function
def create_focused_workflow() -> FocusedCampaignWorkflow:
    """Create a new focused workflow instance."""
    return FocusedCampaignWorkflow()

# Test function
async def test_focused_workflow():
    """Test the focused workflow with the specific question."""
    
    logger.info("🧪 Testing Focused Workflow")
    logger.info("=" * 50)
    
    # Create workflow
    workflow = create_focused_workflow()
    
    # Test the specific question
    test_question = "Show me the top 10 best performing campaigns"
    
    logger.info(f"❓ Testing: {test_question}")
    
    # Get answer
    answer = await workflow.ask_question(test_question)
    
    logger.info("=" * 50)
    logger.info("🤖 ANSWER:")
    logger.info("=" * 50)
    print(answer)
    logger.info("=" * 50)
    
    return answer

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Run test
    result = asyncio.run(test_focused_workflow())
    print(f"\nTest completed. Answer length: {len(result)} characters") 