"""
Campaign Agent for Campaign AI System

This agent handles campaign analysis, optimization, and content generation
using the MCP (Model Context Protocol) for tool integration.
"""

import os
import sys
import asyncio
import logging
import json
from typing import Dict, Any, List, Optional
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

# MCP imports
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

logger = logging.getLogger(__name__)

class CampaignAgent:
    """
    Simplified Campaign Agent that uses direct MCP calls.
    
    This agent handles campaign analysis, optimization, and content generation
    without complex LangGraph dependencies that cause recursion issues.
    """
    
    def __init__(self, 
                 model: str = "gpt-4o-mini",
                 temperature: float = 0.3,
                 max_iterations: int = 5):
        """Initialize the Campaign Agent."""
        self.agent_id = f"campaign_agent_{uuid.uuid4().hex[:8]}"
        self.model = model
        self.temperature = temperature
        self.max_iterations = max_iterations
        
        # MCP server configuration
        self.server_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "mcp_server.py")
        
        # Initialize OpenAI client
        self.llm = ChatOpenAI(model=self.model, temperature=self.temperature)
        
        logger.info(f"✅ Initialized Campaign Agent: {self.agent_id}")
        logger.info(f"🔧 Model: {self.model}, Temperature: {self.temperature}")
        logger.info(f"📍 MCP Server Path: {self.server_path}")
    
    async def execute_campaign_workflow(self, 
                                      user_instruction: str,
                                      campaign_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute campaign workflow using direct MCP calls.
        
        This method uses direct MCP tool calls without complex agent workflows
        to prevent recursion issues.
        
        Args:
            user_instruction: Natural language instruction from user
            campaign_context: Optional context about campaigns
            
        Returns:
            Workflow results with tool calls and analysis
        """
        workflow_id = f"campaign_workflow_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now()
        
        logger.info(f"🚀 Starting Campaign Workflow: {workflow_id}")
        logger.info(f"📝 Instruction: {user_instruction}")
        
        results = {
            "agent_id": self.agent_id,
            "workflow_id": workflow_id,
            "started_at": start_time.isoformat(),
            "user_instruction": user_instruction,
            "campaign_context": campaign_context,
            "tool_calls": [],
            "final_output": "",
            "status": "running"
        }
        
        try:
            # Create direct MCP session for this workflow
            server_params = StdioServerParameters(
                command="python3",
                args=[self.server_path],
            )
            
            # Use context manager for proper session handling
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as mcp_session:
                    await mcp_session.initialize()
                    
                    # Analyze user intent to determine which tools to use
                    intent_keywords = user_instruction.lower()
                    tool_calls_made = []
                    analysis_parts = []
                    
                    # Step 1: Get campaign data if needed
                    if any(word in intent_keywords for word in ['campaign', 'performance', 'analyze', 'optimize']):
                        logger.info("📊 Getting campaign data...")
                        
                        # Get Facebook campaigns
                        fb_result = await mcp_session.call_tool('mcp_get_facebook_campaigns', {'limit': 5})
                        fb_data = fb_result.content[0].text
                        tool_calls_made.append({
                            "tool": "mcp_get_facebook_campaigns",
                            "args": {"limit": 5},
                            "result_length": len(fb_data)
                        })
                        analysis_parts.append(f"**Current Facebook Campaigns:**\n{fb_data[:800]}...")
                        
                        # Search for relevant campaigns
                        if any(word in intent_keywords for word in ['ai', 'marketing', 'search']):
                            search_result = await mcp_session.call_tool('mcp_search_campaign_data', {
                                'query': 'marketing campaign performance',
                                'limit': 3
                            })
                            search_data = search_result.content[0].text
                            tool_calls_made.append({
                                "tool": "mcp_search_campaign_data", 
                                "args": {"query": "marketing campaign performance", "limit": 3},
                                "result_length": len(search_data)
                            })
                            analysis_parts.append(f"**Campaign Search Results:**\n{search_data[:600]}...")
                    
                    # Step 2: Perform analysis if requested
                    if any(word in intent_keywords for word in ['analyze', 'performance', 'insights']):
                        logger.info("🔍 Performing campaign analysis...")
                        
                        # Use sample campaign data for analysis
                        sample_campaign = "Campaign: Marketing Excellence, Budget: R8000, Spend: R5200, ROAS: 2.1x, CTR: 2.8%, Platform: Facebook"
                        analysis_result = await mcp_session.call_tool('mcp_analyze_campaign_performance', {
                            'campaign_data': sample_campaign
                        })
                        analysis_data = analysis_result.content[0].text
                        tool_calls_made.append({
                            "tool": "mcp_analyze_campaign_performance",
                            "args": {"campaign_data": sample_campaign},
                            "result_length": len(analysis_data)
                        })
                        analysis_parts.append(f"**AI Performance Analysis:**\n{analysis_data[:1000]}...")
                    
                    # Step 3: Generate optimization strategy if requested
                    if any(word in intent_keywords for word in ['optimize', 'strategy', 'improve', 'recommendations']):
                        logger.info("🎯 Generating optimization strategy...")
                        
                        strategy_result = await mcp_session.call_tool('mcp_optimize_campaign_strategy', {
                            'campaign_data': 'Current campaign with 2.1x ROAS and 2.8% CTR',
                            'goals': 'increase ROAS to 3.5x and improve CTR to 4.5%'
                        })
                        strategy_data = strategy_result.content[0].text
                        tool_calls_made.append({
                            "tool": "mcp_optimize_campaign_strategy",
                            "args": {"campaign_data": "Current campaign with 2.1x ROAS and 2.8% CTR", "goals": "increase ROAS to 3.5x and improve CTR to 4.5%"},
                            "result_length": len(strategy_data)
                        })
                        analysis_parts.append(f"**Optimization Strategy:**\n{strategy_data[:1000]}...")
                    
                    # Step 4: Generate content if requested
                    if any(word in intent_keywords for word in ['content', 'copy', 'creative', 'generate']):
                        logger.info("✨ Generating campaign content...")
                        
                        content_result = await mcp_session.call_tool('mcp_generate_campaign_content', {
                            'campaign_type': 'ad_copy',
                            'target_audience': 'business professionals aged 25-50',
                            'platform': 'facebook',
                            'campaign_objective': 'lead_generation'
                        })
                        content_data = content_result.content[0].text
                        tool_calls_made.append({
                            "tool": "mcp_generate_campaign_content",
                            "args": {"campaign_type": "ad_copy", "target_audience": "business professionals aged 25-50", "platform": "facebook", "campaign_objective": "lead_generation"},
                            "result_length": len(content_data)
                        })
                        analysis_parts.append(f"**Generated Content:**\n{content_data[:800]}...")
                    
                    # Step 5: Create campaign if requested
                    if any(word in intent_keywords for word in ['create', 'new campaign', 'launch']):
                        logger.info("🚀 Creating new campaign...")
                        
                        create_result = await mcp_session.call_tool('mcp_create_campaign', {
                            'name': f'AI Generated Campaign {datetime.now().strftime("%Y%m%d_%H%M")}',
                            'platform': 'facebook',
                            'objective': 'lead_generation',
                            'budget_amount': 3000.0,
                            'budget_type': 'daily'
                        })
                        create_data = create_result.content[0].text
                        tool_calls_made.append({
                            "tool": "mcp_create_campaign",
                            "args": {"name": f'AI Generated Campaign {datetime.now().strftime("%Y%m%d_%H%M")}', "platform": "facebook", "objective": "lead_generation", "budget_amount": 3000.0, "budget_type": "daily"},
                            "result_length": len(create_data)
                        })
                        analysis_parts.append(f"**Campaign Creation:**\n{create_data[:500]}...")
                    
                    # Compile final comprehensive output
                    final_output = f"""
🤖 **CAMPAIGN AI DIRECT WORKFLOW RESULTS**
📋 **Workflow ID**: {workflow_id}
📝 **User Request**: {user_instruction}
⏰ **Executed**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*60}
📊 **COMPREHENSIVE ANALYSIS & RESULTS**
{'='*60}

