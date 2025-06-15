import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from ..core.database import async_session_factory
from ..models.campaign import Campaign
from ..models.campaign_metrics import CampaignMetrics
from .data_generator import generate_realistic_data
from rich.console import Console
from rich.progress import Progress, TaskID

console = Console()


class DataSeeder:
    """
    Seeds the database with realistic campaign data.
    """
    
    def __init__(self):
        self.session_factory = async_session_factory
    
    async def clear_existing_data(self, session: AsyncSession) -> None:
        """Clear all existing data from the database."""
        console.print("[yellow]Clearing existing data...[/yellow]")
        
        # Delete in correct order due to foreign key constraints
        await session.execute(delete(CampaignMetrics))
        await session.execute(delete(Campaign))
        await session.commit()
        
        console.print("[green]✓ Existing data cleared[/green]")
    
    async def seed_campaigns(self, session: AsyncSession, campaigns_data: List[Dict[str, Any]], 
                           demographics_data: List[Dict[str, Any]], task_id: TaskID, 
                           progress: Progress) -> List[int]:
        """Seed campaigns into the database."""
        campaign_ids = []
        
        for i, (campaign_data, demographics) in enumerate(zip(campaigns_data, demographics_data)):
            # Create campaign instance
            campaign = Campaign(
                name=campaign_data["name"],
                platform=campaign_data["platform"],
                status=campaign_data["status"],
                budget=campaign_data["budget"],
                daily_budget=campaign_data["daily_budget"],
                spend=campaign_data["spend"],
                objective=campaign_data["objective"],
                target_audience=campaign_data["target_audience"],
                ad_creative=campaign_data["ad_creative"],
                campaign_settings=campaign_data["campaign_settings"],
                impressions=campaign_data["impressions"],
                clicks=campaign_data["clicks"],
                conversions=campaign_data["conversions"],
                revenue=campaign_data["revenue"],
                cpm=campaign_data["cpm"],
                cpc=campaign_data["cpc"],
                ctr=campaign_data["ctr"],
                conversion_rate=campaign_data["conversion_rate"],
                roas=campaign_data["roas"],
                is_optimized=campaign_data["is_optimized"],
                optimization_score=campaign_data["optimization_score"],
                start_date=datetime.combine(campaign_data["start_date"], datetime.min.time()),
                end_date=datetime.combine(campaign_data["end_date"], datetime.min.time()),
            )
            
            session.add(campaign)
            await session.flush()  # Get the ID
            campaign_ids.append(campaign.id)
            
            # Update progress
            progress.update(task_id, advance=1)
            
            # Commit in batches for better performance
            if (i + 1) % 50 == 0:
                await session.commit()
        
        # Final commit
        await session.commit()
        return campaign_ids
    
    async def seed_metrics(self, session: AsyncSession, metrics_data: List[Dict[str, Any]], 
                         task_id: TaskID, progress: Progress) -> None:
        """Seed campaign metrics into the database."""
        metrics_objects = []
        
        for i, metric_data in enumerate(metrics_data):
            # Create metrics instance
            metric = CampaignMetrics(
                campaign_id=metric_data["campaign_id"],
                date=metric_data["date"],
                hour=metric_data["hour"],
                impressions=metric_data["impressions"],
                clicks=metric_data["clicks"],
                conversions=metric_data["conversions"],
                spend=metric_data["spend"],
                revenue=metric_data["revenue"],
                likes=metric_data["likes"],
                shares=metric_data["shares"],
                comments=metric_data["comments"],
                saves=metric_data["saves"],
                video_views=metric_data["video_views"],
                video_completion_rate=metric_data["video_completion_rate"],
                cpm=metric_data["cpm"],
                cpc=metric_data["cpc"],
                ctr=metric_data["ctr"],
                conversion_rate=metric_data["conversion_rate"],
                cost_per_conversion=metric_data["cost_per_conversion"],
                roas=metric_data["roas"],
                frequency=metric_data["frequency"],
                reach=metric_data["reach"],
                performance_score=metric_data["performance_score"],
                trend_direction=metric_data["trend_direction"],
                quality_score=metric_data["quality_score"],
                relevance_score=metric_data["relevance_score"],
            )
            
            metrics_objects.append(metric)
            
            # Update progress
            progress.update(task_id, advance=1)
            
            # Bulk insert in batches for better performance
            if len(metrics_objects) >= 100:
                session.add_all(metrics_objects)
                await session.commit()
                metrics_objects = []
        
        # Insert remaining metrics
        if metrics_objects:
            session.add_all(metrics_objects)
            await session.commit()
    
    async def seed_database(self, facebook_count: int = 500, instagram_count: int = 500, 
                          clear_existing: bool = True) -> None:
        """
        Main seeding function.
        
        Args:
            facebook_count: Number of Facebook campaigns to generate
            instagram_count: Number of Instagram campaigns to generate
            clear_existing: Whether to clear existing data first
        """
        console.print(f"[blue]Starting database seeding...[/blue]")
        console.print(f"[blue]Generating {facebook_count} Facebook and {instagram_count} Instagram campaigns[/blue]")
        
        # Generate data
        console.print("[yellow]Generating realistic campaign data...[/yellow]")
        data = generate_realistic_data(facebook_count, instagram_count)
        
        campaigns_data = data["campaigns"]
        demographics_data = data["demographics"]
        metrics_data = data["metrics"]
        
        console.print(f"[green]✓ Generated {len(campaigns_data)} campaigns with {len(metrics_data)} metric records[/green]")
        
        # Seed database
        async with self.session_factory() as session:
            if clear_existing:
                await self.clear_existing_data(session)
            
            with Progress() as progress:
                # Seed campaigns
                campaigns_task = progress.add_task(
                    "[green]Seeding campaigns...", 
                    total=len(campaigns_data)
                )
                
                campaign_ids = await self.seed_campaigns(
                    session, campaigns_data, demographics_data, campaigns_task, progress
                )
                
                console.print(f"[green]✓ Seeded {len(campaign_ids)} campaigns[/green]")
                
                # Update campaign_ids in metrics data
                for metric in metrics_data:
                    if metric["campaign_id"] <= len(campaign_ids):
                        metric["campaign_id"] = campaign_ids[metric["campaign_id"] - 1]
                
                # Seed metrics
                if metrics_data:
                    metrics_task = progress.add_task(
                        "[blue]Seeding metrics...", 
                        total=len(metrics_data)
                    )
                    
                    await self.seed_metrics(session, metrics_data, metrics_task, progress)
                    console.print(f"[green]✓ Seeded {len(metrics_data)} metric records[/green]")
        
        console.print("[bold green]Database seeding completed successfully! 🎉[/bold green]")
        
        # Print summary
        console.print("\n[bold blue]Summary:[/bold blue]")
        console.print(f"• Total campaigns: {len(campaigns_data)}")
        console.print(f"• Facebook campaigns: {facebook_count}")
        console.print(f"• Instagram campaigns: {instagram_count}")
        console.print(f"• Total metrics records: {len(metrics_data)}")


async def seed_data_cli():
    """CLI function to seed data."""
    seeder = DataSeeder()
    await seeder.seed_database()


if __name__ == "__main__":
    asyncio.run(seed_data_cli()) 