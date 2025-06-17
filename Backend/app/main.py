"""
Campaign AI Application

FastAPI application that provides MCP-integrated campaign optimization services.
All agents use the Model Context Protocol (MCP) for tool interactions.
"""

import os
import sys
import asyncio
import logging
import subprocess
import threading
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

# Import direct database access
from app.services.supabase_service import supabase_service
from app.tools.campaign_action_tool import list_campaigns_by_criteria

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Campaign AI Application",
    description="MCP-integrated campaign optimization platform with direct data access",
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
mcp_server_process = None

# Request/Response models for MCP operations
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

# Direct data access models
class CampaignData(BaseModel):
    campaign_id: str
    name: str
    platform: str
    status: str
    objective: str
    budget_amount: float
    spend_amount: float
    remaining_budget: float
    impressions: int
    clicks: int
    conversions: int
    revenue: float
    ctr: float
    cpc: float
    cpm: float
    cpa: float
    roas: float
    start_date: str
    end_date: Optional[str]
    created_at: str
    updated_at: str

class DashboardStats(BaseModel):
    total_campaigns: int
    active_campaigns: int
    total_spend: float
    total_revenue: float
    average_roas: float
    average_ctr: float
    average_cpc: float
    total_clicks: int
    total_impressions: int
    total_conversions: int

