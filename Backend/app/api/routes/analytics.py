"""
Analytics API Routes

This module provides REST API endpoints for campaign analytics, insights, and reporting.
Includes performance dashboards, trend analysis, and custom analytics queries.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from pydantic import BaseModel, Field

from ...core.database import get_session
from ...models.campaign import Campaign, PlatformType, CampaignStatus
from ...models.campaign_metrics import CampaignMetrics
from ...services.facebook_api_sim import facebook_api_sim
from ...services.instagram_api_sim import instagram_api_sim

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/analytics", tags=["analytics"])

# Pydantic models
class PerformanceMetrics(BaseModel):
    """Performance metrics response"""
    total_campaigns: int
    active_campaigns: int
    total_impressions: int
    total_clicks: int
    total_conversions: int
    total_spend: float
    avg_ctr: float
    avg_cpc: float
    avg_roas: float

class PlatformComparison(BaseModel):
    """Platform comparison response"""
    platform: PlatformType
    campaigns: int
    impressions: int
    clicks: int
    conversions: int
    spend: float
    ctr: float
    cpc: float
    roas: float

class TrendData(BaseModel):
    """Trend data point"""
    date: str
    impressions: int
    clicks: int
    conversions: int
    spend: float
    ctr: float
    cpc: float
    roas: float

class TopPerformer(BaseModel):
    """Top performing campaign"""
    campaign_id: str
    campaign_name: str
    platform: PlatformType
    metric_value: float
    metric_name: str

class AnalyticsOverview(BaseModel):
    """Analytics overview response"""
    performance_metrics: PerformanceMetrics
    platform_comparison: List[PlatformComparison]
    trends: List[TrendData]
    top_performers: List[TopPerformer]
    generated_at: datetime

@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    platform: Optional[PlatformType] = Query(None, description="Filter by platform"),
    session: AsyncSession = Depends(get_session)
):
    """Get comprehensive analytics overview"""
    
    start_date = datetime.utcnow().date() - timedelta(days=days)
    
    # Build base query
    query = select(Campaign).where(Campaign.created_at >= start_date)
    if platform:
        query = query.where(Campaign.platform == platform)
    
    # Get campaigns
    result = await session.execute(query)
    campaigns = result.scalars().all()
    
    # Calculate performance metrics
    total_campaigns = len(campaigns)
    active_campaigns = len([c for c in campaigns if c.status == CampaignStatus.ACTIVE])
    
    total_impressions = sum(c.impressions or 0 for c in campaigns)
    total_clicks = sum(c.clicks or 0 for c in campaigns)
    total_conversions = sum(c.conversions or 0 for c in campaigns)
    total_spend = sum(float(c.daily_spend or 0) for c in campaigns) * days
    
    avg_ctr = (total_clicks / total_impressions) if total_impressions > 0 else 0
    avg_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
    avg_roas = sum(float(c.roas or 0) for c in campaigns) / len(campaigns) if campaigns else 0
    
    performance_metrics = PerformanceMetrics(
        total_campaigns=total_campaigns,
        active_campaigns=active_campaigns,
        total_impressions=total_impressions,
        total_clicks=total_clicks,
        total_conversions=total_conversions,
        total_spend=total_spend,
        avg_ctr=avg_ctr,
        avg_cpc=avg_cpc,
        avg_roas=avg_roas
    )
    
    # Platform comparison
    platform_stats = {}
    for campaign in campaigns:
        platform_name = campaign.platform
        if platform_name not in platform_stats:
            platform_stats[platform_name] = {
                'campaigns': 0,
                'impressions': 0,
                'clicks': 0,
                'conversions': 0,
                'spend': 0.0
            }
        
        stats = platform_stats[platform_name]
        stats['campaigns'] += 1
        stats['impressions'] += campaign.impressions or 0
        stats['clicks'] += campaign.clicks or 0
        stats['conversions'] += campaign.conversions or 0
        stats['spend'] += float(campaign.daily_spend or 0) * days
    
    platform_comparison = []
    for platform_name, stats in platform_stats.items():
        ctr = (stats['clicks'] / stats['impressions']) if stats['impressions'] > 0 else 0
        cpc = (stats['spend'] / stats['clicks']) if stats['clicks'] > 0 else 0
        
        # Calculate ROAS for platform
        platform_campaigns = [c for c in campaigns if c.platform == platform_name]
        platform_roas = sum(float(c.roas or 0) for c in platform_campaigns) / len(platform_campaigns) if platform_campaigns else 0
        
        platform_comparison.append(PlatformComparison(
            platform=platform_name,
            campaigns=stats['campaigns'],
            impressions=stats['impressions'],
            clicks=stats['clicks'],
            conversions=stats['conversions'],
            spend=stats['spend'],
            ctr=ctr,
            cpc=cpc,
            roas=platform_roas
        ))
    
    # Get trends (simplified - daily aggregates)
    trends = []
    for i in range(min(days, 30)):  # Limit to 30 data points
        trend_date = datetime.utcnow().date() - timedelta(days=i)
        
        # This would typically query daily metrics
        # For now, generate sample trend data based on campaigns
        daily_impressions = int(total_impressions * (0.8 + 0.4 * (i % 7) / 7) / days)
        daily_clicks = int(daily_impressions * avg_ctr)
        daily_conversions = int(daily_clicks * 0.1)  # 10% conversion rate
        daily_spend = total_spend / days
        
        trends.append(TrendData(
            date=trend_date.isoformat(),
            impressions=daily_impressions,
            clicks=daily_clicks,
            conversions=daily_conversions,
            spend=daily_spend,
            ctr=avg_ctr,
            cpc=avg_cpc,
            roas=avg_roas
        ))
    
    # Top performers
    top_performers = []
    
    # Top by ROAS
    top_roas_campaigns = sorted(campaigns, key=lambda x: x.roas or 0, reverse=True)[:3]
    for campaign in top_roas_campaigns:
        if campaign.roas:
            top_performers.append(TopPerformer(
                campaign_id=campaign.id,
                campaign_name=campaign.name,
                platform=campaign.platform,
                metric_value=float(campaign.roas),
                metric_name="ROAS"
            ))
    
    # Top by CTR
    top_ctr_campaigns = sorted(campaigns, key=lambda x: x.ctr or 0, reverse=True)[:3]
    for campaign in top_ctr_campaigns:
        if campaign.ctr:
            top_performers.append(TopPerformer(
                campaign_id=campaign.id,
                campaign_name=campaign.name,
                platform=campaign.platform,
                metric_value=float(campaign.ctr),
                metric_name="CTR"
            ))
    
    return AnalyticsOverview(
        performance_metrics=performance_metrics,
        platform_comparison=platform_comparison,
        trends=list(reversed(trends)),  # Most recent first
        top_performers=top_performers,
        generated_at=datetime.utcnow()
    )

@router.get("/performance")
async def get_performance_insights(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    platform: Optional[PlatformType] = Query(None, description="Filter by platform"),
    session: AsyncSession = Depends(get_session)
):
    """Get detailed performance insights"""
    
    start_date = datetime.utcnow().date() - timedelta(days=days)
    
    # Get campaigns with metrics
    query = select(Campaign).where(Campaign.created_at >= start_date)
    if platform:
        query = query.where(Campaign.platform == platform)
    
    result = await session.execute(query)
    campaigns = result.scalars().all()
    
    # Performance analysis
    insights = {
        "total_campaigns_analyzed": len(campaigns),
        "analysis_period": f"{days} days",
        "platform_filter": platform.value if platform else "all",
        "key_insights": [],
        "performance_segments": {
            "high_performers": [],
            "average_performers": [],
            "underperformers": []
        },
        "recommendations": []
    }
    
    if not campaigns:
        insights["key_insights"].append("No campaigns found for the specified criteria")
        return insights
    
    # Calculate benchmarks
    avg_roas = sum(float(c.roas or 0) for c in campaigns) / len(campaigns)
    avg_ctr = sum(float(c.ctr or 0) for c in campaigns) / len(campaigns)
    avg_cpc = sum(float(c.cpc or 0) for c in campaigns) / len(campaigns)
    
    # Segment campaigns by performance
    for campaign in campaigns:
        campaign_roas = float(campaign.roas or 0)
        campaign_ctr = float(campaign.ctr or 0)
        campaign_cpc = float(campaign.cpc or 0)
        
        performance_score = 0
        
        # ROAS scoring
        if campaign_roas > avg_roas * 1.2:
            performance_score += 3
        elif campaign_roas > avg_roas * 0.8:
            performance_score += 2
        else:
            performance_score += 1
        
        # CTR scoring
        if campaign_ctr > avg_ctr * 1.2:
            performance_score += 3
        elif campaign_ctr > avg_ctr * 0.8:
            performance_score += 2
        else:
            performance_score += 1
        
        # CPC scoring (lower is better)
        if campaign_cpc < avg_cpc * 0.8:
            performance_score += 3
        elif campaign_cpc < avg_cpc * 1.2:
            performance_score += 2
        else:
            performance_score += 1
        
        campaign_data = {
            "id": campaign.id,
            "name": campaign.name,
            "platform": campaign.platform.value,
            "roas": campaign_roas,
            "ctr": campaign_ctr,
            "cpc": campaign_cpc,
            "performance_score": performance_score
        }
        
        if performance_score >= 8:
            insights["performance_segments"]["high_performers"].append(campaign_data)
        elif performance_score >= 6:
            insights["performance_segments"]["average_performers"].append(campaign_data)
        else:
            insights["performance_segments"]["underperformers"].append(campaign_data)
    
    # Generate insights
    high_performers = len(insights["performance_segments"]["high_performers"])
    underperformers = len(insights["performance_segments"]["underperformers"])
    
    insights["key_insights"].append(f"{high_performers} campaigns are high performers ({high_performers/len(campaigns)*100:.1f}%)")
    insights["key_insights"].append(f"{underperformers} campaigns need optimization ({underperformers/len(campaigns)*100:.1f}%)")
    
    if avg_roas > 3.0:
        insights["key_insights"].append(f"Overall ROAS of {avg_roas:.2f} is above industry average")
    elif avg_roas < 2.0:
        insights["key_insights"].append(f"Overall ROAS of {avg_roas:.2f} is below industry average")
    
    # Generate recommendations
    if underperformers > len(campaigns) * 0.3:
        insights["recommendations"].append("Consider pausing or optimizing underperforming campaigns")
    
    if avg_ctr < 0.02:
        insights["recommendations"].append("Overall CTR is low - review ad creative and targeting")
    
    if avg_cpc > 3.0:
        insights["recommendations"].append("CPC is high - consider refining audience targeting")
    
    insights["generated_at"] = datetime.utcnow().isoformat()
    
    return insights

@router.get("/trends/{metric}")
async def get_metric_trends(
    metric: str = Query(..., regex="^(impressions|clicks|conversions|spend|ctr|cpc|roas)$"),
    days: int = Query(30, ge=7, le=90, description="Number of days to analyze"),
    platform: Optional[PlatformType] = Query(None, description="Filter by platform"),
    session: AsyncSession = Depends(get_session)
):
    """Get trends for a specific metric"""
    
    # This would typically query time-series data
    # For now, generate sample trend data
    
    trends = []
    for i in range(days):
        trend_date = datetime.utcnow().date() - timedelta(days=days-i-1)
        
        # Generate sample trend values with some variation
        base_value = {
            "impressions": 10000,
            "clicks": 200,
            "conversions": 20,
            "spend": 500.0,
            "ctr": 0.02,
            "cpc": 2.5,
            "roas": 3.2
        }[metric]
        
        # Add weekly pattern and random variation
        weekly_multiplier = 1.0 + 0.3 * (i % 7) / 7  # Weekend boost
        random_multiplier = 0.8 + 0.4 * ((i * 17) % 100) / 100  # Pseudo-random
        
        value = base_value * weekly_multiplier * random_multiplier
        
        trends.append({
            "date": trend_date.isoformat(),
            "value": round(value, 4),
            "metric": metric
        })
    
    # Calculate trend direction
    if len(trends) >= 7:
        recent_avg = sum(t["value"] for t in trends[-7:]) / 7
        previous_avg = sum(t["value"] for t in trends[-14:-7]) / 7
        trend_direction = "increasing" if recent_avg > previous_avg else "decreasing"
        trend_strength = abs(recent_avg - previous_avg) / previous_avg if previous_avg > 0 else 0
    else:
        trend_direction = "stable"
        trend_strength = 0
    
    return {
        "metric": metric,
        "analysis_period": f"{days} days",
        "platform_filter": platform.value if platform else "all",
        "trend_direction": trend_direction,
        "trend_strength": round(trend_strength, 4),
        "data_points": trends,
        "summary": {
            "min_value": min(t["value"] for t in trends),
            "max_value": max(t["value"] for t in trends),
            "avg_value": sum(t["value"] for t in trends) / len(trends),
            "latest_value": trends[-1]["value"] if trends else 0
        },
        "generated_at": datetime.utcnow().isoformat()
    }

@router.get("/comparison")
async def get_platform_comparison(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    session: AsyncSession = Depends(get_session)
):
    """Compare performance across platforms"""
    
    start_date = datetime.utcnow().date() - timedelta(days=days)
    
    # Get campaigns by platform
    query = select(Campaign).where(Campaign.created_at >= start_date)
    result = await session.execute(query)
    campaigns = result.scalars().all()
    
    # Group by platform
    platform_data = {}
    
    for campaign in campaigns:
        platform = campaign.platform.value
        
        if platform not in platform_data:
            platform_data[platform] = {
                "platform": platform,
                "campaigns": [],
                "total_campaigns": 0,
                "active_campaigns": 0,
                "metrics": {
                    "impressions": 0,
                    "clicks": 0,
                    "conversions": 0,
                    "spend": 0.0
                }
            }
        
        platform_data[platform]["campaigns"].append({
            "id": campaign.id,
            "name": campaign.name,
            "roas": float(campaign.roas or 0),
            "ctr": float(campaign.ctr or 0),
            "cpc": float(campaign.cpc or 0)
        })
        
        platform_data[platform]["total_campaigns"] += 1
        if campaign.status == CampaignStatus.ACTIVE:
            platform_data[platform]["active_campaigns"] += 1
        
        metrics = platform_data[platform]["metrics"]
        metrics["impressions"] += campaign.impressions or 0
        metrics["clicks"] += campaign.clicks or 0
        metrics["conversions"] += campaign.conversions or 0
        metrics["spend"] += float(campaign.daily_spend or 0) * days
    
    # Calculate averages and ratios
    comparison = {}
    for platform, data in platform_data.items():
        metrics = data["metrics"]
        campaigns_list = data["campaigns"]
        
        avg_roas = sum(c["roas"] for c in campaigns_list) / len(campaigns_list) if campaigns_list else 0
        avg_ctr = sum(c["ctr"] for c in campaigns_list) / len(campaigns_list) if campaigns_list else 0
        avg_cpc = sum(c["cpc"] for c in campaigns_list) / len(campaigns_list) if campaigns_list else 0
        
        comparison[platform] = {
            "platform": platform,
            "total_campaigns": data["total_campaigns"],
            "active_campaigns": data["active_campaigns"],
            "total_impressions": metrics["impressions"],
            "total_clicks": metrics["clicks"],
            "total_conversions": metrics["conversions"],
            "total_spend": metrics["spend"],
            "avg_roas": round(avg_roas, 2),
            "avg_ctr": round(avg_ctr, 4),
            "avg_cpc": round(avg_cpc, 2),
            "efficiency_score": round((avg_roas * avg_ctr) / (avg_cpc + 0.1), 2)  # Combined efficiency metric
        }
    
    # Determine best performing platform
    best_platform = max(comparison.values(), key=lambda x: x["efficiency_score"]) if comparison else None
    
    return {
        "analysis_period": f"{days} days",
        "platforms": list(comparison.values()),
        "best_performing_platform": best_platform["platform"] if best_platform else None,
        "insights": [
            f"Analyzed {sum(p['total_campaigns'] for p in comparison.values())} campaigns across {len(comparison)} platforms",
            f"Best performing platform: {best_platform['platform']}" if best_platform else "No data available"
        ],
        "generated_at": datetime.utcnow().isoformat()
    }

@router.get("/demographics")
async def get_demographic_insights(
    campaign_id: Optional[str] = Query(None, description="Specific campaign ID"),
    platform: Optional[PlatformType] = Query(None, description="Filter by platform"),
    days: int = Query(30, ge=1, le=90, description="Number of days to analyze"),
    session: AsyncSession = Depends(get_session)
):
    """Get demographic performance insights"""
    
    start_date = datetime.utcnow().date() - timedelta(days=days)
    
    # Get campaigns
    if campaign_id:
        campaign = await session.get(Campaign, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
        campaigns = [campaign]
    else:
        query = select(Campaign).where(Campaign.created_at >= start_date)
        if platform:
            query = query.where(Campaign.platform == platform)
        result = await session.execute(query)
        campaigns = result.scalars().all()
    
    # Get metrics with demographics
    demographic_data = {
        "age_performance": {},
        "gender_performance": {},
        "location_performance": {},
        "device_performance": {}
    }
    
    # This would typically query detailed metrics
    # For now, generate sample demographic insights
    
    for campaign in campaigns:
        # Sample age demographics
        age_groups = ["18-24", "25-34", "35-44", "45-54", "55+"]
        for age_group in age_groups:
            if age_group not in demographic_data["age_performance"]:
                demographic_data["age_performance"][age_group] = {
                    "impressions": 0,
                    "clicks": 0,
                    "conversions": 0,
                    "spend": 0.0
                }
            
            # Distribute campaign metrics across age groups
            age_factor = {"18-24": 0.25, "25-34": 0.35, "35-44": 0.25, "45-54": 0.1, "55+": 0.05}[age_group]
            
            demographic_data["age_performance"][age_group]["impressions"] += int((campaign.impressions or 0) * age_factor)
            demographic_data["age_performance"][age_group]["clicks"] += int((campaign.clicks or 0) * age_factor)
            demographic_data["age_performance"][age_group]["conversions"] += int((campaign.conversions or 0) * age_factor)
            demographic_data["age_performance"][age_group]["spend"] += float(campaign.daily_spend or 0) * days * age_factor
    
    # Calculate performance metrics for each demographic
    for age_group, data in demographic_data["age_performance"].items():
        data["ctr"] = (data["clicks"] / data["impressions"]) if data["impressions"] > 0 else 0
        data["cpc"] = (data["spend"] / data["clicks"]) if data["clicks"] > 0 else 0
        data["conversion_rate"] = (data["conversions"] / data["clicks"]) if data["clicks"] > 0 else 0
    
    # Find best performing segments
    best_age_group = max(demographic_data["age_performance"].items(), 
                        key=lambda x: x[1]["conversion_rate"])[0] if demographic_data["age_performance"] else None
    
    return {
        "analysis_period": f"{days} days",
        "campaigns_analyzed": len(campaigns),
        "platform_filter": platform.value if platform else "all",
        "demographic_performance": demographic_data,
        "insights": [
            f"Best performing age group: {best_age_group}" if best_age_group else "No data available",
            f"Analyzed {len(campaigns)} campaigns for demographic insights"
        ],
        "recommendations": [
            f"Consider increasing budget allocation to {best_age_group} age group" if best_age_group else "More data needed for recommendations"
        ],
        "generated_at": datetime.utcnow().isoformat()
    } 