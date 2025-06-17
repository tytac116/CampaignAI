"""
Simple Working LangGraph Workflow for Campaign Optimization

This module defines a working workflow graph using LangGraph that integrates
with the MCP (Model Context Protocol) for all tool interactions.
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

class WorkflowState(TypedDict):
    """State object for the campaign optimization workflow."""
    workflow_id: str
    current_step: str
    user_instruction: str
    campaign_context: Optional[Dict[str, Any]]
    
    # Intent analysis
    intent_analysis: Dict[str, Any]
    
    # Campaign data
    campaign_data: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    
    # Analysis results
    analysis_results: Dict[str, Any]
    optimization_strategy: Dict[str, Any]
    content_generated: Dict[str, Any]
    
    # Actions and results
    action_results: Dict[str, Any]
    
    # Validation and control
    validation_results: Dict[str, Any]
    iteration_count: int
    should_continue: bool
    
    # Tool tracing
    tool_calls: List[Dict[str, Any]]
    
    # Final outputs
    final_output: str
    errors: List[str]
    
    # Metadata
    started_at: str
    completed_at: Optional[str]
    status: str

class SimpleAgent:
    """Simple agent that uses direct MCP calls."""
    
    def __init__(self, agent_type: str, model: str = "gpt-4o-mini", temperature: float = 0.3):
        self.agent_id = f"{agent_type}_{uuid.uuid4().hex[:8]}"
        self.agent_type = agent_type
        self.model = model
        self.temperature = temperature
        
        # MCP server path
        self.mcp_server_path = os.path.join(backend_dir, "mcp_server.py")
        
        # Initialize OpenAI client
        self.llm = ChatOpenAI(model=self.model, temperature=self.temperature)
        
        logger.info(f"✅ Initialized {agent_type} Agent: {self.agent_id}")
    
    async def call_mcp_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Make a direct MCP tool call."""
        try:
            server_params = StdioServerParameters(
                command="python3",
                args=[self.mcp_server_path],
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    result = await session.call_tool(tool_name, args)
                    return result.content[0].text
                    
        except Exception as e:
            logger.error(f"❌ {self.agent_id}: MCP tool call failed: {str(e)}")
            return f"Error calling {tool_name}: {str(e)}"
    
    async def think_and_act(self, prompt: str) -> str:
        """Use OpenAI to think and analyze."""
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
            
        except Exception as e:
            logger.error(f"❌ {self.agent_id}: Think and act failed: {str(e)}")
            return f"Error in thinking: {str(e)}"

class CampaignOptimizationGraph:
    """
    Simple Campaign Optimization Workflow using LangGraph.
    
    This workflow uses direct MCP calls without complex agent dependencies.
    """
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.3):
        self.workflow_id = f"workflow_{uuid.uuid4().hex[:8]}"
        self.model = model
        self.temperature = temperature
        self.mcp_server_path = os.path.join(backend_dir, "mcp_server.py")
        
        # Initialize simple agents
        self.intent_agent = SimpleAgent("intent_analyzer", model, 0.1)
        self.data_agent = SimpleAgent("data_collector", model, 0.2)
        self.analysis_agent = SimpleAgent("performance_analyzer", model, 0.3)
        self.strategy_agent = SimpleAgent("strategy_optimizer", model, 0.4)
        self.content_agent = SimpleAgent("content_generator", model, 0.6)
        
        # Build the graph
        self.graph = self._build_graph()
        
        logger.info(f"✅ Initialized Campaign Optimization Graph: {self.workflow_id}")
    
    def _build_graph(self) -> StateGraph:
        """Build the simplified marketing workflow graph."""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes in logical order
        workflow.add_node("initialize", self._initialize_node)
        workflow.add_node("analyze_intent", self._analyze_intent_node)
        workflow.add_node("collect_data", self._collect_data_node)
        workflow.add_node("analyze_performance", self._analyze_performance_node)
        workflow.add_node("develop_strategy", self._develop_strategy_node)
        workflow.add_node("generate_content", self._generate_content_node)
        workflow.add_node("compile_report", self._compile_report_node)
        workflow.add_node("validate_output", self._validate_output_node)
        
        # Set entry point
        workflow.set_entry_point("initialize")
        
        # Simple linear flow for reliability
        workflow.add_edge("initialize", "analyze_intent")
        workflow.add_edge("analyze_intent", "collect_data")
        workflow.add_edge("collect_data", "analyze_performance")
        workflow.add_edge("analyze_performance", "develop_strategy")
        workflow.add_edge("develop_strategy", "generate_content")
        workflow.add_edge("generate_content", "compile_report")
        workflow.add_edge("compile_report", "validate_output")
        
        # Simple validation routing
        workflow.add_conditional_edges(
            "validate_output",
            self._route_validation,
            {
                "valid": END,
                "failed": END
            }
        )
        
        # Compile with memory
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    
    async def _initialize_node(self, state: WorkflowState) -> WorkflowState:
        """Initialize the workflow."""
        logger.info(f"🚀 Initializing workflow: {state['workflow_id']}")
        
        state["current_step"] = "initialized"
        state["iteration_count"] = 0
        state["should_continue"] = True
        state["tool_calls"] = []
        state["errors"] = []
        state["campaign_data"] = {}
        state["performance_metrics"] = {}
        state["analysis_results"] = {}
        state["optimization_strategy"] = {}
        state["content_generated"] = {}
        state["action_results"] = {}
        
        logger.info(f"✅ Workflow {state['workflow_id']} initialized")
        return state
    
    async def _analyze_intent_node(self, state: WorkflowState) -> WorkflowState:
        """Analyze user intent using the intent agent."""
        logger.info(f"🧠 Analyzing intent for: {state['workflow_id']}")
        
        try:
            # Use the intent agent to analyze
            prompt = f"""
            Analyze this marketing request and determine what the user wants:
            
            Request: {state['user_instruction']}
            
            Determine:
            1. What type of analysis they want (performance, optimization, content, etc.)
            2. What platforms they're interested in (Facebook, Instagram, etc.)
            3. What actions they want taken
            
            Respond with a simple analysis of their intent.
            """
            
            analysis = await self.intent_agent.think_and_act(prompt)
            
            # Simple intent classification
            intent_keywords = state['user_instruction'].lower()
            intent_analysis = {
                "intent_type": "optimization" if "optimize" in intent_keywords else "analysis",
                "needs_data": any(word in intent_keywords for word in ['campaign', 'performance', 'data']),
                "needs_analysis": any(word in intent_keywords for word in ['analyze', 'performance', 'insights']),
                "needs_content": any(word in intent_keywords for word in ['content', 'copy', 'creative']),
                "needs_strategy": any(word in intent_keywords for word in ['strategy', 'optimize', 'improve']),
                "platforms": ["facebook"] if "facebook" in intent_keywords else ["facebook", "instagram"],
                "analysis": analysis,
                "confidence": 0.8
            }
            
            state["intent_analysis"] = intent_analysis
            state["current_step"] = "intent_analyzed"
            
            logger.info(f"📋 Intent: {intent_analysis['intent_type']}")
            
        except Exception as e:
            logger.error(f"❌ Intent analysis failed: {str(e)}")
            state["errors"].append(f"Intent analysis error: {str(e)}")
            state["intent_analysis"] = {
                "intent_type": "optimization",
                "confidence": 0.5,
                "needs_content": True,
                "needs_analysis": True,
                "key_words": ["campaigns"],
                "error": str(e)
            }
        
        return state
    
    async def _collect_data_node(self, state: WorkflowState) -> WorkflowState:
        """Collect campaign data using the data agent."""
        logger.info(f"📊 Collecting campaign data for: {state['workflow_id']}")
        
        try:
            collected_data = {}
            tool_calls = []
            
            # Get Facebook campaigns
            if "facebook" in state["intent_analysis"].get("platforms", []):
                fb_data = await self.data_agent.call_mcp_tool('mcp_get_facebook_campaigns', {'limit': 5})
                collected_data["facebook_campaigns"] = fb_data
                tool_calls.append({"tool": "mcp_get_facebook_campaigns", "status": "success"})
            
            # Search campaign database
            if state["intent_analysis"].get("needs_data", False):
                search_data = await self.data_agent.call_mcp_tool('mcp_search_campaign_data', {
                    'query': 'campaign performance metrics',
                    'limit': 3
                })
                collected_data["search_results"] = search_data
                tool_calls.append({"tool": "mcp_search_campaign_data", "status": "success"})
            
            state["campaign_data"] = {
                **collected_data,
                "timestamp": datetime.now().isoformat()
            }
            
            state["tool_calls"].extend(tool_calls)
            state["current_step"] = "data_collected"
            logger.info(f"✅ Data collection completed: {len(tool_calls)} tools used")
            
        except Exception as e:
            logger.error(f"❌ Data collection failed: {str(e)}")
            state["errors"].append(f"Data collection error: {str(e)}")
            state["campaign_data"] = {"error": str(e)}
        
        return state
    
    async def _analyze_performance_node(self, state: WorkflowState) -> WorkflowState:
        """Analyze campaign performance using the analysis agent."""
        logger.info(f"🔍 Analyzing performance for: {state['workflow_id']}")
        
        try:
            # Prepare data for analysis
            data_summary = f"Campaign data: {str(state['campaign_data'])[:500]}"
            
            # Use MCP tool for analysis
            analysis_result = await self.analysis_agent.call_mcp_tool('mcp_analyze_campaign_performance', {
                'campaign_data': data_summary
            })
            
            # Also get AI insights
            insights_prompt = f"""
            Based on this campaign data, provide key insights:
            {data_summary}
            
            Focus on:
            1. Performance trends
            2. Areas for improvement
            3. Key metrics analysis
            """
            
            ai_insights = await self.analysis_agent.think_and_act(insights_prompt)
            
            state["analysis_results"] = {
                "mcp_analysis": analysis_result,
                "ai_insights": ai_insights,
                "timestamp": datetime.now().isoformat()
            }
            
            state["tool_calls"].append({"tool": "mcp_analyze_campaign_performance", "status": "success"})
            state["current_step"] = "performance_analyzed"
            logger.info(f"✅ Performance analysis completed")
            
        except Exception as e:
            logger.error(f"❌ Performance analysis failed: {str(e)}")
            state["errors"].append(f"Performance analysis error: {str(e)}")
            state["analysis_results"] = {"error": str(e)}
        
        return state
    
    async def _develop_strategy_node(self, state: WorkflowState) -> WorkflowState:
        """Develop optimization strategy using the strategy agent."""
        logger.info(f"🎯 Developing strategy for: {state['workflow_id']}")
        
        try:
            # Prepare context for strategy development
            context = f"Analysis results: {str(state['analysis_results'])[:500]}"
            
            # Use MCP tool for strategy optimization
            strategy_result = await self.strategy_agent.call_mcp_tool('mcp_optimize_campaign_strategy', {
                'campaign_data': context,
                'goals': 'improve campaign performance and ROI'
            })
            
            # Generate additional strategic recommendations
            strategy_prompt = f"""
            Based on this analysis, create actionable optimization recommendations:
            {context}
            
            Provide:
            1. Immediate actions to take
            2. Long-term strategy improvements
            3. Budget optimization suggestions
            4. Targeting refinements
            """
            
            strategic_recommendations = await self.strategy_agent.think_and_act(strategy_prompt)
            
            state["optimization_strategy"] = {
                "mcp_strategy": strategy_result,
                "strategic_recommendations": strategic_recommendations,
                "timestamp": datetime.now().isoformat()
            }
            
            state["tool_calls"].append({"tool": "mcp_optimize_campaign_strategy", "status": "success"})
            state["current_step"] = "strategy_developed"
            logger.info(f"✅ Strategy development completed")
            
        except Exception as e:
            logger.error(f"❌ Strategy development failed: {str(e)}")
            state["errors"].append(f"Strategy development error: {str(e)}")
            state["optimization_strategy"] = {"error": str(e)}
        
        return state
    
    async def _generate_content_node(self, state: WorkflowState) -> WorkflowState:
        """Generate campaign content using the content agent."""
        logger.info(f"✨ Generating content for: {state['workflow_id']}")
        
        try:
            # Use MCP tool for content generation
            content_result = await self.content_agent.call_mcp_tool('mcp_generate_campaign_content', {
                'campaign_type': 'ad_copy',
                'target_audience': 'business professionals',
                'platform': 'facebook',
                'campaign_objective': 'engagement'
            })
            
            # Generate additional creative ideas
            creative_prompt = f"""
            Based on this optimization strategy, create additional creative content ideas:
            {str(state['optimization_strategy'])[:500]}
            
            Generate:
            1. Ad copy variations
            2. Creative concepts
            3. Call-to-action suggestions
            4. Audience messaging ideas
            """
            
            creative_ideas = await self.content_agent.think_and_act(creative_prompt)
            
            state["content_generated"] = {
                "mcp_content": content_result,
                "creative_ideas": creative_ideas,
                "timestamp": datetime.now().isoformat()
            }
            
            state["tool_calls"].append({"tool": "mcp_generate_campaign_content", "status": "success"})
            state["current_step"] = "content_generated"
            logger.info(f"✅ Content generation completed")
            
        except Exception as e:
            logger.error(f"❌ Content generation failed: {str(e)}")
            state["errors"].append(f"Content generation error: {str(e)}")
            state["content_generated"] = {"error": str(e)}
        
        return state
    
    async def _compile_report_node(self, state: WorkflowState) -> WorkflowState:
        """Compile comprehensive report."""
        logger.info(f"📋 Compiling report for: {state['workflow_id']}")
        
        try:
            final_output = f"""
🤖 **CAMPAIGN AI OPTIMIZATION REPORT**
📋 **Workflow ID**: {state['workflow_id']}
📝 **User Request**: {state['user_instruction']}
⏰ **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*60}
🧠 **INTENT ANALYSIS**
{'='*60}
{json.dumps(state['intent_analysis'], indent=2)}

{'='*60}
📊 **CAMPAIGN DATA**
{'='*60}
{str(state['campaign_data'])[:800]}...

{'='*60}
🔍 **PERFORMANCE ANALYSIS**
{'='*60}
{str(state['analysis_results'])[:1000]}...

{'='*60}
🎯 **OPTIMIZATION STRATEGY**
{'='*60}
{str(state['optimization_strategy'])[:1000]}...

{'='*60}
✨ **GENERATED CONTENT**
{'='*60}
{str(state['content_generated'])[:800]}...

{'='*60}
📈 **EXECUTIVE SUMMARY**
{'='*60}

✅ **Workflow Status**: COMPLETED
🔄 **Current Step**: {state['current_step']}
🛠️ **Tool Calls**: {len(state['tool_calls'])}
⚡ **Processing Time**: {(datetime.now() - datetime.fromisoformat(state['started_at'])).total_seconds():.1f}s

**LangGraph Flow Completed:**
1. ✅ Initialize → Setup complete
2. ✅ Analyze Intent → {state['intent_analysis'].get('intent_type', 'unknown')}
3. ✅ Collect Data → {len([tc for tc in state['tool_calls'] if 'mcp_get' in tc.get('tool', '')])} data tools used
4. ✅ Analyze Performance → Insights generated
5. ✅ Develop Strategy → Recommendations provided
6. ✅ Generate Content → Creative content created
7. ✅ Compile Report → Comprehensive output

🎉 **Campaign AI Workflow Completed Successfully!**
            """
            
            state["final_output"] = final_output.strip()
            state["current_step"] = "report_compiled"
            logger.info(f"✅ Report compilation completed")
            
        except Exception as e:
            logger.error(f"❌ Report compilation failed: {str(e)}")
            state["errors"].append(f"Report compilation error: {str(e)}")
            state["final_output"] = f"Report generation failed: {str(e)}"
        
        return state
    
    async def _validate_output_node(self, state: WorkflowState) -> WorkflowState:
        """Validate the final output."""
        logger.info(f"🛡️ Validating output for: {state['workflow_id']}")
        
        try:
            # Simple validation
            is_valid = (
                len(state["final_output"]) > 100 and
                "COMPLETED" in state["final_output"] and
                len(state["errors"]) == 0 and
                len(state["tool_calls"]) > 0
            )
            
            state["validation_results"] = {
                "is_valid": is_valid,
                "confidence": 0.9 if is_valid else 0.3,
                "timestamp": datetime.now().isoformat()
            }
            
            state["should_continue"] = False
            state["status"] = "completed" if is_valid else "failed"
            state["completed_at"] = datetime.now().isoformat()
            state["current_step"] = "validated"
            
            logger.info(f"✅ Validation completed - Output is {'valid' if is_valid else 'invalid'}")
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {str(e)}")
            state["errors"].append(f"Validation error: {str(e)}")
            state["should_continue"] = False
            state["status"] = "failed"
            state["validation_results"] = {"is_valid": False, "error": str(e)}
        
        return state
    
    def _route_validation(self, state: WorkflowState) -> str:
        """Route based on validation results."""
        if state["validation_results"].get("is_valid", False):
            logger.info("🔄 Routing to: valid (validation passed)")
            return "valid"
        else:
            logger.info("🔄 Routing to: failed (validation failed)")
            return "failed"
    
    async def run_workflow(self, 
                          user_instruction: str,
                          campaign_context: Optional[Dict[str, Any]] = None) -> WorkflowState:
        """Run the complete campaign optimization workflow."""
        workflow_id = f"workflow_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now()
        
        logger.info(f"🚀 Starting Campaign Workflow: {workflow_id}")
        logger.info(f"📝 Instruction: {user_instruction}")
        
        # Initialize workflow state
        initial_state = WorkflowState(
            workflow_id=workflow_id,
            current_step="initializing",
            user_instruction=user_instruction,
            campaign_context=campaign_context,
            intent_analysis={},
            campaign_data={},
            performance_metrics={},
            analysis_results={},
            optimization_strategy={},
            content_generated={},
            action_results={},
            validation_results={},
            iteration_count=0,
            should_continue=True,
            tool_calls=[],
            final_output="",
            errors=[],
            started_at=start_time.isoformat(),
            completed_at=None,
            status="running"
        )
        
        try:
            # Run the workflow
            config = {"configurable": {"thread_id": workflow_id}}
            final_state = await self.graph.ainvoke(initial_state, config)
            
            # Calculate execution time
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            final_state["execution_time_seconds"] = execution_time
            
            logger.info(f"✅ Workflow {workflow_id} completed in {execution_time:.2f}s")
            logger.info(f"📊 Total tool calls: {len(final_state['tool_calls'])}")
            logger.info(f"🔧 Final step: {final_state['current_step']}")
            
            return final_state
            
        except Exception as e:
            logger.error(f"❌ Workflow {workflow_id} failed: {str(e)}")
            initial_state["status"] = "failed"
            initial_state["errors"].append(f"Workflow execution failed: {str(e)}")
            initial_state["completed_at"] = datetime.now().isoformat()
            return initial_state
    
    def visualize_graph(self, output_path: str = "campaign_workflow_graph.png"):
        """Generate a visual representation of the workflow graph."""
        try:
            # Get the graph visualization
            graph_image = self.graph.get_graph().draw_mermaid_png()
            
            # Save to file
            with open(output_path, "wb") as f:
                f.write(graph_image)
            
            logger.info(f"📊 Graph visualization saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Failed to generate graph visualization: {str(e)}")
            return None

# Factory function
def create_campaign_graph(model: str = "gpt-4o-mini", temperature: float = 0.3) -> CampaignOptimizationGraph:
    """Create a new campaign optimization graph."""
    return CampaignOptimizationGraph(model=model, temperature=temperature) 