def start_mcp_server():
    """Start the MCP server in a separate process."""
    global mcp_server_process
    try:
        mcp_server_path = os.path.join(backend_dir, "mcp_server.py")
        logger.info(f"🚀 Starting MCP server: {mcp_server_path}")
        
        mcp_server_process = subprocess.Popen(
            [sys.executable, mcp_server_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give the server a moment to start
        asyncio.sleep(2)
        logger.info("✅ MCP server started successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to start MCP server: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize MCP-integrated components and start MCP server on startup."""
    global campaign_agent, coordinator_agent, workflow_graph
    
    logger.info("🚀 Starting Campaign AI Application...")
    
    try:
        # Start MCP server first
        await asyncio.get_event_loop().run_in_executor(None, start_mcp_server)
        
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

@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown of MCP server."""
    global mcp_server_process
    if mcp_server_process:
        logger.info("🛑 Shutting down MCP server...")
        mcp_server_process.terminate()
        mcp_server_process.wait()
        logger.info("✅ MCP server shut down")

# =============================================================================
# DIRECT DATA ACCESS ENDPOINTS (for frontend display)
# =============================================================================

@app.get("/api/campaigns", response_model=List[CampaignData])
async def get_campaigns(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """Get campaigns directly from database for frontend display."""
    try:
        client = supabase_service.get_client()
        if not client:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Build query
        query = client.table("campaigns").select("*")
        
        if platform:
            query = query.eq("platform", platform.lower())
        if status:
            query = query.eq("status", status.lower())
            
        query = query.limit(limit).order("created_at", desc=True)
        
        result = query.execute()
        
        if result.data:
            campaigns = []
            for row in result.data:
                campaigns.append(CampaignData(**row))
            return campaigns
        else:
            return []
            
    except Exception as e:
        logger.error(f"❌ Failed to get campaigns: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics directly from database."""
    try:
        client = supabase_service.get_client()
        if not client:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Get all campaigns for calculations
        result = client.table("campaigns").select("*").execute()
        
        if not result.data:
            return DashboardStats(
                total_campaigns=0,
                active_campaigns=0,
                total_spend=0.0,
                total_revenue=0.0,
                average_roas=0.0,
                average_ctr=0.0,
                average_cpc=0.0,
                total_clicks=0,
                total_impressions=0,
                total_conversions=0
            )
        
        campaigns = result.data
        total_campaigns = len(campaigns)
        active_campaigns = len([c for c in campaigns if c.get('status') == 'active'])
        
        total_spend = sum(c.get('spend_amount', 0) for c in campaigns)
        total_revenue = sum(c.get('revenue', 0) for c in campaigns)
        total_clicks = sum(c.get('clicks', 0) for c in campaigns)
        total_impressions = sum(c.get('impressions', 0) for c in campaigns)
        total_conversions = sum(c.get('conversions', 0) for c in campaigns)
        
        # Calculate averages
        active_campaigns_data = [c for c in campaigns if c.get('status') == 'active']
        if active_campaigns_data:
            average_roas = sum(c.get('roas', 0) for c in active_campaigns_data) / len(active_campaigns_data)
            average_ctr = sum(c.get('ctr', 0) for c in active_campaigns_data) / len(active_campaigns_data)
            average_cpc = sum(c.get('cpc', 0) for c in active_campaigns_data) / len(active_campaigns_data)
        else:
            average_roas = 0.0
            average_ctr = 0.0
            average_cpc = 0.0
        
        return DashboardStats(
            total_campaigns=total_campaigns,
            active_campaigns=active_campaigns,
            total_spend=total_spend,
            total_revenue=total_revenue,
            average_roas=average_roas,
            average_ctr=average_ctr,
            average_cpc=average_cpc,
            total_clicks=total_clicks,
            total_impressions=total_impressions,
            total_conversions=total_conversions
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to get dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/campaigns/{campaign_id}", response_model=CampaignData)
async def get_campaign_by_id(campaign_id: str):
    """Get specific campaign by ID directly from database."""
    try:
        client = supabase_service.get_client()
        if not client:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        result = client.table("campaigns").select("*").eq("campaign_id", campaign_id).execute()
        
        if result.data and len(result.data) > 0:
            return CampaignData(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Campaign not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get campaign {campaign_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# MCP-INTEGRATED ENDPOINTS (for agentic operations)
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint with application info."""
    return {
        "name": "Campaign AI Application",
        "version": "1.0.0",
        "description": "MCP-integrated campaign optimization platform with direct data access",
        "status": "running",
        "endpoints": {
            "campaigns": "/api/campaigns",
            "dashboard_stats": "/api/dashboard/stats",
            "campaign_detail": "/api/campaigns/{campaign_id}",
            "optimize": "/optimize",
            "workflow": "/workflow",
            "workflow_status": "/workflow/{workflow_id}",
            "health": "/health",
            "tools": "/tools",
            "mcp": "/api/mcp"
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

# MCP Tool Call Request/Response models
class MCPToolRequest(BaseModel):
    tool: str
    params: Dict[str, Any] = {}

class MCPToolResponse(BaseModel):
    success: bool
    data: Any
    error: Optional[str] = None
    workflowId: Optional[str] = None
    langsmithTrace: Optional[str] = None

@app.post("/api/mcp", response_model=MCPToolResponse)
async def call_mcp_tool(request: MCPToolRequest):
    """
    Call MCP tools directly - this endpoint matches what the frontend expects.
    
    This endpoint provides direct access to MCP tools for the frontend,
    allowing it to call individual tools like mcp_list_campaigns_by_criteria.
    """
    try:
        logger.info(f"🔧 MCP Tool call: {request.tool} with params: {request.params}")
        
        # Ensure campaign agent is initialized
        if not campaign_agent or not campaign_agent.mcp_tools:
            await campaign_agent.initialize_mcp_connection()
        
        # Find the requested tool
        tool_to_call = None
        for tool in campaign_agent.mcp_tools:
            if tool.name == request.tool:
                tool_to_call = tool
                break
        
        if not tool_to_call:
            return MCPToolResponse(
                success=False,
                data=None,
                error=f"Tool '{request.tool}' not found. Available tools: {[t.name for t in campaign_agent.mcp_tools]}"
            )
        
        # Call the tool
        result = await tool_to_call.ainvoke(request.params)
        
        # Generate workflow ID for tracking
        workflow_id = f"mcp_{request.tool}_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"✅ MCP Tool '{request.tool}' executed successfully")
        
        return MCPToolResponse(
            success=True,
            data=result,
            workflowId=workflow_id,
            langsmithTrace=f"https://smith.langchain.com/trace/{workflow_id}"
        )
        
    except Exception as e:
        logger.error(f"❌ MCP Tool call failed: {str(e)}")
        return MCPToolResponse(
            success=False,
            data=None,
            error=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)