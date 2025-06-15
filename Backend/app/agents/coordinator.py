"""
Coordinator Agent for Campaign Optimization Platform

This agent orchestrates the entire workflow and manages communication between other agents.
It decides when to trigger different agents based on campaign performance and schedules.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import logging
from dataclasses import dataclass

from ..models.campaign import Campaign, CampaignStatus
from ..models.agent_execution import AgentExecution, AgentType, ExecutionStatus
from ..core.database import get_session
from .state import CampaignOptimizationState, WorkflowStatus, Priority
from .nodes import (
    CampaignMonitorNode,
    DataAnalysisNode, 
    OptimizationNode,
    ReportingNode
)

logger = logging.getLogger(__name__)

@dataclass  
class WorkflowTask:
    """Represents a workflow task for the coordinator"""
    campaign_id: str
    agent_type: AgentType
    priority: Priority
    scheduled_at: datetime
    data: Dict[str, Any]
    retry_count: int = 0
    max_retries: int = 3

class CoordinatorAgent:
    """
    Coordinator Agent that orchestrates the campaign optimization workflow.
    
    This agent:
    - Monitors campaign schedules and triggers appropriate agents
    - Manages workflow state and execution order
    - Handles error recovery and retries
    - Coordinates communication between agents
    - Manages workflow priorities and resource allocation
    """
    
    def __init__(self):
        self.monitor_node = CampaignMonitorNode()
        self.analysis_node = DataAnalysisNode()
        self.optimization_node = OptimizationNode()
        self.reporting_node = ReportingNode()
        
        # Task queue for managing workflow execution
        self.task_queue: List[WorkflowTask] = []
        self.active_workflows: Dict[str, CampaignOptimizationState] = {}
        
    async def start_campaign_optimization_workflow(
        self, 
        campaign_id: str, 
        trigger_reason: str = "scheduled",
        priority: Priority = Priority.MEDIUM
    ) -> str:
        """
        Start a complete campaign optimization workflow
        
        Args:
            campaign_id: ID of the campaign to optimize
            trigger_reason: Reason for triggering the workflow
            priority: Workflow priority level
            
        Returns:
            workflow_id: Unique identifier for this workflow execution
        """
        workflow_id = f"workflow_{campaign_id}_{datetime.utcnow().timestamp()}"
        
        # Initialize workflow state
        state = CampaignOptimizationState(
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
            metadata={}
        )
        
        self.active_workflows[workflow_id] = state
        
        logger.info(f"Starting campaign optimization workflow {workflow_id} for campaign {campaign_id}")
        
        try:
            # Execute the workflow steps in sequence
            await self._execute_workflow(state)
            
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {str(e)}")
            state["status"] = WorkflowStatus.FAILED
            state["error_message"] = str(e)
            state["completed_at"] = datetime.utcnow()
            
        return workflow_id
    
    async def _execute_workflow(self, state: CampaignOptimizationState):
        """Execute the complete workflow pipeline"""
        
        try:
            # Step 1: Campaign Monitoring and Alert Detection
            state["current_step"] = "monitoring"
            state["progress"] = 0.2
            logger.info(f"Workflow {state['workflow_id']}: Starting campaign monitoring")
            
            monitor_result = await self.monitor_node.execute(state)
            state.update(monitor_result)
            
            # Step 2: Data Analysis
            state["current_step"] = "analysis" 
            state["progress"] = 0.4
            logger.info(f"Workflow {state['workflow_id']}: Starting data analysis")
            
            analysis_result = await self.analysis_node.execute(state)
            state.update(analysis_result)
            
            # Step 3: Optimization Recommendations
            state["current_step"] = "optimization"
            state["progress"] = 0.6
            logger.info(f"Workflow {state['workflow_id']}: Generating optimization recommendations")
            
            optimization_result = await self.optimization_node.execute(state)
            state.update(optimization_result)
            
            # Step 4: Report Generation
            state["current_step"] = "reporting"
            state["progress"] = 0.8
            logger.info(f"Workflow {state['workflow_id']}: Generating reports")
            
            reporting_result = await self.reporting_node.execute(state)
            state.update(reporting_result)
            
            # Step 5: Workflow Completion
            state["current_step"] = "completed"
            state["progress"] = 1.0
            state["status"] = WorkflowStatus.COMPLETED
            state["completed_at"] = datetime.utcnow()
            
            logger.info(f"Workflow {state['workflow_id']} completed successfully")
            
            # Clean up completed workflow
            await self._cleanup_workflow(state["workflow_id"])
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            state["status"] = WorkflowStatus.FAILED
            state["error_message"] = str(e)
            state["completed_at"] = datetime.utcnow()
            raise
    
    async def schedule_campaign_monitoring(self, campaign_ids: List[str]):
        """
        Schedule monitoring tasks for multiple campaigns
        
        Args:
            campaign_ids: List of campaign IDs to monitor
        """
        current_time = datetime.utcnow()
        
        for campaign_id in campaign_ids:
            # Check if campaign needs monitoring
            async with get_session() as session:
                campaign = await session.get(Campaign, campaign_id)
                
                if not campaign or campaign.status != CampaignStatus.ACTIVE:
                    continue
                
                # Determine monitoring priority based on campaign performance
                priority = await self._determine_campaign_priority(campaign)
                
                # Schedule monitoring task
                task = WorkflowTask(
                    campaign_id=campaign_id,
                    agent_type=AgentType.CAMPAIGN_MONITOR,
                    priority=priority,
                    scheduled_at=current_time,
                    data={"trigger_reason": "scheduled_monitoring"}
                )
                
                self.task_queue.append(task)
        
        # Sort tasks by priority and scheduled time
        self.task_queue.sort(key=lambda x: (x.priority.value, x.scheduled_at))
        
        logger.info(f"Scheduled monitoring for {len(campaign_ids)} campaigns")
    
    async def _determine_campaign_priority(self, campaign: Campaign) -> Priority:
        """Determine the priority level for a campaign based on its performance"""
        
        # High priority conditions
        if (campaign.daily_spend and campaign.budget and 
            campaign.daily_spend > campaign.budget * 0.8):
            return Priority.HIGH
            
        if campaign.ctr and campaign.ctr < 0.01:  # Very low CTR
            return Priority.HIGH
            
        if campaign.roas and campaign.roas < 1.0:  # Negative ROAS
            return Priority.HIGH
        
        # Medium priority conditions  
        if campaign.cpc and campaign.cpc > 5.0:  # High CPC
            return Priority.MEDIUM
            
        if campaign.ctr and campaign.ctr < 0.02:  # Low CTR
            return Priority.MEDIUM
            
        # Default to low priority
        return Priority.LOW
    
    async def process_task_queue(self):
        """Process pending tasks in the task queue"""
        
        while self.task_queue:
            task = self.task_queue.pop(0)
            
            try:
                if task.agent_type == AgentType.CAMPAIGN_MONITOR:
                    await self.start_campaign_optimization_workflow(
                        task.campaign_id,
                        task.data.get("trigger_reason", "scheduled"),
                        task.priority
                    )
                    
            except Exception as e:
                logger.error(f"Task execution failed for campaign {task.campaign_id}: {str(e)}")
                
                # Retry logic
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    task.scheduled_at = datetime.utcnow() + timedelta(minutes=5 * task.retry_count)
                    self.task_queue.append(task)
                    logger.info(f"Retrying task for campaign {task.campaign_id} (attempt {task.retry_count})")
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[CampaignOptimizationState]:
        """Get the current status of a workflow"""
        return self.active_workflows.get(workflow_id)
    
    async def get_active_workflows(self) -> Dict[str, CampaignOptimizationState]:
        """Get all currently active workflows"""
        return self.active_workflows.copy()
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel an active workflow"""
        if workflow_id in self.active_workflows:
            state = self.active_workflows[workflow_id]
            state["status"] = WorkflowStatus.CANCELLED
            state["completed_at"] = datetime.utcnow()
            
            await self._cleanup_workflow(workflow_id)
            logger.info(f"Cancelled workflow {workflow_id}")
            return True
        
        return False
    
    async def _cleanup_workflow(self, workflow_id: str):
        """Clean up completed workflow from active workflows"""
        if workflow_id in self.active_workflows:
            del self.active_workflows[workflow_id]
    
    async def get_workflow_metrics(self) -> Dict[str, Any]:
        """Get metrics about workflow execution"""
        active_count = len(self.active_workflows)
        
        status_counts = {}
        priority_counts = {}
        
        for state in self.active_workflows.values():
            status = state["status"]
            priority = state["priority"]
            
            status_counts[status.value] = status_counts.get(status.value, 0) + 1
            priority_counts[priority.value] = priority_counts.get(priority.value, 0) + 1
        
        return {
            "active_workflows": active_count,
            "queued_tasks": len(self.task_queue),
            "status_distribution": status_counts,
            "priority_distribution": priority_counts,
            "last_updated": datetime.utcnow().isoformat()
        }

# Global coordinator instance
coordinator = CoordinatorAgent() 