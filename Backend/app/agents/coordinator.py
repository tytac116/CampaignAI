"""
Coordinator Agent for Campaign Optimization

This module contains a coordinator agent that uses MCP (Model Context Protocol)
for orchestrating campaign optimization workflows.
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

from .state import CampaignOptimizationState, WorkflowStatus, Priority
from .validation import get_hallucination_grader, get_enforcer_agent

logger = logging.getLogger(__name__)

class CoordinatorAgent:
    """
    Coordinator agent for campaign optimization workflows.
    
    This coordinator uses MCP protocol for all tool interactions and manages
    the overall workflow execution with proper validation and error handling.
    """
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.1):
        self.coordinator_id = f"coordinator_{uuid.uuid4().hex[:8]}"
        self.model = model
        self.temperature = temperature
        
        # Initialize LLM with low temperature for consistent coordination
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=1500,
            timeout=60
        )
        
        # MCP connection details
        self.server_path = os.path.join(backend_dir, "mcp_server.py")
        self.mcp_tools = None
        self.mcp_agent = None
        
        # Validation tools
        self.hallucination_grader = get_hallucination_grader()
        self.enforcer_agent = get_enforcer_agent()
        
        # Workflow tracking
        self.active_workflows = {}
        self.workflow_history = []
        
        logger.info(f"✅ Initialized Coordinator: {self.coordinator_id}")
    
    async def initialize_mcp_connection(self) -> bool:
        """Initialize MCP connection and load tools."""
        try:
            if self.mcp_agent:
                return True  # Already initialized
                
            logger.info(f"🔗 {self.coordinator_id}: Initializing MCP connection...")
            
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
                    logger.info(f"✅ {self.coordinator_id}: Loaded {len(self.mcp_tools)} MCP tools")
                    
                    # Create LangGraph ReAct agent with MCP tools
                    self.mcp_agent = create_react_agent(self.llm, self.mcp_tools)
                    logger.info(f"✅ {self.coordinator_id}: MCP-integrated coordinator created")
                    
                    return True
                    
        except Exception as e:
            logger.error(f"❌ {self.coordinator_id}: MCP connection failed: {str(e)}")
            return False
    
    async def coordinate_campaign_optimization(self, 
                                             campaign_ids: List[int],
                                             trigger_reason: str = "api_request",
                                             priority: Priority = Priority.MEDIUM,
                                             user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Coordinate a complete campaign optimization workflow using MCP tools.
        
        Args:
            campaign_ids: List of campaign IDs to optimize
            trigger_reason: Reason for triggering the optimization
            priority: Priority level for the workflow
            user_context: Additional context from the user
            
        Returns:
            Complete workflow results with MCP tool tracing
        """
        workflow_id = f"mcp_workflow_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now()
        
        logger.info(f"🚀 {self.coordinator_id}: Starting workflow {workflow_id}")
        logger.info(f"📋 Campaign IDs: {campaign_ids}")
        logger.info(f"🎯 Priority: {priority.value}")
        
        # Initialize workflow state
        workflow_state = {
            "workflow_id": workflow_id,
            "coordinator_id": self.coordinator_id,
            "campaign_ids": campaign_ids,
            "trigger_reason": trigger_reason,
            "priority": priority,
            "user_context": user_context or {},
            "started_at": start_time.isoformat(),
            "status": "running",
            "current_phase": "initialization",
            "phases_completed": [],
            "tool_calls": [],
            "validation_results": [],
            "errors": [],
            "results": {}
        }
        
        # Track active workflow
        self.active_workflows[workflow_id] = workflow_state
        
        try:
            # Ensure MCP connection
            if not await self.initialize_mcp_connection():
                raise Exception("Failed to establish MCP connection")
            
            # Phase 1: Campaign Monitoring
            logger.info(f"📊 {workflow_id}: Phase 1 - Campaign Monitoring")
            monitoring_result = await self._execute_monitoring_phase(workflow_state)
            workflow_state["phases_completed"].append("monitoring")
            workflow_state["results"]["monitoring"] = monitoring_result
            
            # Phase 2: Data Analysis (if monitoring found issues)
            if monitoring_result.get("alerts_found", 0) > 0:
                logger.info(f"🔍 {workflow_id}: Phase 2 - Data Analysis")
                analysis_result = await self._execute_analysis_phase(workflow_state)
                workflow_state["phases_completed"].append("analysis")
                workflow_state["results"]["analysis"] = analysis_result
                
                # Phase 3: Optimization
                logger.info(f"🎯 {workflow_id}: Phase 3 - Optimization")
                optimization_result = await self._execute_optimization_phase(workflow_state)
                workflow_state["phases_completed"].append("optimization")
                workflow_state["results"]["optimization"] = optimization_result
            else:
                logger.info(f"✅ {workflow_id}: No issues found, skipping analysis and optimization")
            
            # Phase 4: Reporting
            logger.info(f"📋 {workflow_id}: Phase 4 - Reporting")
            reporting_result = await self._execute_reporting_phase(workflow_state)
            workflow_state["phases_completed"].append("reporting")
            workflow_state["results"]["reporting"] = reporting_result
            
            # Finalize workflow
            workflow_state["status"] = "completed"
            workflow_state["current_phase"] = "completed"
            workflow_state["completed_at"] = datetime.now().isoformat()
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            workflow_state["execution_time_seconds"] = execution_time
            
            logger.info(f"✅ {workflow_id}: Completed in {execution_time:.2f}s")
            logger.info(f"📊 Total tool calls: {len(workflow_state['tool_calls'])}")
            logger.info(f"🔄 Phases completed: {len(workflow_state['phases_completed'])}")
            
            # Move to history
            self.workflow_history.append(workflow_state)
            del self.active_workflows[workflow_id]
            
            return workflow_state
            
        except Exception as e:
            logger.error(f"❌ {workflow_id}: Workflow failed: {str(e)}")
            workflow_state["status"] = "failed"
            workflow_state["current_phase"] = "failed"
            workflow_state["errors"].append({
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "phase": workflow_state.get("current_phase", "unknown")
            })
            workflow_state["completed_at"] = datetime.now().isoformat()
            
            # Move to history even if failed
            self.workflow_history.append(workflow_state)
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
            
            return workflow_state
    
    async def _execute_monitoring_phase(self, workflow_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute campaign monitoring phase using MCP tools."""
        workflow_state["current_phase"] = "monitoring"
        
        # Build monitoring prompt
        monitoring_prompt = self._build_monitoring_prompt(workflow_state)
        
        # Execute via MCP
        result = await self._execute_with_mcp(monitoring_prompt, {
            "campaign_ids": workflow_state["campaign_ids"],
            "workflow_id": workflow_state["workflow_id"],
            "phase": "monitoring"
        })
        
        # Update workflow state
        workflow_state["tool_calls"].extend(result["tool_calls"])
        workflow_state["validation_results"].append(result["validation"])
        
        if not result["success"]:
            raise Exception(f"Monitoring phase failed: {result.get('error', 'Unknown error')}")
        
        # Parse monitoring results
        monitoring_data = self._parse_monitoring_output(result["output"])
        
        return {
            "success": True,
            "campaigns_analyzed": monitoring_data.get("campaigns_analyzed", []),
            "alerts_found": len(monitoring_data.get("alerts", [])),
            "alerts": monitoring_data.get("alerts", []),
            "summary": monitoring_data.get("summary", {}),
            "tool_calls": len(result["tool_calls"]),
            "validation": result["validation"]
        }
    
    async def _execute_analysis_phase(self, workflow_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data analysis phase using MCP tools."""
        workflow_state["current_phase"] = "analysis"
        
        # Build analysis prompt
        analysis_prompt = self._build_analysis_prompt(workflow_state)
        
        # Execute via MCP
        result = await self._execute_with_mcp(analysis_prompt, {
            "monitoring_results": workflow_state["results"]["monitoring"],
            "workflow_id": workflow_state["workflow_id"],
            "phase": "analysis"
        })
        
        # Update workflow state
        workflow_state["tool_calls"].extend(result["tool_calls"])
        workflow_state["validation_results"].append(result["validation"])
        
        if not result["success"]:
            raise Exception(f"Analysis phase failed: {result.get('error', 'Unknown error')}")
        
        # Parse analysis results
        analysis_data = self._parse_analysis_output(result["output"])
        
        return {
            "success": True,
            "insights_generated": len(analysis_data.get("insights", [])),
            "insights": analysis_data.get("insights", []),
            "trend_analysis": analysis_data.get("trend_analysis", {}),
            "competitive_analysis": analysis_data.get("competitive_analysis", {}),
            "tool_calls": len(result["tool_calls"]),
            "validation": result["validation"]
        }
    
    async def _execute_optimization_phase(self, workflow_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute optimization phase using MCP tools."""
        workflow_state["current_phase"] = "optimization"
        
        # Build optimization prompt
        optimization_prompt = self._build_optimization_prompt(workflow_state)
        
        # Execute via MCP
        result = await self._execute_with_mcp(optimization_prompt, {
            "monitoring_results": workflow_state["results"]["monitoring"],
            "analysis_results": workflow_state["results"]["analysis"],
            "workflow_id": workflow_state["workflow_id"],
            "phase": "optimization"
        })
        
        # Update workflow state
        workflow_state["tool_calls"].extend(result["tool_calls"])
        workflow_state["validation_results"].append(result["validation"])
        
        if not result["success"]:
            raise Exception(f"Optimization phase failed: {result.get('error', 'Unknown error')}")
        
        # Parse optimization results
        optimization_data = self._parse_optimization_output(result["output"])
        
        return {
            "success": True,
            "recommendations_generated": len(optimization_data.get("recommendations", [])),
            "recommendations": optimization_data.get("recommendations", []),
            "optimized_content": optimization_data.get("optimized_content", {}),
            "implementation_plan": optimization_data.get("implementation_plan", {}),
            "roi_projection": optimization_data.get("roi_projection", {}),
            "tool_calls": len(result["tool_calls"]),
            "validation": result["validation"]
        }
    
    async def _execute_reporting_phase(self, workflow_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute reporting phase using MCP tools."""
        workflow_state["current_phase"] = "reporting"
        
        # Build reporting prompt
        reporting_prompt = self._build_reporting_prompt(workflow_state)
        
        # Execute via MCP
        result = await self._execute_with_mcp(reporting_prompt, {
            "all_results": workflow_state["results"],
            "workflow_id": workflow_state["workflow_id"],
            "phase": "reporting"
        })
        
        # Update workflow state
        workflow_state["tool_calls"].extend(result["tool_calls"])
        workflow_state["validation_results"].append(result["validation"])
        
        if not result["success"]:
            raise Exception(f"Reporting phase failed: {result.get('error', 'Unknown error')}")
        
        # Parse reporting results
        reporting_data = self._parse_reporting_output(result["output"])
        
        return {
            "success": True,
            "executive_summary": reporting_data.get("executive_summary", {}),
            "final_report": reporting_data,
            "tool_calls": len(result["tool_calls"]),
            "validation": result["validation"]
        }
    
    async def _execute_with_mcp(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task using MCP tools with validation."""
        try:
            # Execute via MCP agent
            response = await self.mcp_agent.ainvoke({"messages": [("human", prompt)]})
            
            # Extract results
            final_message = response["messages"][-1].content
            tool_calls_made = self._extract_tool_calls(response["messages"])
            
            # Validate output for hallucinations
            validation_result = self.hallucination_grader.grade_output(
                final_message,
                context=prompt,
                source_data=json.dumps(context)
            )
            
            # Check iteration limits
            enforcer_result = self.enforcer_agent.should_continue(
                self.coordinator_id,
                operation=f"coordinate_{context.get('phase', 'unknown')}"
            )
            
            return {
                "output": final_message,
                "tool_calls": tool_calls_made,
                "validation": validation_result,
                "enforcer_check": enforcer_result,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ {self.coordinator_id}: MCP execution failed: {str(e)}")
            return {
                "output": f"Error: {str(e)}",
                "tool_calls": [],
                "validation": {"is_hallucination": False, "confidence": 0.0},
                "enforcer_check": {"should_continue": False},
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
    
    def _extract_tool_calls(self, messages: List) -> List[Dict[str, Any]]:
        """Extract and log all tool calls made."""
        tool_calls = []
        
        for message in messages:
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tool_call in message.tool_calls:
                    call_info = {
                        "sequence": len(tool_calls) + 1,
                        "tool_name": tool_call['name'],
                        "arguments": tool_call['args'],
                        "timestamp": datetime.now().isoformat()
                    }
                    tool_calls.append(call_info)
                    logger.info(f"🔧 {self.coordinator_id} Tool Call #{call_info['sequence']}: {tool_call['name']}")
        
        return tool_calls
    
    def _build_monitoring_prompt(self, workflow_state: Dict[str, Any]) -> str:
        """Build monitoring prompt for MCP execution."""
        campaign_ids_str = ", ".join(map(str, workflow_state["campaign_ids"]))
        
        return f"""You are the MCP Coordinator Agent executing campaign monitoring.

**WORKFLOW CONTEXT:**
- Workflow ID: {workflow_state['workflow_id']}
- Campaign IDs: {campaign_ids_str}
- Priority: {workflow_state['priority'].value}
- Trigger: {workflow_state['trigger_reason']}

**MONITORING OBJECTIVES:**
1. Retrieve current campaign data from Facebook and Instagram
2. Analyze performance metrics and identify issues
3. Generate alerts for campaigns needing attention
4. Provide performance summary

**REQUIRED MCP TOOLS:**
Use Facebook and Instagram campaign API tools to gather comprehensive data.

**OUTPUT FORMAT:**
Provide structured JSON with campaigns analyzed, alerts generated, and summary metrics.

Execute monitoring using available MCP tools."""
    
    def _build_analysis_prompt(self, workflow_state: Dict[str, Any]) -> str:
        """Build analysis prompt for MCP execution."""
        monitoring_results = json.dumps(workflow_state["results"]["monitoring"], indent=2)
        
        return f"""You are the MCP Coordinator Agent executing data analysis.

**WORKFLOW CONTEXT:**
- Workflow ID: {workflow_state['workflow_id']}
- Previous Phase: Monitoring completed

**MONITORING RESULTS:**
{monitoring_results}

**ANALYSIS OBJECTIVES:**
1. Perform trend analysis on campaign performance
2. Search for similar campaigns and patterns
3. Conduct competitive market research
4. Generate actionable insights

**REQUIRED MCP TOOLS:**
Use vector search, web search, and analysis tools for comprehensive insights.

**OUTPUT FORMAT:**
Provide structured JSON with trend analysis, competitive insights, and recommendations.

Execute analysis using available MCP tools."""
    
    def _build_optimization_prompt(self, workflow_state: Dict[str, Any]) -> str:
        """Build optimization prompt for MCP execution."""
        monitoring_results = json.dumps(workflow_state["results"]["monitoring"], indent=2)
        analysis_results = json.dumps(workflow_state["results"]["analysis"], indent=2)
        
        return f"""You are the MCP Coordinator Agent executing optimization.

**WORKFLOW CONTEXT:**
- Workflow ID: {workflow_state['workflow_id']}
- Previous Phases: Monitoring and Analysis completed

**PREVIOUS RESULTS:**
Monitoring: {monitoring_results}
Analysis: {analysis_results}

**OPTIMIZATION OBJECTIVES:**
1. Generate specific optimization recommendations
2. Create optimized content and strategies
3. Provide implementation roadmap
4. Estimate ROI impact

**REQUIRED MCP TOOLS:**
Use optimization and content generation tools for actionable recommendations.

**OUTPUT FORMAT:**
Provide structured JSON with recommendations, content, implementation plan, and ROI projections.

Execute optimization using available MCP tools."""
    
    def _build_reporting_prompt(self, workflow_state: Dict[str, Any]) -> str:
        """Build reporting prompt for MCP execution."""
        all_results = json.dumps(workflow_state["results"], indent=2)
        
        return f"""You are the MCP Coordinator Agent generating final reports.

**WORKFLOW CONTEXT:**
- Workflow ID: {workflow_state['workflow_id']}
- All Phases: {', '.join(workflow_state['phases_completed'])}
- Total Tool Calls: {len(workflow_state['tool_calls'])}

**COMPLETE WORKFLOW RESULTS:**
{all_results}

**REPORTING OBJECTIVES:**
1. Create executive summary of findings
2. Compile comprehensive performance report
3. Provide prioritized action items
4. Include ROI projections and next steps

**OUTPUT FORMAT:**
Generate professional executive report with summary, analysis, recommendations, and action plan.

Create final report using available MCP tools if needed."""
    
    def _parse_monitoring_output(self, output: str) -> Dict[str, Any]:
        """Parse monitoring output and extract structured data."""
        try:
            json_start = output.find('{')
            json_end = output.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = output[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"raw_output": output}
        except Exception as e:
            logger.error(f"❌ Failed to parse monitoring output: {str(e)}")
            return {"error": str(e), "raw_output": output}
    
    def _parse_analysis_output(self, output: str) -> Dict[str, Any]:
        """Parse analysis output and extract structured data."""
        try:
            json_start = output.find('{')
            json_end = output.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = output[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"raw_output": output}
        except Exception as e:
            logger.error(f"❌ Failed to parse analysis output: {str(e)}")
            return {"error": str(e), "raw_output": output}
    
    def _parse_optimization_output(self, output: str) -> Dict[str, Any]:
        """Parse optimization output and extract structured data."""
        try:
            json_start = output.find('{')
            json_end = output.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = output[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"raw_output": output}
        except Exception as e:
            logger.error(f"❌ Failed to parse optimization output: {str(e)}")
            return {"error": str(e), "raw_output": output}
    
    def _parse_reporting_output(self, output: str) -> Dict[str, Any]:
        """Parse reporting output and extract structured data."""
        try:
            json_start = output.find('{')
            json_end = output.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = output[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"raw_output": output}
        except Exception as e:
            logger.error(f"❌ Failed to parse reporting output: {str(e)}")
            return {"error": str(e), "raw_output": output}
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a workflow."""
        # Check active workflows
        if workflow_id in self.active_workflows:
            return self.active_workflows[workflow_id]
        
        # Check workflow history
        for workflow in self.workflow_history:
            if workflow["workflow_id"] == workflow_id:
                return workflow
        
        return None
    
    async def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List all currently active workflows."""
        return list(self.active_workflows.values())
    
    async def get_workflow_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent workflow history."""
        return self.workflow_history[-limit:] if self.workflow_history else []

# Factory function for easy instantiation
def create_coordinator(model: str = "gpt-4o-mini", temperature: float = 0.1) -> CoordinatorAgent:
    """Create a new coordinator agent."""
    return CoordinatorAgent(model=model, temperature=temperature)