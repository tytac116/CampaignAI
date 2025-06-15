"""
Campaign Performance Optimization Platform - Main Application

This is the main FastAPI application entry point that brings together all components:
- API routes for campaigns, analytics, and optimization
- WebSocket endpoints for real-time updates
- MCP server integration
- Background task management
- Startup and shutdown event handlers
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .core.config import get_settings
from .core.database import init_db, close_db, get_session
from .api.routes.campaigns import router as campaigns_router
from .api.routes.analytics import router as analytics_router
from .services.mcp_server import mcp_server
from .workers.background_tasks import task_scheduler, celery_app
from .agents.coordinator import coordinator
from .data.seed_data import DataSeeder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected via WebSocket")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")
    
    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to {client_id}: {str(e)}")
                self.disconnect(client_id)
    
    async def broadcast(self, message: Dict[str, Any]):
        disconnected_clients = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to {client_id}: {str(e)}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

manager = ConnectionManager()

# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    
    # Startup
    logger.info("Starting Campaign Optimization Platform...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")
        
        # Start background tasks if configured
        if settings.enable_background_tasks:
            logger.info("Background tasks enabled")
            # Schedule initial metric simulation
            task_scheduler.schedule_metric_simulation()
        
        # Initialize MCP server
        logger.info("MCP server initialized")
        
        # Seed initial data if database is empty
        if settings.seed_initial_data:
            seeder = DataSeeder()
            await seeder.seed_initial_data()
            logger.info("Initial data seeded")
        
        logger.info("Application startup completed")
        
        yield
        
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down Campaign Optimization Platform...")
        
        # Close database connections
        await close_db()
        logger.info("Database connections closed")
        
        # Stop background tasks
        celery_app.control.broadcast('shutdown')
        logger.info("Background tasks stopped")
        
        logger.info("Application shutdown completed")

# Create FastAPI application
app = FastAPI(
    title="Campaign Performance Optimization Platform",
    description="AI-powered campaign optimization platform with Facebook and Instagram API simulation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API routers
app.include_router(campaigns_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0",
        "database": "connected",
        "services": {
            "mcp_server": "running",
            "background_tasks": "running" if settings.enable_background_tasks else "disabled",
            "coordinator": "running"
        }
    }

# System info endpoint
@app.get("/api/v1/system/info")
async def get_system_info():
    """Get system information and metrics"""
    
    # Get coordinator metrics
    coordinator_metrics = await coordinator.get_workflow_metrics()
    
    # Get task scheduler info
    task_info = {
        "running_tasks": len(task_scheduler.running_tasks),
        "completed_tasks_cleaned": task_scheduler.cleanup_completed_tasks()
    }
    
    return {
        "system": {
            "status": "running",
            "version": "1.0.0",
            "environment": settings.environment
        },
        "coordinator": coordinator_metrics,
        "background_tasks": task_info,
        "database": {
            "status": "connected",
            "pool_size": 10  # This would come from actual connection pool
        }
    }

# MCP server endpoint
@app.post("/api/v1/mcp")
async def handle_mcp_request(request: Dict[str, Any]):
    """Handle MCP (Model Context Protocol) requests"""
    try:
        response = await mcp_server.handle_request(request)
        return response.dict()
    except Exception as e:
        logger.error(f"MCP request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"MCP request failed: {str(e)}")

# WebSocket endpoint for real-time updates
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time campaign updates"""
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_json()
            
            # Handle different message types
            message_type = data.get("type")
            
            if message_type == "subscribe_campaign":
                campaign_id = data.get("campaign_id")
                await manager.send_personal_message({
                    "type": "subscription_confirmed",
                    "campaign_id": campaign_id,
                    "status": "subscribed"
                }, client_id)
                
            elif message_type == "get_workflow_status":
                workflow_id = data.get("workflow_id")
                status = await coordinator.get_workflow_status(workflow_id)
                
                await manager.send_personal_message({
                    "type": "workflow_status",
                    "workflow_id": workflow_id,
                    "status": status.dict() if status else None
                }, client_id)
                
            elif message_type == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": "2024-01-01T00:00:00Z"
                }, client_id)
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)

# Background task endpoints
@app.post("/api/v1/tasks/optimize/{campaign_id}")
async def trigger_optimization_task(campaign_id: str, priority: str = "medium"):
    """Manually trigger optimization task for a campaign"""
    
    if priority not in ["low", "medium", "high"]:
        raise HTTPException(status_code=400, detail="Priority must be 'low', 'medium', or 'high'")
    
    try:
        task_id = task_scheduler.schedule_optimization(campaign_id, priority)
        return {
            "task_id": task_id,
            "campaign_id": campaign_id,
            "priority": priority,
            "status": "scheduled"
        }
    except Exception as e:
        logger.error(f"Failed to schedule optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to schedule optimization: {str(e)}")

@app.get("/api/v1/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a background task"""
    
    task_info = task_scheduler.get_task_info(task_id)
    
    if not task_info:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task_info

@app.post("/api/v1/tasks/simulate-metrics")
async def trigger_metrics_simulation():
    """Manually trigger metrics simulation"""
    
    try:
        task_id = task_scheduler.schedule_metric_simulation()
        return {
            "task_id": task_id,
            "task_type": "metric_simulation",
            "status": "scheduled"
        }
    except Exception as e:
        logger.error(f"Failed to schedule metrics simulation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to schedule task: {str(e)}")

# Development data seeding endpoints
@app.post("/api/v1/dev/seed-data")
async def seed_development_data(
    facebook_campaigns: int = 100,
    instagram_campaigns: int = 100
):
    """Seed development data (development only)"""
    
    if settings.environment == "production":
        raise HTTPException(status_code=403, detail="Data seeding not allowed in production")
    
    try:
        seeder = DataSeeder()
        
        # Seed campaigns
        await seeder.create_sample_campaigns(
            facebook_count=facebook_campaigns,
            instagram_count=instagram_campaigns
        )
        
        return {
            "message": "Development data seeded successfully",
            "facebook_campaigns": facebook_campaigns,
            "instagram_campaigns": instagram_campaigns
        }
        
    except Exception as e:
        logger.error(f"Failed to seed data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to seed data: {str(e)}")

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

# Broadcast workflow updates via WebSocket
async def broadcast_workflow_update(workflow_id: str, status_data: Dict[str, Any]):
    """Broadcast workflow status updates to connected clients"""
    message = {
        "type": "workflow_update",
        "workflow_id": workflow_id,
        "data": status_data,
        "timestamp": "2024-01-01T00:00:00Z"
    }
    await manager.broadcast(message)

# Campaign performance broadcast
async def broadcast_campaign_update(campaign_id: str, performance_data: Dict[str, Any]):
    """Broadcast campaign performance updates"""
    message = {
        "type": "campaign_update",
        "campaign_id": campaign_id,
        "data": performance_data,
        "timestamp": "2024-01-01T00:00:00Z"
    }
    await manager.broadcast(message)

if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 