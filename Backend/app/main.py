"""
Campaign AI Application

FastAPI application that provides MCP-integrated campaign optimization services.
All agents use the Model Context Protocol (MCP) for tool interactions.
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

# Add Backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agents import (
    CampaignAgent,
    CoordinatorAgent,
    CampaignOptimizationGraph,
    get_campaign_agent,
    create_coordinator,
    create_campaign_graph
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Campaign AI Application",
    description="MCP-integrated campaign optimization platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
campaign_agent = None
coordinator_agent = None
workflow_graph = None

# Request/Response models
class OptimizationRequest(BaseModel):
    instruction: str
    campaign_context: Optional[Dict[str, Any]] = None

class WorkflowRequest(BaseModel):
    campaign_ids: List[int]
    trigger_reason: str = "api_request"
    priority: str = "MEDIUM"
    user_context: Optional[Dict[str, Any]] = None

class OptimizationResponse(BaseModel):
    agent_id: str
    workflow_id: str
    status: str
    final_output: str
    tool_calls: List[Dict[str, Any]]
    validation_results: Dict[str, Any]
    execution_time_seconds: float

class WorkflowResponse(BaseModel):
    workflow_id: str
    coordinator_id: str
    status: str
    phases_completed: List[str]
    tool_calls: List[Dict[str, Any]]
    results: Dict[str, Any]
    execution_time_seconds: float

@app.on_event("startup")
async def startup_event():
    """Initialize MCP-integrated components on startup."""
    global campaign_agent, coordinator_agent, workflow_graph
    
    logger.info("🚀 Starting Campaign AI Application...")
    
    try:
        # Initialize campaign agent
        campaign_agent = get_campaign_agent()
        await campaign_agent.initialize_mcp_connection()
        logger.info("✅ Campaign Agent initialized")
        
        # Initialize coordinator
        coordinator_agent = create_coordinator()
        await coordinator_agent.initialize_mcp_connection()
        logger.info("✅ Coordinator Agent initialized")
        
        # Initialize workflow graph
        workflow_graph = create_campaign_graph()
        logger.info("✅ Workflow Graph initialized")
        
        logger.info("🎉 Campaign AI Application ready!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise

@app.get("/")
async def root():
    """Root endpoint with application info."""
    return {
        "name": "Campaign AI Application",
        "version": "1.0.0",
        "description": "MCP-integrated campaign optimization platform",
        "status": "running",
        "endpoints": {
            "optimize": "/optimize",
            "workflow": "/workflow",
            "workflow_status": "/workflow/{workflow_id}",
            "health": "/health",
            "tools": "/tools"
        }
    }

@app.post("/optimize", response_model=OptimizationResponse)
async def optimize_campaigns(request: OptimizationRequest):
    """
    Execute campaign optimization using the Campaign Agent.
    
    This endpoint uses the MCP-integrated Campaign Agent to analyze and optimize
    campaigns based on natural language instructions.
    """
    try:
        logger.info(f"📝 Optimization request: {request.instruction}")
        
        # Execute optimization
        result = await campaign_agent.execute_campaign_optimization(
            instruction=request.instruction,
            campaign_context=request.campaign_context
        )
        
        return OptimizationResponse(
            agent_id=result["agent_id"],
            workflow_id=result["workflow_id"],
            status=result["status"],
            final_output=result["final_output"],
            tool_calls=result["tool_calls"],
            validation_results=result["validation_results"],
            execution_time_seconds=result["execution_time_seconds"]
        )
        
    except Exception as e:
        logger.error(f"❌ Optimization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflow", response_model=WorkflowResponse)
async def execute_workflow(request: WorkflowRequest):
    """
    Execute complete campaign optimization workflow using the Coordinator.
    
    This endpoint orchestrates a multi-phase workflow including monitoring,
    analysis, optimization, and reporting using MCP tools.
    """
    try:
        logger.info(f"🔄 Workflow request for campaigns: {request.campaign_ids}")
        
        # Convert priority string to enum
        from app.agents.state import Priority
        priority = Priority[request.priority.upper()]
        
        # Execute workflow
        result = await coordinator_agent.coordinate_campaign_optimization(
            campaign_ids=request.campaign_ids,
            trigger_reason=request.trigger_reason,
            priority=priority,
            user_context=request.user_context
        )
        
        return WorkflowResponse(
            workflow_id=result["workflow_id"],
            coordinator_id=result["coordinator_id"],
            status=result["status"],
            phases_completed=result["phases_completed"],
            tool_calls=result["tool_calls"],
            results=result["results"],
            execution_time_seconds=result["execution_time_seconds"]
        )
        
    except Exception as e:
        logger.error(f"❌ Workflow failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflow/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Get the status of a specific workflow."""
    try:
        status = await coordinator_agent.get_workflow_status(workflow_id)
        
        if status is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test MCP connections
        agent_health = await campaign_agent.test_mcp_connection() if campaign_agent else False
        coordinator_health = await coordinator_agent.initialize_mcp_connection() if coordinator_agent else False
        
        return {
            "status": "healthy" if (agent_health and coordinator_health) else "degraded",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "campaign_agent": "healthy" if agent_health else "unhealthy",
                "coordinator_agent": "healthy" if coordinator_health else "unhealthy",
                "workflow_graph": "healthy" if workflow_graph else "unhealthy"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.get("/tools")
async def list_available_tools():
    """List all available MCP tools."""
    try:
        if not campaign_agent or not campaign_agent.mcp_tools:
            await campaign_agent.initialize_mcp_connection()
        
        tools_info = []
        for tool in campaign_agent.mcp_tools:
            tools_info.append({
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.args_schema.schema() if hasattr(tool, 'args_schema') else {}
            })
        
        return {
            "total_tools": len(tools_info),
            "tools": tools_info,
            "categories": {
                "llm_tools": [t for t in tools_info if "analyze" in t["name"] or "generate" in t["name"] or "optimize" in t["name"] or "assistant" in t["name"]],
                "api_tools": [t for t in tools_info if "facebook" in t["name"] or "instagram" in t["name"]],
                "search_tools": [t for t in tools_info if "search" in t["name"] or "tavily" in t["name"] or "wikipedia" in t["name"]],
                "validation_tools": [t for t in tools_info if "grade" in t["name"] or "enforce" in t["name"]]
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to list tools: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 