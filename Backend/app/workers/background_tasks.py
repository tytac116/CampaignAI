"""
Background Tasks and Workers

This module provides background task processing for the Campaign Optimization Platform.
Includes metric simulation, scheduled optimization, and data maintenance tasks.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random

from celery import Celery
from ..core.config import get_settings
from ..core.database import get_session
from ..models.campaign import Campaign, CampaignStatus
from ..models.campaign_metrics import CampaignMetrics
from ..agents.coordinator import coordinator
from ..data.data_generator import CampaignDataGenerator

logger = logging.getLogger(__name__)
settings = get_settings()

# Create Celery app
celery_app = Celery(
    "campaign_ai_workers",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['app.workers.background_tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    'simulate-campaign-metrics': {
        'task': 'app.workers.background_tasks.simulate_campaign_metrics',
        'schedule': 300.0,  # Every 5 minutes
    },
    'scheduled-campaign-optimization': {
        'task': 'app.workers.background_tasks.run_scheduled_optimizations',
        'schedule': 3600.0,  # Every hour
    },
    'cleanup-old-data': {
        'task': 'app.workers.background_tasks.cleanup_old_data',
        'schedule': 86400.0,  # Daily
    },
    'update-campaign-performance': {
        'task': 'app.workers.background_tasks.update_campaign_performance',
        'schedule': 900.0,  # Every 15 minutes
    }
}

class MetricSimulator:
    """Simulates real-time campaign metrics updates"""
    
    def __init__(self):
        self.data_generator = CampaignDataGenerator()
    
    async def simulate_hourly_metrics(self, campaign: Campaign) -> Dict[str, Any]:
        """Generate realistic hourly metrics for a campaign"""
        
        # Base metrics on campaign's current performance
        base_impressions = campaign.impressions or 1000
        base_ctr = float(campaign.ctr or 0.02)
        base_cpc = float(campaign.cpc or 2.5)
        base_roas = float(campaign.roas or 3.0)
        
        # Add hourly variation (lower at night, higher during business hours)
        current_hour = datetime.utcnow().hour
        hour_multiplier = self._get_hour_multiplier(current_hour)
        
        # Add random variation
        random_multiplier = random.uniform(0.7, 1.3)
        
        # Calculate hourly metrics
        hourly_impressions = int(base_impressions / 24 * hour_multiplier * random_multiplier)
        hourly_clicks = int(hourly_impressions * base_ctr * random.uniform(0.8, 1.2))
        hourly_conversions = int(hourly_clicks * 0.1 * random.uniform(0.5, 2.0))
        hourly_spend = base_cpc * hourly_clicks * random.uniform(0.9, 1.1)
        
        # Calculate derived metrics
        hourly_ctr = (hourly_clicks / hourly_impressions) if hourly_impressions > 0 else 0
        hourly_cpc = (hourly_spend / hourly_clicks) if hourly_clicks > 0 else 0
        hourly_roas = base_roas * random.uniform(0.8, 1.2)
        
        return {
            "impressions": hourly_impressions,
            "clicks": hourly_clicks,
            "conversions": hourly_conversions,
            "spend": hourly_spend,
            "ctr": hourly_ctr,
            "cpc": hourly_cpc,
            "roas": hourly_roas
        }
    
    def _get_hour_multiplier(self, hour: int) -> float:
        """Get traffic multiplier based on hour of day"""
        # Higher traffic during business hours
        if 9 <= hour <= 17:
            return 1.5
        elif 18 <= hour <= 22:
            return 1.2
        elif 6 <= hour <= 8:
            return 0.8
        else:  # Night hours
            return 0.4
    
    async def update_campaign_cumulative_metrics(self, campaign: Campaign, hourly_metrics: Dict[str, Any]):
        """Update campaign's cumulative metrics"""
        
        campaign.impressions = (campaign.impressions or 0) + hourly_metrics["impressions"]
        campaign.clicks = (campaign.clicks or 0) + hourly_metrics["clicks"]
        campaign.conversions = (campaign.conversions or 0) + hourly_metrics["conversions"]
        
        # Update daily spend
        campaign.daily_spend = (campaign.daily_spend or 0) + hourly_metrics["spend"]
        
        # Recalculate rates
        if campaign.impressions > 0:
            campaign.ctr = campaign.clicks / campaign.impressions
        
        if campaign.clicks > 0:
            campaign.cpc = float(campaign.daily_spend) / campaign.clicks
        
        # ROAS calculation (simplified)
        campaign.roas = hourly_metrics["roas"]
        
        campaign.updated_at = datetime.utcnow()

