"""
MCP (Model Context Protocol) Server Integration

This module provides MCP server functionality for the Campaign Optimization Platform.
It enables external AI models to interact with the campaign data and optimization system.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from pydantic import BaseModel
from ..core.config import get_settings
from ..core.database import get_session
from ..models.campaign import Campaign
from ..models.campaign_metrics import CampaignMetrics
from ..agents.graph import campaign_optimization_graph

logger = logging.getLogger(__name__)
settings = get_settings()

class MCPRequest(BaseModel):
    """MCP request model"""
    method: str
    params: Dict[str, Any]
    id: Optional[str] = None

class MCPResponse(BaseModel):
    """MCP response model"""
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None

class MCPError(BaseModel):
    """MCP error model"""
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None

class MCPServer:
    """
    MCP Server for Campaign Optimization Platform
    
    Provides external AI models with access to:
    - Campaign data and metrics
    - Optimization workflows
    - Real-time performance insights
    - Custom analysis requests
    """
    
    def __init__(self):
        self.capabilities = {
            "textDocument/completion": True,
            "textDocument/references": True,
            "workspace/executeCommand": True
        }
        
        # Available MCP methods
        self.methods = {
            "initialize": self._initialize,
            "shutdown": self._shutdown,
            "campaign/get": self._get_campaign,
            "campaign/list": self._list_campaigns,
            "campaign/metrics": self._get_campaign_metrics,
            "campaign/optimize": self._optimize_campaign,
            "campaign/analyze": self._analyze_campaign,
            "insights/performance": self._get_performance_insights,
            "insights/trends": self._get_trend_insights,
            "workflow/start": self._start_workflow,
            "workflow/status": self._get_workflow_status,
            "tools/list": self._list_tools,
            "tools/call": self._call_tool
        }
        
        # Available tools for AI models
        self.tools = {
            "campaign_optimizer": {
                "name": "campaign_optimizer",
                "description": "Optimize campaign performance using AI analysis",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {"type": "string", "description": "Campaign ID to optimize"},
                        "optimization_type": {"type": "string", "enum": ["budget", "targeting", "creative", "all"]},
                        "constraints": {"type": "object", "description": "Optimization constraints"}
                    },
                    "required": ["campaign_id"]
                }
            },
            "performance_analyzer": {
                "name": "performance_analyzer", 
                "description": "Analyze campaign performance and identify issues",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "campaign_ids": {"type": "array", "items": {"type": "string"}},
                        "time_range": {"type": "string", "description": "Time range for analysis (e.g., '7d', '30d')"},
                        "metrics": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["campaign_ids"]
                }
            },
            "trend_detector": {
                "name": "trend_detector",
                "description": "Detect trends and patterns in campaign data",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "platform": {"type": "string", "enum": ["facebook", "instagram", "all"]},
                        "metric": {"type": "string", "description": "Metric to analyze for trends"},
                        "period": {"type": "string", "description": "Time period for trend analysis"}
                    }
                }
            }
        }
    
    async def handle_request(self, request_data: Dict[str, Any]) -> MCPResponse:
        """Handle incoming MCP request"""
        try:
            request = MCPRequest(**request_data)
            
            if request.method not in self.methods:
                return MCPResponse(
                    error=MCPError(
                        code=-32601,
                        message=f"Method not found: {request.method}"
                    ).__dict__,
                    id=request.id
                )
            
            # Execute the method
            handler = self.methods[request.method]
            result = await handler(request.params)
            
            return MCPResponse(result=result, id=request.id)
            
        except Exception as e:
            logger.error(f"MCP request failed: {str(e)}")
            return MCPResponse(
                error=MCPError(
                    code=-32603,
                    message="Internal error",
                    data={"details": str(e)}
                ).__dict__,
                id=request_data.get("id")
            )
    
    async def _initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize MCP connection"""
        return {
            "capabilities": self.capabilities,
            "serverInfo": {
                "name": "CampaignAI MCP Server",
                "version": "1.0.0"
            }
        }
    
    async def _shutdown(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Shutdown MCP connection"""
        return {"message": "Server shutdown"}
    
    async def _get_campaign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed campaign information"""
        campaign_id = params.get("campaign_id")
        
        if not campaign_id:
            raise ValueError("campaign_id is required")
        
        async with get_session() as session:
            campaign = await session.get(Campaign, campaign_id)
            
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            return {
                "campaign": {
                    "id": campaign.id,
                    "name": campaign.name,
                    "platform": campaign.platform.value,
                    "status": campaign.status.value,
                    "budget": float(campaign.budget) if campaign.budget else None,
                    "daily_spend": float(campaign.daily_spend) if campaign.daily_spend else None,
                    "impressions": campaign.impressions,
                    "clicks": campaign.clicks,
                    "conversions": campaign.conversions,
                    "ctr": float(campaign.ctr) if campaign.ctr else None,
                    "cpc": float(campaign.cpc) if campaign.cpc else None,
                    "roas": float(campaign.roas) if campaign.roas else None,
                    "created_at": campaign.created_at.isoformat(),
                    "updated_at": campaign.updated_at.isoformat()
                }
            }
    
    async def _list_campaigns(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List campaigns with optional filtering"""
        platform = params.get("platform")
        status = params.get("status")
        limit = params.get("limit", 50)
        offset = params.get("offset", 0)
        
        async with get_session() as session:
            query = session.query(Campaign)
            
            if platform:
                query = query.filter(Campaign.platform == platform)
            if status:
                query = query.filter(Campaign.status == status)
            
            campaigns = await query.offset(offset).limit(limit).all()
            
            return {
                "campaigns": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "platform": c.platform.value,
                        "status": c.status.value,
                        "budget": float(c.budget) if c.budget else None,
                        "daily_spend": float(c.daily_spend) if c.daily_spend else None,
                        "roas": float(c.roas) if c.roas else None
                    }
                    for c in campaigns
                ],
                "total": len(campaigns),
                "offset": offset,
                "limit": limit
            }
    
    async def _get_campaign_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get campaign metrics for specified time range"""
        campaign_id = params.get("campaign_id")
        days = params.get("days", 7)
        
        if not campaign_id:
            raise ValueError("campaign_id is required")
        
        async with get_session() as session:
            # Get recent metrics
            metrics = await session.query(CampaignMetrics)\
                .filter(CampaignMetrics.campaign_id == campaign_id)\
                .filter(CampaignMetrics.date >= datetime.utcnow().date() - timedelta(days=days))\
                .order_by(CampaignMetrics.date.desc())\
                .all()
            
            return {
                "campaign_id": campaign_id,
                "time_range_days": days,
                "metrics": [
                    {
                        "date": m.date.isoformat(),
                        "impressions": m.impressions,
                        "clicks": m.clicks,
                        "conversions": m.conversions,
                        "spend": float(m.spend),
                        "ctr": float(m.ctr),
                        "cpc": float(m.cpc),
                        "roas": float(m.roas)
                    }
                    for m in metrics
                ]
            }
    
    async def _optimize_campaign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start campaign optimization workflow"""
        campaign_id = params.get("campaign_id")
        optimization_type = params.get("optimization_type", "all")
        
        if not campaign_id:
            raise ValueError("campaign_id is required")
        
        # Start optimization workflow
        result = await campaign_optimization_graph.run_workflow(
            campaign_id=campaign_id,
            trigger_reason="mcp_api_request",
            priority=Priority.MEDIUM
        )
        
        return {
            "workflow_id": result["workflow_id"],
            "status": result["status"].value,
            "optimization_type": optimization_type,
            "started_at": result["started_at"].isoformat(),
            "recommendations": [
                {
                    "type": rec.optimization_type,
                    "description": rec.description,
                    "confidence": rec.confidence_score,
                    "estimated_impact": rec.estimated_impact
                }
                for rec in result.get("optimization_recommendations", [])
            ]
        }
    
    async def _analyze_campaign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform custom campaign analysis"""
        campaign_ids = params.get("campaign_ids", [])
        analysis_type = params.get("analysis_type", "performance")
        
        if not campaign_ids:
            raise ValueError("campaign_ids is required")
        
        # This would typically call specialized analysis functions
        # For now, return basic analysis structure
        return {
            "analysis_type": analysis_type,
            "campaign_ids": campaign_ids,
            "insights": [
                {
                    "campaign_id": cid,
                    "performance_score": 0.75,  # Placeholder
                    "key_insights": [
                        "CTR is above industry average",
                        "CPC could be optimized further",
                        "Strong weekend performance"
                    ],
                    "recommendations": [
                        "Consider increasing weekend budget allocation",
                        "Test new ad creative variants",
                        "Expand high-performing audience segments"
                    ]
                }
                for cid in campaign_ids
            ],
            "analyzed_at": datetime.utcnow().isoformat()
        }
    
    async def _get_performance_insights(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get performance insights across campaigns"""
        platform = params.get("platform", "all")
        time_range = params.get("time_range", "7d")
        
        # This would perform actual analysis
        # For now, return sample insights
        return {
            "platform": platform,
            "time_range": time_range,
            "insights": {
                "total_campaigns": 156,
                "active_campaigns": 89,
                "avg_ctr": 0.0234,
                "avg_cpc": 2.45,
                "avg_roas": 3.2,
                "top_performing_campaigns": [
                    {"id": "camp_123", "name": "Summer Sale", "roas": 4.8},
                    {"id": "camp_456", "name": "Brand Awareness", "roas": 4.1}
                ],
                "underperforming_campaigns": [
                    {"id": "camp_789", "name": "Product Launch", "roas": 0.8}
                ]
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _get_trend_insights(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get trend analysis insights"""
        metric = params.get("metric", "roas")
        period = params.get("period", "30d")
        
        return {
            "metric": metric,
            "period": period,
            "trends": {
                "overall_trend": "increasing",
                "trend_strength": 0.72,
                "weekly_pattern": [0.8, 0.9, 1.1, 1.2, 1.0, 1.3, 1.1],
                "anomalies": [
                    {
                        "date": "2024-01-15",
                        "deviation": -0.45,
                        "description": "Significant drop in ROAS"
                    }
                ],
                "forecast": {
                    "next_7_days": [1.1, 1.2, 1.0, 1.1, 1.3, 1.4, 1.2],
                    "confidence": 0.68
                }
            },
            "analyzed_at": datetime.utcnow().isoformat()
        }
    
    async def _start_workflow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start a custom workflow"""
        campaign_id = params.get("campaign_id")
        workflow_type = params.get("workflow_type", "optimization")
        
        if not campaign_id:
            raise ValueError("campaign_id is required")
        
        result = await campaign_optimization_graph.run_workflow(
            campaign_id=campaign_id,
            trigger_reason=f"mcp_{workflow_type}_request"
        )
        
        return {
            "workflow_id": result["workflow_id"],
            "workflow_type": workflow_type,
            "status": result["status"].value,
            "started_at": result["started_at"].isoformat()
        }
    
    async def _get_workflow_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get workflow execution status"""
        workflow_id = params.get("workflow_id")
        
        if not workflow_id:
            raise ValueError("workflow_id is required")
        
        state = await campaign_optimization_graph.get_workflow_state(workflow_id)
        
        if not state:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        return {
            "workflow_id": workflow_id,
            "status": state["status"].value,
            "current_step": state["current_step"],
            "progress": state["progress"],
            "started_at": state["started_at"].isoformat(),
            "completed_at": state.get("completed_at").isoformat() if state.get("completed_at") else None,
            "error_message": state.get("error_message")
        }
    
    async def _list_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available tools"""
        return {
            "tools": list(self.tools.values())
        }
    
    async def _call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool"""
        tool_name = params.get("name")
        tool_params = params.get("arguments", {})
        
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        
        # Route to specific tool handlers
        if tool_name == "campaign_optimizer":
            return await self._optimize_campaign(tool_params)
        elif tool_name == "performance_analyzer":
            return await self._analyze_campaign(tool_params)
        elif tool_name == "trend_detector":
            return await self._get_trend_insights(tool_params)
        
        raise ValueError(f"Tool {tool_name} not implemented")

# Global MCP server instance
mcp_server = MCPServer() 