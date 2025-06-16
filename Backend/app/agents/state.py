from typing import TypedDict, List, Dict, Any, Optional, Annotated
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

from langchain_core.messages import BaseMessage


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Priority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CampaignData:
    """Campaign data structure."""
    id: int
    name: str
    platform: str
    status: str
    budget: float
    spend: float
    impressions: int
    clicks: int
    conversions: int
    cpm: float
    cpc: float
    ctr: float
    conversion_rate: float
    roas: float


@dataclass
class AlertData:
    """Alert/anomaly data structure."""
    campaign_id: int
    alert_type: str  # "performance_drop", "budget_overrun", "anomaly"
    severity: Priority
    message: str
    suggested_action: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


@dataclass
class OptimizationRecommendation:
    """Optimization recommendation structure."""
    campaign_id: int
    recommendation_type: str  # "budget", "targeting", "creative", "bidding"
    title: str
    description: str
    expected_impact: str
    confidence_score: float
    implementation_steps: List[str]
    estimated_results: Dict[str, Any]


@dataclass
class ReportData:
    """Report data structure."""
    report_type: str  # "performance", "insights", "recommendations"
    period: str
    summary: str
    key_metrics: Dict[str, Any]
    insights: List[str]
    recommendations: List[OptimizationRecommendation]
    charts_data: Optional[Dict[str, Any]] = None


class CampaignOptimizationState(TypedDict):
    """
    State for the campaign optimization workflow.
    This represents the shared state across all agents in the LangGraph.
    """
    
    # Workflow metadata
    workflow_id: str
    status: WorkflowStatus
    created_at: datetime
    updated_at: datetime
    priority: Priority
    
    # Input parameters
    campaign_ids: List[int]
    requested_analysis: List[str]  # Types of analysis requested
    user_preferences: Dict[str, Any]
    
    # Campaign data
    campaigns: List[CampaignData]
    campaign_metrics: Dict[int, Dict[str, Any]]  # campaign_id -> metrics
    
    # Analysis results
    performance_analysis: Dict[str, Any]
    anomaly_detection: Dict[str, Any]
    trend_analysis: Dict[str, Any]
    audience_insights: Dict[str, Any]
    
    # Alerts and notifications
    alerts: List[AlertData]
    notifications: List[Dict[str, Any]]
    
    # Optimization recommendations
    recommendations: List[OptimizationRecommendation]
    optimization_results: Dict[str, Any]
    
    # Reporting
    reports: List[ReportData]
    
    # Agent execution tracking
    completed_agents: List[str]
    agent_outputs: Dict[str, Any]  # agent_name -> output
    
    # Messages and logs
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]
    execution_log: List[str]
    
    # Error handling
    errors: List[Dict[str, Any]]
    retry_count: int
    
    # External API data
    facebook_api_data: Optional[Dict[str, Any]]
    instagram_api_data: Optional[Dict[str, Any]]


def create_initial_state(
    workflow_id: str,
    campaign_ids: List[int],
    requested_analysis: List[str],
    user_preferences: Optional[Dict[str, Any]] = None,
    priority: Priority = Priority.MEDIUM
) -> CampaignOptimizationState:
    """Create initial state for a new workflow."""
    now = datetime.utcnow()
    
    return CampaignOptimizationState(
        # Workflow metadata
        workflow_id=workflow_id,
        status=WorkflowStatus.PENDING,
        created_at=now,
        updated_at=now,
        priority=priority,
        
        # Input parameters
        campaign_ids=campaign_ids,
        requested_analysis=requested_analysis,
        user_preferences=user_preferences or {},
        
        # Campaign data
        campaigns=[],
        campaign_metrics={},
        
        # Analysis results
        performance_analysis={},
        anomaly_detection={},
        trend_analysis={},
        audience_insights={},
        
        # Alerts and notifications
        alerts=[],
        notifications=[],
        
        # Optimization recommendations
        recommendations=[],
        optimization_results={},
        
        # Reporting
        reports=[],
        
        # Agent execution tracking
        completed_agents=[],
        agent_outputs={},
        
        # Messages and logs
        messages=[],
        execution_log=[],
        
        # Error handling
        errors=[],
        retry_count=0,
        
        # External API data
        facebook_api_data=None,
        instagram_api_data=None,
    ) 