@celery_app.task(bind=True)
def simulate_campaign_metrics(self):
    """Simulate campaign metrics updates"""
    
    async def _simulate_metrics():
        simulator = MetricSimulator()
        
        async with get_session() as session:
            # Get active campaigns
            campaigns = await session.execute(
                session.query(Campaign).filter(Campaign.status == CampaignStatus.ACTIVE)
            )
            campaigns = campaigns.scalars().all()
            
            logger.info(f"Simulating metrics for {len(campaigns)} active campaigns")
            
            for campaign in campaigns:
                try:
                    # Generate hourly metrics
                    hourly_metrics = await simulator.simulate_hourly_metrics(campaign)
                    
                    # Update campaign cumulative metrics
                    await simulator.update_campaign_cumulative_metrics(campaign, hourly_metrics)
                    
                    # Create or update daily metrics record
                    today = datetime.utcnow().date()
                    
                    # Check if metrics record exists for today
                    existing_metrics = await session.execute(
                        session.query(CampaignMetrics).filter(
                            CampaignMetrics.campaign_id == campaign.id,
                            CampaignMetrics.date == today
                        )
                    )
                    existing_metrics = existing_metrics.scalar_one_or_none()
                    
                    if existing_metrics:
                        # Update existing record
                        existing_metrics.impressions += hourly_metrics["impressions"]
                        existing_metrics.clicks += hourly_metrics["clicks"]
                        existing_metrics.conversions += hourly_metrics["conversions"]
                        existing_metrics.spend += hourly_metrics["spend"]
                        
                        # Recalculate rates
                        if existing_metrics.impressions > 0:
                            existing_metrics.ctr = existing_metrics.clicks / existing_metrics.impressions
                        if existing_metrics.clicks > 0:
                            existing_metrics.cpc = existing_metrics.spend / existing_metrics.clicks
                        
                        existing_metrics.roas = hourly_metrics["roas"]
                        existing_metrics.updated_at = datetime.utcnow()
                        
                    else:
                        # Create new metrics record
                        new_metrics = CampaignMetrics(
                            campaign_id=campaign.id,
                            date=today,
                            impressions=hourly_metrics["impressions"],
                            clicks=hourly_metrics["clicks"],
                            conversions=hourly_metrics["conversions"],
                            spend=hourly_metrics["spend"],
                            ctr=hourly_metrics["ctr"],
                            cpc=hourly_metrics["cpc"],
                            roas=hourly_metrics["roas"],
                            # Add demographic data (simplified)
                            age_demographics={"18-24": 0.3, "25-34": 0.4, "35-44": 0.2, "45+": 0.1},
                            gender_demographics={"male": 0.6, "female": 0.4},
                            location_demographics={"US": 0.7, "CA": 0.15, "UK": 0.1, "Other": 0.05},
                            device_demographics={"mobile": 0.7, "desktop": 0.25, "tablet": 0.05}
                        )
                        session.add(new_metrics)
                    
                    await session.commit()
                    
                except Exception as e:
                    logger.error(f"Failed to simulate metrics for campaign {campaign.id}: {str(e)}")
                    await session.rollback()
            
            logger.info("Completed metrics simulation")
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_simulate_metrics())
    finally:
        loop.close()

