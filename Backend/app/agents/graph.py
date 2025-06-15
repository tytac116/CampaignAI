"""
LangGraph Orchestration for Campaign Optimization Platform

This module defines the workflow graph using LangGraph for campaign optimization.
It creates a state machine that coordinates the execution of different agents.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import CampaignOptimizationState, WorkflowStatus, Priority
from .nodes import (
    CampaignMonitorNode,
    DataAnalysisNode,
    OptimizationNode, 
    ReportingNode
)
from .coordinator import CoordinatorAgent

logger = logging.getLogger(__name__)

class CampaignOptimizationGraph:
    """
    LangGraph-based workflow orchestration for campaign optimization.
    
    This class creates and manages the state graph that defines the flow
    of execution between different optimization agents.
    """
    
    def __init__(self):
        self.monitor_node = CampaignMonitorNode()
        self.analysis_node = DataAnalysisNode()
        self.optimization_node = OptimizationNode()
        self.reporting_node = ReportingNode()
        self.coordinator = CoordinatorAgent()
        
        # Initialize the graph
        self.graph = self._create_graph()
        self.checkpointer = MemorySaver()
        
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph state graph for campaign optimization"""
        
        # Create the graph with our state schema
        workflow = StateGraph(CampaignOptimizationState)
        
        # Add nodes to the graph
        workflow.add_node("campaign_monitor", self._monitor_wrapper)
        workflow.add_node("data_analysis", self._analysis_wrapper) 
        workflow.add_node("optimization", self._optimization_wrapper)
        workflow.add_node("reporting", self._reporting_wrapper)
        workflow.add_node("coordinator_check", self._coordinator_check_wrapper)
        
        # Define the entry point
        workflow.set_entry_point("campaign_monitor")
        
        # Define the edges (workflow transitions)
        workflow.add_edge("campaign_monitor", "coordinator_check")
        workflow.add_conditional_edges(
            "coordinator_check",
            self._should_continue_analysis,
            {
                "continue": "data_analysis",
                "skip": "reporting"
            }
        )
        workflow.add_edge("data_analysis", "optimization")
        workflow.add_edge("optimization", "reporting")
        workflow.add_edge("reporting", END)
        
        return workflow
    
    async def _monitor_wrapper(self, state: CampaignOptimizationState) -> CampaignOptimizationState:
        """Wrapper for campaign monitoring node"""
        logger.info(f"Executing campaign monitoring for workflow {state['workflow_id']}")
        
        try:
            state["current_step"] = "monitoring"
            state["progress"] = 0.2
            state["status"] = WorkflowStatus.RUNNING
            
            result = await self.monitor_node.execute(state)
            state.update(result)
            
            logger.info(f"Campaign monitoring completed for workflow {state['workflow_id']}")
            
        except Exception as e:
            logger.error(f"Campaign monitoring failed: {str(e)}")
            state["status"] = WorkflowStatus.FAILED
            state["error_message"] = str(e)
            
        return state
    
    async def _analysis_wrapper(self, state: CampaignOptimizationState) -> CampaignOptimizationState:
        """Wrapper for data analysis node"""
        logger.info(f"Executing data analysis for workflow {state['workflow_id']}")
        
        try:
            state["current_step"] = "analysis"
            state["progress"] = 0.4
            
            result = await self.analysis_node.execute(state)
            state.update(result)
            
            logger.info(f"Data analysis completed for workflow {state['workflow_id']}")
            
        except Exception as e:
            logger.error(f"Data analysis failed: {str(e)}")
            state["status"] = WorkflowStatus.FAILED
            state["error_message"] = str(e)
            
        return state
    
    async def _optimization_wrapper(self, state: CampaignOptimizationState) -> CampaignOptimizationState:
        """Wrapper for optimization node"""
        logger.info(f"Executing optimization for workflow {state['workflow_id']}")
        
        try:
            state["current_step"] = "optimization"
            state["progress"] = 0.6
            
            result = await self.optimization_node.execute(state)
            state.update(result)
            
            logger.info(f"Optimization completed for workflow {state['workflow_id']}")
            
        except Exception as e:
            logger.error(f"Optimization failed: {str(e)}")
            state["status"] = WorkflowStatus.FAILED
            state["error_message"] = str(e)
            
        return state
    
    async def _reporting_wrapper(self, state: CampaignOptimizationState) -> CampaignOptimizationState:
        """Wrapper for reporting node"""
        logger.info(f"Executing reporting for workflow {state['workflow_id']}")
        
        try:
            state["current_step"] = "reporting"
            state["progress"] = 0.8
            
            result = await self.reporting_node.execute(state)
            state.update(result)
            
            # Mark workflow as completed
            state["current_step"] = "completed"
            state["progress"] = 1.0
            state["status"] = WorkflowStatus.COMPLETED
            state["completed_at"] = datetime.utcnow()
            
            logger.info(f"Reporting completed for workflow {state['workflow_id']}")
            
        except Exception as e:
            logger.error(f"Reporting failed: {str(e)}")
            state["status"] = WorkflowStatus.FAILED
            state["error_message"] = str(e)
            
        return state
    
    async def _coordinator_check_wrapper(self, state: CampaignOptimizationState) -> CampaignOptimizationState:
        """Wrapper for coordinator decision making"""
        logger.info(f"Coordinator check for workflow {state['workflow_id']}")
        
        # The coordinator can modify the state or add metadata
        # This is where business logic for workflow routing can be implemented
        state["metadata"]["coordinator_decision"] = "continue_normal_flow"
        
        return state
    
    def _should_continue_analysis(self, state: CampaignOptimizationState) -> str:
        """
        Conditional logic to determine if we should continue with full analysis
        or skip to reporting for simple cases
        """
        
        # Skip full analysis if no alerts were generated
        if not state.get("alerts"):
            logger.info(f"No alerts found for workflow {state['workflow_id']}, skipping to reporting")
            return "skip"
        
        # Continue with full analysis if we have high priority alerts
        high_priority_alerts = [alert for alert in state.get("alerts", []) 
                              if alert.priority == Priority.HIGH]
        
        if high_priority_alerts:
            logger.info(f"High priority alerts found for workflow {state['workflow_id']}, continuing analysis")
            return "continue"
        
        # Default to continuing analysis
        return "continue"
    
    async def run_workflow(
        self, 
        campaign_id: str, 
        trigger_reason: str = "api_request",
        priority: Priority = Priority.MEDIUM,
        config: Optional[Dict[str, Any]] = None
    ) -> CampaignOptimizationState:
        """
        Run the complete campaign optimization workflow
        
        Args:
            campaign_id: ID of the campaign to optimize
            trigger_reason: Reason for triggering the workflow
            priority: Priority level of the workflow
            config: Optional configuration for the workflow
            
        Returns:
            Final state of the workflow execution
        """
        
        workflow_id = f"workflow_{campaign_id}_{datetime.utcnow().timestamp()}"
        
        # Initialize the workflow state
        initial_state = CampaignOptimizationState(
            workflow_id=workflow_id,
            campaign_id=campaign_id,
            status=WorkflowStatus.PENDING,
            priority=priority,
            started_at=datetime.utcnow(),
            trigger_reason=trigger_reason,
            current_step="initialization",
            progress=0.0,
            campaign_data=None,
            alerts=[],
            optimization_recommendations=[],
            report_data=None,
            metadata=config or {}
        )
        
        logger.info(f"Starting workflow {workflow_id} for campaign {campaign_id}")
        
        try:
            # Compile the graph with checkpointing
            app = self.graph.compile(checkpointer=self.checkpointer)
            
            # Run the workflow
            final_state = None
            thread_config = {"configurable": {"thread_id": workflow_id}}
            
            async for state in app.astream(initial_state, config=thread_config):
                final_state = state
                logger.debug(f"Workflow {workflow_id} step completed: {final_state.get('current_step')}")
            
            logger.info(f"Workflow {workflow_id} completed with status: {final_state['status']}")
            return final_state
            
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {str(e)}")
            
            error_state = initial_state.copy()
            error_state.update({
                "status": WorkflowStatus.FAILED,
                "error_message": str(e),
                "completed_at": datetime.utcnow()
            })
            
            return error_state
    
    async def get_workflow_state(self, workflow_id: str) -> Optional[CampaignOptimizationState]:
        """Get the current state of a workflow"""
        try:
            app = self.graph.compile(checkpointer=self.checkpointer)
            thread_config = {"configurable": {"thread_id": workflow_id}}
            
            # Get the latest state from the checkpointer
            state = await app.aget_state(thread_config)
            return state.values if state else None
            
        except Exception as e:
            logger.error(f"Failed to get workflow state for {workflow_id}: {str(e)}")
            return None
    
    async def resume_workflow(self, workflow_id: str) -> Optional[CampaignOptimizationState]:
        """Resume a paused or failed workflow"""
        try:
            current_state = await self.get_workflow_state(workflow_id)
            
            if not current_state:
                logger.error(f"Cannot resume workflow {workflow_id}: state not found")
                return None
            
            if current_state["status"] == WorkflowStatus.COMPLETED:
                logger.info(f"Workflow {workflow_id} is already completed")
                return current_state
            
            # Resume the workflow from its current state
            app = self.graph.compile(checkpointer=self.checkpointer)
            thread_config = {"configurable": {"thread_id": workflow_id}}
            
            final_state = None
            async for state in app.astream(None, config=thread_config):
                final_state = state
            
            logger.info(f"Resumed workflow {workflow_id} completed with status: {final_state['status']}")
            return final_state
            
        except Exception as e:
            logger.error(f"Failed to resume workflow {workflow_id}: {str(e)}")
            return None

# Global graph instance
campaign_optimization_graph = CampaignOptimizationGraph() 