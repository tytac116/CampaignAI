"""
LangGraph Workflow for Campaign Optimization

This module defines a workflow graph using LangGraph that integrates
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
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from .validation import get_hallucination_grader, get_enforcer_agent
from .campaign_agent import CampaignAgent
from .campaign_action_agent import CampaignActionAgent

logger = logging.getLogger(__name__)

class WorkflowState(TypedDict):
    """State object for the campaign optimization workflow."""
    workflow_id: str
    current_step: str
    user_instruction: str
    campaign_context: Optional[Dict[str, Any]]
    
    # Intent analysis
    intent_analysis: Dict[str, Any]
    
    # Agent results
    monitoring_results: Dict[str, Any]
    analysis_results: Dict[str, Any]
    optimization_results: Dict[str, Any]
    action_results: Dict[str, Any]
    reporting_results: Dict[str, Any]
    
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

class CampaignOptimizationGraph:
    """
    Enhanced LangGraph workflow for campaign optimization with action capabilities.
    
    This class creates and manages a state graph that uses MCP protocol
    for all tool interactions, including intelligent intent analysis and
    multi-agent coordination for both analysis and action requests.
    """
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.3):
        self.workflow_id = f"workflow_{uuid.uuid4().hex[:8]}"
        self.model = model
        self.temperature = temperature
        
        # Initialize agents
        self.campaign_agent = CampaignAgent(model=model, temperature=temperature)
        self.action_agent = CampaignActionAgent(model=model, temperature=0.2)  # Lower temp for actions
        
        # Validation tools
        self.hallucination_grader = get_hallucination_grader()
        self.enforcer_agent = get_enforcer_agent()
        
        # Build the graph
        self.graph = self._build_graph()
        
        logger.info(f"✅ Initialized Enhanced Campaign Optimization Graph: {self.workflow_id}")
        logger.info(f"🤖 Agents: Campaign Agent + Action Agent")
    
    def _build_graph(self) -> StateGraph:
        """Build the enhanced LangGraph workflow with action capabilities."""
        # Create the state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("initialize", self._initialize_node)
        workflow.add_node("analyze_intent", self._analyze_intent_node)
        workflow.add_node("monitor_campaigns", self._monitor_campaigns_node)
        workflow.add_node("analyze_data", self._analyze_data_node)
        workflow.add_node("execute_actions", self._execute_actions_node)
        workflow.add_node("optimize_campaigns", self._optimize_campaigns_node)
        workflow.add_node("generate_report", self._generate_report_node)
        workflow.add_node("validate_output", self._validate_output_node)
        
        # Set entry point
        workflow.set_entry_point("initialize")
        
        # Add edges
        workflow.add_edge("initialize", "analyze_intent")
        
        # Add conditional routing based on intent
        workflow.add_conditional_edges(
            "analyze_intent",
            self._route_by_intent,
            {
                "analysis": "monitor_campaigns",
                "action": "execute_actions",
                "hybrid": "monitor_campaigns"
            }
        )
        
        workflow.add_edge("monitor_campaigns", "analyze_data")
        
        # Conditional routing after analysis
        workflow.add_conditional_edges(
            "analyze_data",
            self._route_after_analysis,
            {
                "action_needed": "execute_actions",
                "optimization": "optimize_campaigns",
                "report": "generate_report"
            }
        )
        
        workflow.add_edge("execute_actions", "generate_report")
        workflow.add_edge("optimize_campaigns", "generate_report")
        workflow.add_edge("generate_report", "validate_output")
        
        # Add conditional edge from validation
        workflow.add_conditional_edges(
            "validate_output",
            self._should_continue,
            {
                "continue": "monitor_campaigns",  # Loop back if needed
                "end": END
            }
        )
        
        # Compile with memory
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    
    async def _initialize_node(self, state: WorkflowState) -> WorkflowState:
        """Initialize the workflow."""
        logger.info(f"🚀 Initializing enhanced workflow: {state['workflow_id']}")
        
        # Ensure MCP connections for both agents
        await self.campaign_agent.initialize_mcp_connection()
        await self.action_agent.initialize_mcp_connection()
        
        state["current_step"] = "initialized"
        state["iteration_count"] = 0
        state["should_continue"] = True
        state["tool_calls"] = []
        state["errors"] = []
        state["intent_analysis"] = {}
        state["action_results"] = {}
        
        return state
    
    async def _analyze_intent_node(self, state: WorkflowState) -> WorkflowState:
        """Analyze user intent to determine workflow routing."""
        logger.info(f"🧠 Analyzing intent for workflow: {state['workflow_id']}")
        
        try:
            # Use action agent to analyze intent
            intent_analysis = await self.action_agent.analyze_user_intent(state["user_instruction"])
            
            state["intent_analysis"] = intent_analysis
            state["current_step"] = "intent_analyzed"
            
            logger.info(f"📋 Intent: {intent_analysis['intent_type']} (confidence: {intent_analysis['confidence']})")
            logger.info(f"🔧 DB Changes Required: {intent_analysis['requires_database_changes']}")
            
        except Exception as e:
            logger.error(f"❌ Intent analysis failed: {str(e)}")
            state["errors"].append(f"Intent analysis error: {str(e)}")
            # Fallback to analysis intent
            state["intent_analysis"] = {
                "intent_type": "analysis",
                "confidence": 0.5,
                "requires_database_changes": False,
                "reasoning": f"Fallback due to error: {str(e)}"
            }
        
        return state
    
    def _route_by_intent(self, state: WorkflowState) -> str:
        """Route workflow based on intent analysis."""
        intent_type = state["intent_analysis"].get("intent_type", "analysis")
        
        logger.info(f"🔀 Routing by intent: {intent_type}")
        
        if intent_type == "action":
            return "action"
        elif intent_type == "hybrid":
            return "hybrid"
        else:
            return "analysis"
    
    def _route_after_analysis(self, state: WorkflowState) -> str:
        """Route workflow after analysis based on intent and results."""
        intent_type = state["intent_analysis"].get("intent_type", "analysis")
        requires_db_changes = state["intent_analysis"].get("requires_database_changes", False)
        
        logger.info(f"🔀 Routing after analysis: intent={intent_type}, db_changes={requires_db_changes}")
        
        if intent_type == "hybrid" or requires_db_changes:
            return "action_needed"
        elif intent_type == "analysis":
            return "report"
        else:
            return "optimization"
    
    async def _monitor_campaigns_node(self, state: WorkflowState) -> WorkflowState:
        """Monitor campaign performance."""
        logger.info(f"📊 Monitoring campaigns for workflow: {state['workflow_id']}")
        
        try:
            # Use campaign agent to monitor campaigns
            result = await self.campaign_agent.execute_campaign_workflow(
                f"Monitor and analyze campaign performance. Context: {state.get('campaign_context', {})}"
            )
            
            state["monitoring_results"] = {
                "status": result["status"],
                "tool_calls": result["tool_calls"],
                "output": result["final_output"]
            }
            state["tool_calls"].extend(result["tool_calls"])
            state["current_step"] = "monitoring_completed"
            
        except Exception as e:
            logger.error(f"❌ Monitoring failed: {str(e)}")
            state["errors"].append(f"Monitoring error: {str(e)}")
            state["monitoring_results"] = {"status": "failed", "error": str(e)}
        
        return state
    
    async def _analyze_data_node(self, state: WorkflowState) -> WorkflowState:
        """Analyze campaign data."""
        logger.info(f"🔍 Analyzing data for workflow: {state['workflow_id']}")
        
        try:
            # Use campaign agent for analysis
            analysis_prompt = f"""
            Analyze the campaign monitoring results and provide insights.
            Monitoring Results: {state.get('monitoring_results', {})}
            User Instruction: {state['user_instruction']}
            Intent: {state['intent_analysis']['intent_type']}
            """
            
            result = await self.campaign_agent.execute_campaign_workflow(analysis_prompt)
            
            state["analysis_results"] = {
                "status": result["status"],
                "tool_calls": result["tool_calls"],
                "output": result["final_output"]
            }
            state["tool_calls"].extend(result["tool_calls"])
            state["current_step"] = "analysis_completed"
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {str(e)}")
            state["errors"].append(f"Analysis error: {str(e)}")
            state["analysis_results"] = {"status": "failed", "error": str(e)}
        
        return state
    
    async def _execute_actions_node(self, state: WorkflowState) -> WorkflowState:
        """Execute campaign actions using the Action Agent."""
        logger.info(f"🎯 Executing actions for workflow: {state['workflow_id']}")
        
        try:
            # Prepare context for action execution
            action_context = {
                "monitoring_results": state.get("monitoring_results", {}),
                "analysis_results": state.get("analysis_results", {}),
                "campaign_context": state.get("campaign_context", {})
            }
            
            # Use action agent to execute the workflow
            result = await self.action_agent.execute_action_workflow(
                state["user_instruction"],
                state["intent_analysis"],
                action_context
            )
            
            state["action_results"] = result
            state["tool_calls"].extend(result.get("tool_calls", []))
            state["current_step"] = "actions_completed"
            
            logger.info(f"✅ Actions executed: {result.get('database_changes_made', False)} DB changes made")
            
        except Exception as e:
            logger.error(f"❌ Action execution failed: {str(e)}")
            state["errors"].append(f"Action execution error: {str(e)}")
            state["action_results"] = {"status": "failed", "error": str(e)}
        
        return state
    
    async def _optimize_campaigns_node(self, state: WorkflowState) -> WorkflowState:
        """Optimize campaign strategies."""
        logger.info(f"🎯 Optimizing campaigns for workflow: {state['workflow_id']}")
        
        try:
            # Use campaign agent for optimization
            optimization_prompt = f"""
            Optimize campaigns based on analysis results.
            Analysis Results: {state.get('analysis_results', {})}
            Monitoring Results: {state.get('monitoring_results', {})}
            User Instruction: {state['user_instruction']}
            """
            
            result = await self.campaign_agent.execute_campaign_workflow(optimization_prompt)
            
            state["optimization_results"] = {
                "status": result["status"],
                "tool_calls": result["tool_calls"],
                "output": result["final_output"]
            }
            state["tool_calls"].extend(result["tool_calls"])
            state["current_step"] = "optimization_completed"
            
        except Exception as e:
            logger.error(f"❌ Optimization failed: {str(e)}")
            state["errors"].append(f"Optimization error: {str(e)}")
            state["optimization_results"] = {"status": "failed", "error": str(e)}
        
        return state
    
    async def _generate_report_node(self, state: WorkflowState) -> WorkflowState:
        """Generate comprehensive report."""
        logger.info(f"📋 Generating report for workflow: {state['workflow_id']}")
        
        try:
            # Determine which agent to use for reporting
            intent_type = state["intent_analysis"].get("intent_type", "analysis")
            
            if intent_type == "action" or state.get("action_results", {}).get("success"):
                # Use action agent for action-focused reports
                report_prompt = f"""
                Generate a comprehensive report of the actions taken and their results.
                User Instruction: {state['user_instruction']}
                Intent Analysis: {state['intent_analysis']}
                Action Results: {state.get('action_results', {})}
                Analysis Results: {state.get('analysis_results', {})}
                Monitoring Results: {state.get('monitoring_results', {})}
                """
                
                result = await self.action_agent.execute_action_workflow(
                    report_prompt,
                    {"intent_type": "analysis", "confidence": 1.0},
                    state
                )
                final_output = result.get("output", "Report generation completed")
                
            else:
                # Use campaign agent for analysis-focused reports
                report_prompt = f"""
                Generate a comprehensive campaign optimization report.
                Monitoring: {state.get('monitoring_results', {})}
                Analysis: {state.get('analysis_results', {})}
                Optimization: {state.get('optimization_results', {})}
                User Instruction: {state['user_instruction']}
                """
                
                result = await self.campaign_agent.execute_campaign_workflow(report_prompt)
                final_output = result["final_output"]
            
            state["reporting_results"] = {
                "status": "completed",
                "output": final_output
            }
            state["final_output"] = final_output
            state["current_step"] = "reporting_completed"
            
        except Exception as e:
            logger.error(f"❌ Reporting failed: {str(e)}")
            state["errors"].append(f"Reporting error: {str(e)}")
            state["reporting_results"] = {"status": "failed", "error": str(e)}
            state["final_output"] = f"Report generation failed: {str(e)}"
        
        return state
    
    async def _validate_output_node(self, state: WorkflowState) -> WorkflowState:
        """Validate the final output."""
        logger.info(f"🛡️ Validating output for workflow: {state['workflow_id']}")
        
        try:
            # Validate using hallucination grader
            validation_result = self.hallucination_grader.grade_output(
                state["final_output"],
                context=state["user_instruction"],
                source_data=json.dumps({
                    "intent": state.get("intent_analysis", {}),
                    "monitoring": state.get("monitoring_results", {}),
                    "analysis": state.get("analysis_results", {}),
                    "actions": state.get("action_results", {}),
                    "optimization": state.get("optimization_results", {})
                })
            )
            
            # Check enforcer limits
            enforcer_result = self.enforcer_agent.should_continue(
                state["workflow_id"],
                operation="workflow_validation"
            )
            
            state["validation_results"] = {
                "is_valid": not validation_result["is_hallucination"],
                "confidence": validation_result["confidence"],
                "enforcer_continue": enforcer_result["should_continue"]
            }
            
            state["iteration_count"] += 1
            state["should_continue"] = (
                validation_result["is_hallucination"] and 
                enforcer_result["should_continue"] and 
                state["iteration_count"] < 3
            )
            
            if not state["should_continue"]:
                state["status"] = "completed"
                state["completed_at"] = datetime.now().isoformat()
                state["current_step"] = "completed"
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {str(e)}")
            state["errors"].append(f"Validation error: {str(e)}")
            state["should_continue"] = False
            state["status"] = "failed"
        
        return state
    
    def _should_continue(self, state: WorkflowState) -> str:
        """Determine if workflow should continue or end."""
        if state.get("should_continue", False):
            logger.info(f"🔄 Continuing workflow: {state['workflow_id']} (iteration {state['iteration_count']})")
            return "continue"
        else:
            logger.info(f"✅ Ending workflow: {state['workflow_id']}")
            return "end"
    
    async def run_workflow(self, 
                          user_instruction: str,
                          campaign_context: Optional[Dict[str, Any]] = None) -> WorkflowState:
        """
        Run the complete enhanced campaign optimization workflow.
        
        Args:
            user_instruction: Natural language instruction from user
            campaign_context: Optional context about campaigns
            
        Returns:
            Complete workflow state with results
        """
        workflow_id = f"workflow_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now()
        
        logger.info(f"🚀 Starting Enhanced Campaign Workflow: {workflow_id}")
        logger.info(f"📝 Instruction: {user_instruction}")
        
        # Initialize workflow state
        initial_state = WorkflowState(
            workflow_id=workflow_id,
            current_step="initializing",
            user_instruction=user_instruction,
            campaign_context=campaign_context,
            intent_analysis={},
            monitoring_results={},
            analysis_results={},
            optimization_results={},
            action_results={},
            reporting_results={},
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
            
            logger.info(f"✅ Enhanced Workflow {workflow_id} completed in {execution_time:.2f}s")
            logger.info(f"📊 Total tool calls: {len(final_state['tool_calls'])}")
            logger.info(f"🎯 Intent: {final_state['intent_analysis'].get('intent_type', 'unknown')}")
            logger.info(f"🔧 DB Changes: {final_state.get('action_results', {}).get('database_changes_made', False)}")
            
            return final_state
            
        except Exception as e:
            logger.error(f"❌ Enhanced Workflow {workflow_id} failed: {str(e)}")
            initial_state["status"] = "failed"
            initial_state["errors"].append(f"Workflow execution failed: {str(e)}")
            initial_state["completed_at"] = datetime.now().isoformat()
            return initial_state
    
    def visualize_graph(self, output_path: str = "enhanced_campaign_workflow_graph.png"):
        """
        Generate a visual representation of the enhanced workflow graph.
        
        Args:
            output_path: Path to save the PNG image
        """
        try:
            # Get the graph visualization
            graph_image = self.graph.get_graph().draw_mermaid_png()
            
            # Save to file
            with open(output_path, "wb") as f:
                f.write(graph_image)
            
            logger.info(f"📊 Enhanced Graph visualization saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Failed to generate graph visualization: {str(e)}")
            return None

# Factory function for easy instantiation
def create_campaign_graph(model: str = "gpt-4o-mini", temperature: float = 0.3) -> CampaignOptimizationGraph:
    """Create a new enhanced campaign optimization graph."""
    return CampaignOptimizationGraph(model=model, temperature=temperature) 