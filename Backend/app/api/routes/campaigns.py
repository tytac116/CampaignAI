"""
Campaign API Routes

This module provides REST API endpoints for campaign management and optimization.
Includes CRUD operations, performance metrics, and optimization workflows.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from pydantic import BaseModel, Field

from ...core.database import get_session
from ...models.campaign import Campaign, CampaignStatus, PlatformType
from ...models.campaign_metrics import CampaignMetrics
from ...agents.graph import campaign_optimization_graph
from ...agents.coordinator import coordinator
from ...agents.state import Priority, WorkflowStatus

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/campaigns", tags=["campaigns"])

# Pydantic models for request/response
class CampaignCreate(BaseModel):
    """Campaign creation request"""
    name: str = Field(..., min_length=1, max_length=255)
    platform: PlatformType
    budget: float = Field(..., gt=0)
    start_date: datetime
    end_date: Optional[datetime] = None
    targeting: Optional[Dict[str, Any]] = None
    ad_creative: Optional[Dict[str, Any]] = None

class CampaignUpdate(BaseModel):
    """Campaign update request"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[CampaignStatus] = None
    budget: Optional[float] = Field(None, gt=0)
    end_date: Optional[datetime] = None
    targeting: Optional[Dict[str, Any]] = None
    ad_creative: Optional[Dict[str, Any]] = None

class CampaignResponse(BaseModel):
    """Campaign response model"""
    id: str
    name: str
    platform: PlatformType
    status: CampaignStatus
    budget: Optional[float]
    daily_spend: Optional[float]
    impressions: Optional[int]
    clicks: Optional[int]
    conversions: Optional[int]
    ctr: Optional[float]
    cpc: Optional[float]
    roas: Optional[float]
    start_date: datetime
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class CampaignMetricsResponse(BaseModel):
    """Campaign metrics response"""
    campaign_id: str
    date: str
    impressions: int
    clicks: int
    conversions: int
    spend: float
    ctr: float
    cpc: float
    roas: float
    age_demographics: Optional[Dict[str, Any]]
    gender_demographics: Optional[Dict[str, Any]]
    location_demographics: Optional[Dict[str, Any]]

class OptimizationRequest(BaseModel):
    """Optimization request"""
    campaign_ids: List[str]
    optimization_type: str = Field(default="all", regex="^(budget|targeting|creative|all)$")
    priority: Priority = Priority.MEDIUM
    constraints: Optional[Dict[str, Any]] = None

class WorkflowResponse(BaseModel):
    """Workflow response"""
    workflow_id: str
    campaign_id: str
    status: WorkflowStatus
    current_step: str
    progress: float
    started_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]

@router.get("/", response_model=List[CampaignResponse])
async def list_campaigns(
    platform: Optional[PlatformType] = Query(None, description="Filter by platform"),
    status: Optional[CampaignStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=1000, description="Number of campaigns to return"),
    offset: int = Query(0, ge=0, description="Number of campaigns to skip"),
    session: AsyncSession = Depends(get_session)
):
    """List campaigns with optional filtering"""
    
    query = select(Campaign)
    
    if platform:
        query = query.where(Campaign.platform == platform)
    if status:
        query = query.where(Campaign.status == status)
    
    query = query.offset(offset).limit(limit).order_by(desc(Campaign.created_at))
    
    result = await session.execute(query)
    campaigns = result.scalars().all()
    
    return [CampaignResponse.from_orm(campaign) for campaign in campaigns]

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get a specific campaign by ID"""
    
    campaign = await session.get(Campaign, campaign_id)
    
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
    
    return CampaignResponse.from_orm(campaign)

@router.post("/", response_model=CampaignResponse)
async def create_campaign(
    campaign_data: CampaignCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new campaign"""
    
    campaign = Campaign(
        name=campaign_data.name,
        platform=campaign_data.platform,
        budget=campaign_data.budget,
        start_date=campaign_data.start_date,
        end_date=campaign_data.end_date,
        targeting=campaign_data.targeting,
        ad_creative=campaign_data.ad_creative,
        status=CampaignStatus.ACTIVE
    )
    
    session.add(campaign)
    await session.commit()
    await session.refresh(campaign)
    
    logger.info(f"Created campaign {campaign.id}: {campaign.name}")
    
    return CampaignResponse.from_orm(campaign)

