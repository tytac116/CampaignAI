"""
Workflow Nodes for Campaign Optimization

This module contains workflow nodes that use MCP (Model Context Protocol)
for all tool interactions instead of direct API calls.
"""

import os
import sys
import asyncio
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add Backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

from .validation import get_hallucination_grader, get_enforcer_agent
from .state import CampaignOptimizationState, CampaignData, AlertData, Priority, ReportData

logger = logging.getLogger(__name__)

class BaseWorkflowNode:
    """Base class for workflow nodes that use MCP protocol."""
    
    def __init__(self, node_type: str, model: str = "gpt-4o-mini", temperature: float = 0.3):
        self.node_id = f"{node_type}_{uuid.uuid4().hex[:8]}"
        self.node_type = node_type
        self.model = model
        self.temperature = temperature
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=2000,
            timeout=60
        )
        
        # MCP connection details
        self.server_path = os.path.join(backend_dir, "mcp_server.py")
        self.mcp_tools = None
        self.mcp_agent = None
        
        # Validation tools
        self.hallucination_grader = get_hallucination_grader()
        self.enforcer_agent = get_enforcer_agent()
        
        logger.info(f"✅ Initialized {node_type} Node: {self.node_id}")
    
    async def initialize_mcp_connection(self) -> bool:
        """Initialize MCP connection and load tools."""
        try:
            if self.mcp_agent:
                return True  # Already initialized
                
            logger.info(f"🔗 {self.node_id}: Initializing MCP connection...")
            
            # Create server parameters
            server_params = StdioServerParameters(
                command="python3",
                args=[self.server_path],
            )
            
            # Connect to MCP server and load tools
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Load MCP tools
                    self.mcp_tools = await load_mcp_tools(session)
                    logger.info(f"✅ {self.node_id}: Loaded {len(self.mcp_tools)} MCP tools")
                    
                    # Create LangGraph ReAct agent with MCP tools
                    self.mcp_agent = create_react_agent(self.llm, self.mcp_tools)
                    logger.info(f"✅ {self.node_id}: MCP-integrated agent created")
                    
                    return True
                    
        except Exception as e:
            logger.error(f"❌ {self.node_id}: MCP connection failed: {str(e)}")
            return False
    
    async def execute_with_mcp(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a task using MCP tools with validation."""
        try:
            # Ensure MCP connection
            if not await self.initialize_mcp_connection():
                raise Exception("Failed to establish MCP connection")
            
            # Check enforcer limits
            enforcer_result = self.enforcer_agent.should_continue(
                self.node_id,
                operation=f"{self.node_type}_execute"
            )
            
            if not enforcer_result["should_continue"]:
                return {
                    "success": False,
                    "error": f"Enforcer blocked execution: {enforcer_result['reason']}",
                    "output": "",
                    "tool_calls": [],
                    "validation": {"is_valid": False, "reason": "enforcer_blocked"}
                }
            
            # Execute via MCP agent
            messages = [HumanMessage(content=prompt)]
            response = await self.mcp_agent.ainvoke({"messages": messages})
            
            # Extract final output
            final_message = response["messages"][-1]
            output = final_message.content if hasattr(final_message, 'content') else str(final_message)
            
            # Extract tool calls
            tool_calls = self._extract_tool_calls(response["messages"])
            
            # Validate output
            validation_result = self.hallucination_grader.grade_output(
                output,
                context=prompt,
                source_data=json.dumps(context or {})
            )
            
            return {
                "success": True,
                "output": output,
                "tool_calls": tool_calls,
                "validation": {
                    "is_valid": not validation_result["is_hallucination"],
                    "confidence": validation_result["confidence"],
                    "reasoning": validation_result.get("reasoning", "")
                }
            }
            
        except Exception as e:
            logger.error(f"❌ {self.node_id}: MCP execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "output": f"Error: {str(e)}",
                "tool_calls": [],
                "validation": {"is_valid": False, "reason": "execution_error"}
            }
    
    def _extract_tool_calls(self, messages: List) -> List[Dict[str, Any]]:
        """Extract tool call information from messages."""
        tool_calls = []
        sequence = 1
        
        for message in messages:
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tool_call in message.tool_calls:
                    call_info = {
                        "sequence": sequence,
                        "name": tool_call["name"],
                        "args": tool_call.get("args", {}),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    tool_calls.append(call_info)
                    logger.info(f"🔧 {self.node_id} Tool Call #{call_info['sequence']}: {tool_call['name']}")
                    sequence += 1
        
        return tool_calls
    
    def _log_execution(self, state: CampaignOptimizationState, message: str):
        """Add execution log entry."""
        timestamp = datetime.utcnow().isoformat()
        state["execution_log"].append(f"[{timestamp}] {self.node_id}: {message}")
        state["updated_at"] = datetime.utcnow()
    
    async def execute(self, state: CampaignOptimizationState) -> CampaignOptimizationState:
        """Execute the node. Must be implemented by subclasses."""
        raise NotImplementedError

class CampaignMonitorNode(BaseWorkflowNode):
    """Node for monitoring campaign performance and detecting anomalies."""
    
    def __init__(self):
        super().__init__("monitor", temperature=0.2)
    
    async def execute(self, state: CampaignOptimizationState) -> CampaignOptimizationState:
        """Execute campaign monitoring using MCP tools."""
        self._log_execution(state, "Starting campaign monitoring")
        
        try:
            # Build monitoring prompt
            monitoring_prompt = self._build_monitoring_prompt(state)
            
            # Execute via MCP
            result = await self.execute_with_mcp(monitoring_prompt, {
                "campaign_ids": state["campaign_ids"],
                "workflow_id": state["workflow_id"]
            })
            
            if result["success"]:
                # Parse the monitoring results
                await self._parse_monitoring_results(state, result)
                
                state["completed_agents"].append(self.node_id)
                state["agent_outputs"][self.node_id] = {
                    "campaigns_monitored": len(state.get("campaigns", [])),
                    "alerts_generated": len(state.get("alerts", [])),
                    "tool_calls": len(result["tool_calls"]),
                    "status": "completed",
                    "validation": result["validation"]
                }
                
                self._log_execution(state, f"Monitoring completed. Found {len(state.get('alerts', []))} alerts")
            else:
                raise Exception(result.get("error", "MCP execution failed"))
                
        except Exception as e:
            error_msg = f"Error in campaign monitoring: {str(e)}"
            state["errors"].append({
                "agent": self.node_id,
                "error": error_msg,
                "timestamp": datetime.utcnow().isoformat()
            })
            self._log_execution(state, error_msg)
        
        return state
    
    def _build_monitoring_prompt(self, state: CampaignOptimizationState) -> str:
        """Build comprehensive monitoring prompt for MCP execution."""
        campaign_ids_str = ", ".join(map(str, state["campaign_ids"]))
        
        return f"""You are a Campaign AI Agent performing comprehensive campaign monitoring via MCP tools.

**MONITORING OBJECTIVES:**
1. Retrieve current campaign data from Facebook and Instagram APIs
2. Analyze campaign performance metrics
3. Identify performance issues and anomalies
4. Generate alerts for campaigns needing attention
5. Calculate key performance indicators

**CAMPAIGN IDS TO MONITOR:**
{campaign_ids_str}

**REQUIRED MCP TOOL USAGE:**
1. Use `mcp_get_facebook_campaigns` to retrieve Facebook campaign data
2. Use `mcp_get_facebook_campaign_details` for detailed Facebook insights
3. Use `mcp_get_instagram_campaigns` to retrieve Instagram campaign data
4. Use `mcp_get_instagram_campaign_details` for detailed Instagram insights

Execute the monitoring using the available MCP tools and provide structured analysis."""
    
    async def _parse_monitoring_results(self, state: CampaignOptimizationState, result: Dict[str, Any]):
        """Parse monitoring results and update state."""
        try:
            output = result["output"]
            
            # Create basic campaign and alert data from output
            state["campaigns"] = []
            state["alerts"] = []
            state["monitoring_summary"] = {"raw_output": output, "tool_calls": len(result["tool_calls"])}
                
        except Exception as e:
            logger.error(f"❌ {self.node_id}: Failed to parse monitoring results: {str(e)}")
            state["campaigns"] = []
            state["alerts"] = []
            state["monitoring_summary"] = {"error": str(e), "raw_output": result["output"]}

class DataAnalysisNode(BaseWorkflowNode):
    """Node for performing data analysis and trend detection."""
    
    def __init__(self):
        super().__init__("analysis", temperature=0.3)
    
    async def execute(self, state: CampaignOptimizationState) -> CampaignOptimizationState:
        """Perform data analysis using MCP tools."""
        self._log_execution(state, "Starting data analysis")
        
        try:
            # Build analysis prompt
            analysis_prompt = self._build_analysis_prompt(state)
            
            # Execute via MCP
            result = await self.execute_with_mcp(analysis_prompt, {
                "campaigns": state.get("campaigns", []),
                "alerts": state.get("alerts", []),
                "workflow_id": state["workflow_id"]
            })
            
            if result["success"]:
                # Parse analysis results
                await self._parse_analysis_results(state, result)
                
                state["completed_agents"].append(self.node_id)
                state["agent_outputs"][self.node_id] = {
                    "analysis_completed": True,
                    "tool_calls": len(result["tool_calls"]),
                    "status": "completed",
                    "validation": result["validation"]
                }
                
                self._log_execution(state, "Data analysis completed")
            else:
                raise Exception(result.get("error", "MCP execution failed"))
                
        except Exception as e:
            error_msg = f"Error in data analysis: {str(e)}"
            state["errors"].append({
                "agent": self.node_id,
                "error": error_msg,
                "timestamp": datetime.utcnow().isoformat()
            })
            self._log_execution(state, error_msg)
        
        return state
    
    def _build_analysis_prompt(self, state: CampaignOptimizationState) -> str:
        """Build analysis prompt."""
        return f"""Analyze campaign data and trends using MCP tools.
        
Campaign data: {state.get('monitoring_summary', {})}
Alerts: {len(state.get('alerts', []))} alerts found

Use vector search and analysis tools to identify patterns and insights."""
    
    async def _parse_analysis_results(self, state: CampaignOptimizationState, result: Dict[str, Any]):
        """Parse analysis results."""
        state["analysis_results"] = {"output": result["output"], "tool_calls": len(result["tool_calls"])}
        state["insights"] = []

class OptimizationNode(BaseWorkflowNode):
    """Node for generating optimization recommendations."""
    
    def __init__(self):
        super().__init__("optimization", temperature=0.4)
    
    async def execute(self, state: CampaignOptimizationState) -> CampaignOptimizationState:
        """Generate optimization recommendations using MCP tools."""
        self._log_execution(state, "Starting optimization")
        
        try:
            # Build optimization prompt
            optimization_prompt = self._build_optimization_prompt(state)
            
            # Execute via MCP
            result = await self.execute_with_mcp(optimization_prompt, {
                "analysis_results": state.get("analysis_results", {}),
                "campaigns": state.get("campaigns", []),
                "workflow_id": state["workflow_id"]
            })
            
            if result["success"]:
                # Parse optimization results
                await self._parse_optimization_results(state, result)
                
                state["completed_agents"].append(self.node_id)
                state["agent_outputs"][self.node_id] = {
                    "recommendations_generated": len(state.get("recommendations", [])),
                    "tool_calls": len(result["tool_calls"]),
                    "status": "completed",
                    "validation": result["validation"]
                }
                
                self._log_execution(state, f"Generated {len(state.get('recommendations', []))} recommendations")
            else:
                raise Exception(result.get("error", "MCP execution failed"))
                
        except Exception as e:
            error_msg = f"Error in optimization: {str(e)}"
            state["errors"].append({
                "agent": self.node_id,
                "error": error_msg,
                "timestamp": datetime.utcnow().isoformat()
            })
            self._log_execution(state, error_msg)
        
        return state
    
    def _build_optimization_prompt(self, state: CampaignOptimizationState) -> str:
        """Build optimization prompt."""
        return f"""Generate optimization recommendations using MCP tools.
        
Analysis results: {state.get('analysis_results', {})}
Campaign count: {len(state.get('campaigns', []))}

Use LLM tools to generate actionable optimization strategies."""
    
    async def _parse_optimization_results(self, state: CampaignOptimizationState, result: Dict[str, Any]):
        """Parse optimization results."""
        state["recommendations"] = []
        state["optimization_results"] = {"output": result["output"], "tool_calls": len(result["tool_calls"])}

class ReportingNode(BaseWorkflowNode):
    """Node for generating comprehensive reports."""
    
    def __init__(self):
        super().__init__("reporting", temperature=0.2)
    
    async def execute(self, state: CampaignOptimizationState) -> CampaignOptimizationState:
        """Generate comprehensive reports using MCP tools."""
        self._log_execution(state, "Starting report generation")
        
        try:
            # Build reporting prompt
            reporting_prompt = self._build_reporting_prompt(state)
            
            # Execute via MCP
            result = await self.execute_with_mcp(reporting_prompt, {
                "optimization_results": state.get("optimization_results", {}),
                "analysis_results": state.get("analysis_results", {}),
                "monitoring_summary": state.get("monitoring_summary", {}),
                "workflow_id": state["workflow_id"]
            })
            
            if result["success"]:
                # Parse reporting results
                await self._parse_reporting_results(state, result)
                
                state["completed_agents"].append(self.node_id)
                state["agent_outputs"][self.node_id] = {
                    "reports_generated": len(state.get("reports", [])),
                    "tool_calls": len(result["tool_calls"]),
                    "status": "completed",
                    "validation": result["validation"]
                }
                
                self._log_execution(state, "Report generation completed")
            else:
                raise Exception(result.get("error", "MCP execution failed"))
                
        except Exception as e:
            error_msg = f"Error in reporting: {str(e)}"
            state["errors"].append({
                "agent": self.node_id,
                "error": error_msg,
                "timestamp": datetime.utcnow().isoformat()
            })
            self._log_execution(state, error_msg)
        
        return state
    
    def _build_reporting_prompt(self, state: CampaignOptimizationState) -> str:
        """Build reporting prompt."""
        return f"""Generate comprehensive campaign optimization report using MCP tools.
        
Workflow ID: {state['workflow_id']}
Completed agents: {len(state.get('completed_agents', []))}
Total errors: {len(state.get('errors', []))}

Create a detailed report summarizing all findings and recommendations."""
    
    async def _parse_reporting_results(self, state: CampaignOptimizationState, result: Dict[str, Any]):
        """Parse reporting results."""
        state["reports"] = []
        state["final_report"] = result["output"]

# Factory functions
def create_monitor_node() -> CampaignMonitorNode:
    """Create a campaign monitor node."""
    return CampaignMonitorNode()

def create_analysis_node() -> DataAnalysisNode:
    """Create a data analysis node."""
    return DataAnalysisNode()

def create_optimization_node() -> OptimizationNode:
    """Create an optimization node."""
    return OptimizationNode()

def create_reporting_node() -> ReportingNode:
    """Create a reporting node."""
    return ReportingNode()