@celery_app.task(bind=True)
def run_scheduled_optimizations(self):
    """Run scheduled campaign optimizations"""
    
    async def _run_optimizations():
        async with get_session() as session:
            # Get campaigns that need optimization
            campaigns = await session.execute(
                session.query(Campaign).filter(
                    Campaign.status == CampaignStatus.ACTIVE,
                    Campaign.updated_at < datetime.utcnow() - timedelta(hours=6)  # Not optimized in last 6 hours
                )
            )
            campaigns = campaigns.scalars().all()
            
            logger.info(f"Running scheduled optimizations for {len(campaigns)} campaigns")
            
            # Schedule optimization for campaigns that might need it
            campaign_ids = []
            for campaign in campaigns:
                # Check if campaign needs optimization
                needs_optimization = False
                
                if campaign.roas and campaign.roas < 2.0:
                    needs_optimization = True
                elif campaign.ctr and campaign.ctr < 0.01:
                    needs_optimization = True
                elif campaign.cpc and campaign.cpc > 5.0:
                    needs_optimization = True
                elif campaign.daily_spend and campaign.budget and campaign.daily_spend > campaign.budget * 0.9:
                    needs_optimization = True
                
                if needs_optimization:
                    campaign_ids.append(campaign.id)
            
            if campaign_ids:
                await coordinator.schedule_campaign_monitoring(campaign_ids)
                logger.info(f"Scheduled optimization for {len(campaign_ids)} campaigns")
            
            # Process task queue
            await coordinator.process_task_queue()
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_run_optimizations())
    finally:
        loop.close()

@celery_app.task(bind=True)
def cleanup_old_data(self):
    """Clean up old data and metrics"""
    
    async def _cleanup():
        async with get_session() as session:
            # Remove metrics older than 90 days
            cutoff_date = datetime.utcnow().date() - timedelta(days=90)
            
            old_metrics = await session.execute(
                session.query(CampaignMetrics).filter(CampaignMetrics.date < cutoff_date)
            )
            old_metrics = old_metrics.scalars().all()
            
            for metric in old_metrics:
                await session.delete(metric)
            
            await session.commit()
            
            logger.info(f"Cleaned up {len(old_metrics)} old metric records")
            
            # Clean up completed workflows older than 7 days
            # This would typically clean up workflow state data
            logger.info("Completed data cleanup")
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_cleanup())
    finally:
        loop.close()

@celery_app.task(bind=True)
def update_campaign_performance(self):
    """Update campaign performance scores and flags"""
    
    async def _update_performance():
        async with get_session() as session:
            # Get all active campaigns
            campaigns = await session.execute(
                session.query(Campaign).filter(Campaign.status == CampaignStatus.ACTIVE)
            )
            campaigns = campaigns.scalars().all()
            
            logger.info(f"Updating performance scores for {len(campaigns)} campaigns")
            
            for campaign in campaigns:
                try:
                    # Calculate performance score
                    performance_score = 0
                    
                    # ROAS scoring (40% weight)
                    if campaign.roas:
                        if campaign.roas >= 4.0:
                            performance_score += 40
                        elif campaign.roas >= 3.0:
                            performance_score += 30
                        elif campaign.roas >= 2.0:
                            performance_score += 20
                        else:
                            performance_score += 10
                    
                    # CTR scoring (30% weight)
                    if campaign.ctr:
                        if campaign.ctr >= 0.03:
                            performance_score += 30
                        elif campaign.ctr >= 0.02:
                            performance_score += 25
                        elif campaign.ctr >= 0.01:
                            performance_score += 15
                        else:
                            performance_score += 5
                    
                    # CPC scoring (20% weight) - lower is better
                    if campaign.cpc:
                        if campaign.cpc <= 1.0:
                            performance_score += 20
                        elif campaign.cpc <= 2.0:
                            performance_score += 15
                        elif campaign.cpc <= 3.0:
                            performance_score += 10
                        else:
                            performance_score += 5
                    
                    # Budget utilization (10% weight)
                    if campaign.daily_spend and campaign.budget:
                        utilization = campaign.daily_spend / campaign.budget
                        if 0.7 <= utilization <= 0.9:
                            performance_score += 10
                        elif 0.5 <= utilization <= 1.0:
                            performance_score += 8
                        else:
                            performance_score += 3
                    
                    # Update campaign flags
                    if performance_score >= 80:
                        campaign.requires_optimization = False
                        campaign.is_high_performer = True
                    elif performance_score <= 40:
                        campaign.requires_optimization = True
                        campaign.is_high_performer = False
                    else:
                        campaign.is_high_performer = False
                    
                    campaign.updated_at = datetime.utcnow()
                    
                except Exception as e:
                    logger.error(f"Failed to update performance for campaign {campaign.id}: {str(e)}")
            
            await session.commit()
            logger.info("Completed performance updates")
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_update_performance())
    finally:
        loop.close()