@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    campaign_data: CampaignUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update an existing campaign"""
    
    campaign = await session.get(Campaign, campaign_id)
    
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
    
    # Update fields if provided
    update_data = campaign_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    campaign.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(campaign)
    
    logger.info(f"Updated campaign {campaign_id}")
    
    return CampaignResponse.from_orm(campaign)

@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Delete a campaign"""
    
    campaign = await session.get(Campaign, campaign_id)
    
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
    
    await session.delete(campaign)
    await session.commit()
    
    logger.info(f"Deleted campaign {campaign_id}")
    
    return {"message": f"Campaign {campaign_id} deleted successfully"}

@router.get("/{campaign_id}/metrics", response_model=List[CampaignMetricsResponse])
async def get_campaign_metrics(
    campaign_id: str,
    days: int = Query(7, ge=1, le=90, description="Number of days of metrics to retrieve"),
    session: AsyncSession = Depends(get_session)
):
    """Get campaign metrics for a specified time range"""
    
    # Verify campaign exists
    campaign = await session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
    
    # Get metrics
    start_date = datetime.utcnow().date() - timedelta(days=days)
    
    query = select(CampaignMetrics).where(
        and_(
            CampaignMetrics.campaign_id == campaign_id,
            CampaignMetrics.date >= start_date
        )
    ).order_by(desc(CampaignMetrics.date))
    
    result = await session.execute(query)
    metrics = result.scalars().all()
    
    return [
        CampaignMetricsResponse(
            campaign_id=m.campaign_id,
            date=m.date.isoformat(),
            impressions=m.impressions,
            clicks=m.clicks,
            conversions=m.conversions,
            spend=float(m.spend),
            ctr=float(m.ctr),
            cpc=float(m.cpc),
            roas=float(m.roas),
            age_demographics=m.age_demographics,
            gender_demographics=m.gender_demographics,
            location_demographics=m.location_demographics
        )
        for m in metrics
    ]

@router.post("/{campaign_id}/optimize", response_model=WorkflowResponse)
async def optimize_campaign(
    campaign_id: str,
    optimization_type: str = Query("all", regex="^(budget|targeting|creative|all)$"),
    priority: Priority = Query(Priority.MEDIUM),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    session: AsyncSession = Depends(get_session)
):
    """Start campaign optimization workflow"""
    
    # Verify campaign exists
    campaign = await session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
    
    # Start optimization workflow
    try:
        result = await campaign_optimization_graph.run_workflow(
            campaign_id=campaign_id,
            trigger_reason="api_optimization_request",
            priority=priority
        )
        
        logger.info(f"Started optimization workflow {result['workflow_id']} for campaign {campaign_id}")
        
        return WorkflowResponse(
            workflow_id=result["workflow_id"],
            campaign_id=campaign_id,
            status=result["status"],
            current_step=result["current_step"],
            progress=result["progress"],
            started_at=result["started_at"],
            completed_at=result.get("completed_at"),
            error_message=result.get("error_message")
        )
        
    except Exception as e:
        logger.error(f"Failed to start optimization for campaign {campaign_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start optimization: {str(e)}")