{chr(10).join(analysis_parts)}

{'='*60}
📈 **EXECUTION SUMMARY**
{'='*60}

✅ **Tools Used**: {len(tool_calls_made)}
🔧 **Tool Details**:
{chr(10).join([f"   • {call['tool']}: {call.get('result_length', 0)} chars" for call in tool_calls_made])}

⚡ **Processing Time**: {(datetime.now() - start_time).total_seconds():.1f}s
🎯 **Status**: COMPLETED

🎉 **Campaign AI Direct Workflow Completed Successfully!**
                    """
                    
                    results.update({
                        "tool_calls": tool_calls_made,
                        "final_output": final_output.strip(),
                        "status": "completed",
                        "completed_at": datetime.now().isoformat(),
                        "execution_time_seconds": (datetime.now() - start_time).total_seconds()
                    })
                    
                    logger.info(f"✅ Campaign workflow {workflow_id} completed successfully")
                    logger.info(f"🛠️ Used {len(tool_calls_made)} MCP tools")
                    
                    return results
                    
        except Exception as e:
            logger.error(f"❌ Campaign workflow {workflow_id} failed: {str(e)}")
            results.update({
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.now().isoformat(),
                "final_output": f"Campaign workflow failed: {str(e)}"
            })
            return results
    
    async def execute_campaign_optimization(self, 
                                          instruction: str,
                                          campaign_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute campaign optimization workflow.
        
        This is an alias for execute_campaign_workflow for backward compatibility.
        """
        return await self.execute_campaign_workflow(instruction, campaign_context)
    
    def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities and configuration."""
        return {
            "agent_id": self.agent_id,
            "model": self.model,
            "temperature": self.temperature,
            "max_iterations": self.max_iterations,
            "server_path": self.server_path,
            "capabilities": [
                "campaign_analysis",
                "performance_optimization", 
                "content_generation",
                "strategy_development",
                "campaign_creation",
                "data_collection"
            ],
            "available_tools": [
                "mcp_get_facebook_campaigns",
                "mcp_search_campaign_data",
                "mcp_analyze_campaign_performance",
                "mcp_optimize_campaign_strategy",
                "mcp_generate_campaign_content",
                "mcp_create_campaign"
            ]
        }

# Factory function
def get_campaign_agent() -> CampaignAgent:
    """Get a Campaign Agent instance."""
    return CampaignAgent() 