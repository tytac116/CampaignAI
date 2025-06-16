"""
Campaign AI Agents Module

This module contains all MCP-integrated agents for campaign optimization.
All agents use the Model Context Protocol (MCP) for tool interactions.
"""

# Import MCP-integrated components (clean names since everything is MCP-integrated)
from .campaign_agent import CampaignAgent, get_campaign_agent
from .coordinator import CoordinatorAgent, create_coordinator
from .workflow_graph import CampaignOptimizationGraph, create_campaign_graph, WorkflowState
from .workflow_nodes import (
    CampaignMonitorNode,
    DataAnalysisNode, 
    OptimizationNode,
    ReportingNode
)

# Import validation and state management
from .validation import (
    HallucinationGrader,
    EnforcerAgent,
    get_hallucination_grader,
    get_enforcer_agent
)
from .state import (
    CampaignOptimizationState,
    WorkflowStatus,
    Priority
)

__all__ = [
    # Main agents
    "CampaignAgent",
    "CoordinatorAgent", 
    "CampaignOptimizationGraph",
    
    # Factory functions
    "get_campaign_agent",
    "create_coordinator",
    "create_campaign_graph",
    
    # Workflow nodes
    "CampaignMonitorNode",
    "DataAnalysisNode",
    "OptimizationNode", 
    "ReportingNode",
    
    # Validation
    "HallucinationGrader",
    "EnforcerAgent",
    "get_hallucination_grader",
    "get_enforcer_agent",
    
    # State management
    "CampaignOptimizationState",
    "WorkflowState",
    "WorkflowStatus",
    "Priority"
] 