@router.post("/optimize/batch", response_model=List[WorkflowResponse])
async def optimize_campaigns_batch(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    session: AsyncSession = Depends(get_session)
):
    """Optimize multiple campaigns in batch"""
    
    workflows = []
    
    for campaign_id in request.campaign_ids:
        # Verify campaign exists
        campaign = await session.get(Campaign, campaign_id)
        if not campaign:
            logger.warning(f"Campaign {campaign_id} not found, skipping")
            continue
        
        try:
            result = await campaign_optimization_graph.run_workflow(
                campaign_id=campaign_id,
                trigger_reason="api_batch_optimization",
                priority=request.priority
            )
            
            workflows.append(WorkflowResponse(
                workflow_id=result["workflow_id"],
                campaign_id=campaign_id,
                status=result["status"],
                current_step=result["current_step"],
                progress=result["progress"],
                started_at=result["started_at"],
                completed_at=result.get("completed_at"),
                error_message=result.get("error_message")
            ))
            
        except Exception as e:
            logger.error(f"Failed to start optimization for campaign {campaign_id}: {str(e)}")
            workflows.append(WorkflowResponse(
                workflow_id=f"error_{campaign_id}",
                campaign_id=campaign_id,
                status=WorkflowStatus.FAILED,
                current_step="initialization",
                progress=0.0,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                error_message=str(e)
            ))
    
    logger.info(f"Started batch optimization for {len(workflows)} campaigns")
    
    return workflows

@router.get("/{campaign_id}/workflow/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow_status(
    campaign_id: str,
    workflow_id: str
):
    """Get workflow execution status"""
    
    try:
        state = await campaign_optimization_graph.get_workflow_state(workflow_id)
        
        if not state:
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
        
        return WorkflowResponse(
            workflow_id=workflow_id,
            campaign_id=state["campaign_id"],
            status=state["status"],
            current_step=state["current_step"],
            progress=state["progress"],
            started_at=state["started_at"],
            completed_at=state.get("completed_at"),
            error_message=state.get("error_message")
        )
        
    except Exception as e:
        logger.error(f"Failed to get workflow status {workflow_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")

@router.get("/{campaign_id}/performance")
async def get_campaign_performance(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get campaign performance summary"""
    
    # Verify campaign exists
    campaign = await session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
    
    # Get recent metrics for analysis
    start_date = datetime.utcnow().date() - timedelta(days=30)
    
    query = select(CampaignMetrics).where(
        and_(
            CampaignMetrics.campaign_id == campaign_id,
            CampaignMetrics.date >= start_date
        )
    ).order_by(desc(CampaignMetrics.date))
    
    result = await session.execute(query)
    metrics = result.scalars().all()
    
    if not metrics:
        return {
            "campaign_id": campaign_id,
            "performance_summary": "No metrics available",
            "recommendations": []
        }
    
    # Calculate performance metrics
    total_impressions = sum(m.impressions for m in metrics)
    total_clicks = sum(m.clicks for m in metrics)
    total_conversions = sum(m.conversions for m in metrics)
    total_spend = sum(float(m.spend) for m in metrics)
    
    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    avg_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
    avg_roas = (sum(float(m.roas) for m in metrics) / len(metrics)) if metrics else 0
    
    # Simple performance assessment
    performance_score = 0
    recommendations = []
    
    if avg_ctr > 2.0:
        performance_score += 25
    elif avg_ctr < 1.0:
        recommendations.append("Consider improving ad creative to increase CTR")
    
    if avg_cpc < 2.0:
        performance_score += 25
    elif avg_cpc > 5.0:
        recommendations.append("CPC is high, consider refining targeting")
    
    if avg_roas > 3.0:
        performance_score += 50
    elif avg_roas < 2.0:
        recommendations.append("ROAS is below target, review conversion tracking")
    
    performance_level = "Excellent" if performance_score >= 75 else \
                      "Good" if performance_score >= 50 else \
                      "Needs Improvement"
    
    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign.name,
        "performance_summary": {
            "level": performance_level,
            "score": performance_score,
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "total_spend": total_spend,
            "avg_ctr": round(avg_ctr, 2),
            "avg_cpc": round(avg_cpc, 2),
            "avg_roas": round(avg_roas, 2)
        },
        "recommendations": recommendations,
        "analysis_period": "30 days",
        "analyzed_at": datetime.utcnow().isoformat()
    } 