# Custom task for manual optimization trigger
@celery_app.task(bind=True)
def trigger_campaign_optimization(self, campaign_id: str, priority: str = "medium"):
    """Manually trigger optimization for a specific campaign"""
    
    async def _trigger_optimization():
        from ..agents.state import Priority
        
        priority_map = {
            "low": Priority.LOW,
            "medium": Priority.MEDIUM,
            "high": Priority.HIGH
        }
        
        try:
            workflow_id = await coordinator.start_campaign_optimization_workflow(
                campaign_id=campaign_id,
                trigger_reason="manual_api_trigger",
                priority=priority_map.get(priority, Priority.MEDIUM)
            )
            
            logger.info(f"Triggered optimization workflow {workflow_id} for campaign {campaign_id}")
            return {"workflow_id": workflow_id, "status": "started"}
            
        except Exception as e:
            logger.error(f"Failed to trigger optimization for campaign {campaign_id}: {str(e)}")
            raise
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_trigger_optimization())
    finally:
        loop.close()

# Utility functions for task management
def get_task_status(task_id: str):
    """Get status of a Celery task"""
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
        "traceback": result.traceback if result.failed() else None
    }

def get_active_tasks():
    """Get list of active tasks"""
    inspect = celery_app.control.inspect()
    active_tasks = inspect.active()
    return active_tasks

def cancel_task(task_id: str):
    """Cancel a running task"""
    celery_app.control.revoke(task_id, terminate=True)
    return {"task_id": task_id, "status": "cancelled"}

# Background task scheduler
class BackgroundTaskScheduler:
    """Manages background task scheduling and monitoring"""
    
    def __init__(self):
        self.running_tasks = {}
    
    def schedule_metric_simulation(self):
        """Schedule metric simulation task"""
        task = simulate_campaign_metrics.delay()
        self.running_tasks[task.id] = {
            "task_type": "metric_simulation",
            "started_at": datetime.utcnow(),
            "task_id": task.id
        }
        return task.id
    
    def schedule_optimization(self, campaign_id: str, priority: str = "medium"):
        """Schedule campaign optimization"""
        task = trigger_campaign_optimization.delay(campaign_id, priority)
        self.running_tasks[task.id] = {
            "task_type": "optimization",
            "campaign_id": campaign_id,
            "started_at": datetime.utcnow(),
            "task_id": task.id
        }
        return task.id
    
    def get_task_info(self, task_id: str):
        """Get information about a scheduled task"""
        task_info = self.running_tasks.get(task_id)
        if task_info:
            status = get_task_status(task_id)
            task_info.update(status)
        return task_info
    
    def cleanup_completed_tasks(self):
        """Clean up completed task records"""
        completed_tasks = []
        for task_id, task_info in self.running_tasks.items():
            status = get_task_status(task_id)
            if status["status"] in ["SUCCESS", "FAILURE", "REVOKED"]:
                completed_tasks.append(task_id)
        
        for task_id in completed_tasks:
            del self.running_tasks[task_id]
        
        return len(completed_tasks)

# Global scheduler instance
task_scheduler = BackgroundTaskScheduler() 