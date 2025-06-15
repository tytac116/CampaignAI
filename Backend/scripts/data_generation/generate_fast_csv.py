"""
Generate realistic campaign data FAST with minimal AI calls.
Uses AI for a few samples then intelligent fallbacks for speed.
Includes LangSmith tracing for token monitoring and numeric primary IDs for Supabase.
"""

import csv
import json
import os
import time
from datetime import datetime
from pathlib import Path
import shutil

# LangSmith tracing setup (optional)
HAS_LANGSMITH = False
try:
    from langsmith import traceable
    import langsmith
    
    # Initialize LangSmith if API key is available
    if os.getenv("LANGCHAIN_API_KEY"):
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "CampaignAI-DataGeneration"
        HAS_LANGSMITH = True
        print("✅ LangSmith tracing enabled")
    else:
        print("⚠️  LangSmith API key not found - tracing disabled")
        # Create dummy decorator if LangSmith not available
        def traceable(name=None):
            def decorator(func):
                return func
            return decorator
        
except ImportError:
    print("⚠️  LangSmith not installed - tracing disabled")
    # Create dummy decorator if LangSmith not available
    def traceable(name=None):
        def decorator(func):
            return func
        return decorator

# Import our AI data generator
from app.data.ai_data_generator import (
    get_ai_generated_campaigns,
    generate_smart_fallback_audience_creative,
    generate_realistic_kpis,
    generate_campaign_settings,
    generate_campaign_metrics,
    generate_agent_executions,
    fake
)
import random

def clean_csv_directory():
    """Clean up existing CSV files."""
    csv_dir = Path("csv_data")
    if csv_dir.exists():
        print("🧹 Cleaning up existing CSV files...")
        shutil.rmtree(csv_dir)
    
    csv_dir.mkdir(exist_ok=True)
    print("✅ CSV directory ready")

def serialize_for_csv(obj):
    """Convert complex objects to JSON strings for CSV storage."""
    if isinstance(obj, (dict, list)):
        return json.dumps(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, bool):
        return str(obj).lower()
    elif obj is None:
        return ""
    else:
        return str(obj)

def generate_campaigns_csv(campaigns_data, filename="campaigns.csv"):
    """Generate campaigns CSV file with numeric primary ID."""
    
    fieldnames = [
        "id", "campaign_id", "name", "platform", "status", "objective", "campaign_type",
        "budget_type", "budget_amount", "spend_amount", "remaining_budget",
        "impressions", "clicks", "conversions", "revenue", 
        "ctr", "cpc", "cpm", "cpa", "roas",
        "is_optimized", "optimization_score",
        "target_audience", "ad_creative", "campaign_settings",
        "start_date", "end_date", "created_at", "updated_at"
    ]
    
    with open(f"csv_data/{filename}", 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for idx, campaign in enumerate(campaigns_data, 1):
            row = {"id": idx}  # Add numeric primary ID
            for field in fieldnames[1:]:  # Skip 'id' since we just added it
                value = campaign.get(field)
                row[field] = serialize_for_csv(value)
            
            writer.writerow(row)

@traceable(name="generate_campaigns_batch")
def generate_campaigns_fast(platform: str, count: int, start_idx: int = 0) -> list:
    """Generate campaigns quickly using minimal AI + smart fallbacks."""
    
    campaigns = []
    
    # Generate a small sample with AI (only first 25 campaigns)
    if start_idx < 25:
        ai_count = min(25 - start_idx, count)
        print(f"  🤖 Using AI for {ai_count} {platform} campaigns...")
        ai_campaigns = get_ai_generated_campaigns(platform, ai_count)
    else:
        ai_campaigns = []
    
    # Campaign types based on platform
    campaign_types = {
        "facebook": ["video_ad", "image_post", "carousel_post", "webinar_promo", "case_study_post", "testimonial_video", "demo_video", "infographic_post", "live_stream"],
        "instagram": ["image_post", "story_ad", "reel_video", "carousel_post", "video_ad", "infographic_post", "testimonial_video", "demo_video"]
    }
    
    # Use fallback templates for the rest
    fallback_templates = [
        {"name": "AI Marketing Revolution", "objective": "brand_awareness", "target_business": "small businesses"},
        {"name": "Smart Campaign Optimization", "objective": "conversions", "target_business": "e-commerce stores"},
        {"name": "Automated Lead Generation", "objective": "lead_generation", "target_business": "marketing agencies"},
        {"name": "AI-Powered Growth Hacking", "objective": "traffic", "target_business": "startups"},
        {"name": "Intelligent Audience Targeting", "objective": "reach", "target_business": "retail businesses"},
        {"name": "Predictive Analytics Demo", "objective": "engagement", "target_business": "traditional businesses"},
        {"name": "ROI Optimization Suite", "objective": "conversions", "target_business": "digital agencies"},
        {"name": "South African AI Solutions", "objective": "brand_awareness", "target_business": "local businesses"},
        {"name": "Campaign Performance Boost", "objective": "traffic", "target_business": "service providers"},
        {"name": "AI Chatbot Integration", "objective": "lead_generation", "target_business": "customer service"}
    ]
    
    for i in range(count):
        if i < len(ai_campaigns):
            # Use AI-generated campaign
            base_campaign = ai_campaigns[i]
        else:
            # Use fallback template with variations
            template = fallback_templates[i % len(fallback_templates)]
            base_campaign = {
                "name": f"{template['name']} - {platform.title()} #{start_idx + i + 1}",
                "objective": template["objective"],
                "description": f"Advanced AI marketing solutions for {template['target_business']} in South Africa",
                "target_business": template["target_business"],
                "campaign_type": random.choice(campaign_types[platform])
            }
        
        # Generate audience and creative (fast fallback)
        audience_creative = generate_smart_fallback_audience_creative(
            base_campaign["target_business"], 
            platform
        )
        
        # Generate financial data
        budget_amount = random.uniform(500 if platform == "facebook" else 300, 
                                     15000 if platform == "facebook" else 12000)
        spend_amount = budget_amount * random.uniform(0.3, 0.95)
        
        # Generate KPIs
        kpis = generate_realistic_kpis(spend_amount, platform, base_campaign["objective"])
        
        campaign = {
            "campaign_id": f"{'fb' if platform == 'facebook' else 'ig'}_camp_{start_idx + i + 1:04d}",
            "name": base_campaign["name"][:60],
            "platform": platform,
            "status": random.choices(["active", "paused", "completed"], weights=[70, 20, 10])[0],
            "objective": base_campaign["objective"],
            "campaign_type": base_campaign.get("campaign_type", random.choice(campaign_types[platform])),
            "budget_type": "daily",
            "budget_amount": round(budget_amount, 2),
            "spend_amount": round(spend_amount, 2),
            "remaining_budget": round(budget_amount - spend_amount, 2),
            "impressions": kpis["impressions"],
            "clicks": kpis["clicks"],
            "conversions": kpis["conversions"],
            "revenue": kpis["revenue"],
            "ctr": kpis["ctr"],
            "cpc": kpis["cpc"],
            "cpm": kpis["cpm"],
            "cpa": round(spend_amount / kpis["conversions"], 2) if kpis["conversions"] > 0 else 0,
            "roas": kpis["roas"],
            "is_optimized": random.choice([True, False]),
            "optimization_score": random.uniform(0.5, 0.95),
            "target_audience": audience_creative["target_audience"],
            "ad_creative": audience_creative["ad_creative"],
            "campaign_settings": generate_campaign_settings(platform, base_campaign["objective"]),
            "start_date": fake.date_between(start_date="-90d", end_date="-7d"),
            "end_date": fake.date_between(start_date="+7d", end_date="+60d") if random.choice([True, False]) else None,
            "created_at": fake.date_time_between(start_date="-100d", end_date="-90d"),
            "updated_at": fake.date_time_between(start_date="-7d", end_date="now")
        }
        campaigns.append(campaign)
    
    return campaigns

@traceable(name="generate_full_dataset")
def main():
    """Generate all CSV files FAST with minimal AI calls and LangSmith tracing."""
    
    print("🚀 Starting FAST AI-powered data generation for CampaignAI...")
    print("⚡ This optimized version uses minimal AI calls for maximum speed!")
    if HAS_LANGSMITH:
        print("📊 LangSmith tracing enabled for token monitoring")
    else:
        print("📊 LangSmith tracing disabled (API key not configured)")
    print("🔢 Numeric primary IDs added for Supabase compatibility")
    print("=" * 60)
    
    start_time = time.time()
    
    # Clean up existing files
    clean_csv_directory()
    
    all_campaigns = []
    
    try:
        # Generate Facebook campaigns
        facebook_count = 250
        print(f"\n📘 Generating {facebook_count} Facebook campaigns...")
        
        batch_size = 100  # Large batches for speed
        facebook_batches = (facebook_count + batch_size - 1) // batch_size
        
        for batch_num in range(facebook_batches):
            start_idx = batch_num * batch_size
            end_idx = min((batch_num + 1) * batch_size, facebook_count)
            current_batch_size = end_idx - start_idx
            
            elapsed = time.time() - start_time
            if batch_num > 0:
                estimated_total = elapsed * facebook_batches / batch_num
                remaining = estimated_total - elapsed
                print(f"🔄 Facebook batch {batch_num + 1}/{facebook_batches} - ETA: {remaining:.0f}s")
            else:
                print(f"🔄 Facebook batch {batch_num + 1}/{facebook_batches}")
            
            batch_campaigns = generate_campaigns_fast("facebook", current_batch_size, start_idx)
            all_campaigns.extend(batch_campaigns)
            
            print(f"  ✅ Generated {len(batch_campaigns)} campaigns (Total: {len(all_campaigns)})")
        
        # Generate Instagram campaigns
        instagram_count = 250
        print(f"\n📷 Generating {instagram_count} Instagram campaigns...")
        
        instagram_batches = (instagram_count + batch_size - 1) // batch_size
        
        for batch_num in range(instagram_batches):
            start_idx = batch_num * batch_size
            end_idx = min((batch_num + 1) * batch_size, instagram_count)
            current_batch_size = end_idx - start_idx
            
            elapsed = time.time() - start_time
            print(f"🔄 Instagram batch {batch_num + 1}/{instagram_batches}")
            
            batch_campaigns = generate_campaigns_fast("instagram", current_batch_size, start_idx)
            all_campaigns.extend(batch_campaigns)
            
            print(f"  ✅ Generated {len(batch_campaigns)} campaigns (Total: {len(all_campaigns)})")
        
        print(f"\n💾 Saving campaigns to CSV...")
        generate_campaigns_csv(all_campaigns, "campaigns.csv")
        
        # Generate metrics quickly
        print(f"\n📈 Generating campaign metrics...")
        metrics_campaigns = all_campaigns[:100]  # Limit for speed
        all_metrics = []
        
        for idx, campaign in enumerate(metrics_campaigns):
            if (idx + 1) % 25 == 0:
                print(f"  🔄 Metrics progress: {idx + 1}/100 campaigns")
            
            campaign_metrics = generate_campaign_metrics(campaign, days=30)
            all_metrics.extend(campaign_metrics)
        
        # Save metrics with numeric primary ID
        fieldnames = [
            "id", "campaign_id", "metric_date", "hour_of_day",
            "impressions", "clicks", "conversions", "spend", "revenue",
            "likes", "shares", "comments", "saves", "video_views",
            "demographics", "geo_data", "device_data",
            "relevance_score", "quality_score", "engagement_rate",
            "performance_index", "efficiency_index",
            "created_at", "updated_at"
        ]
        
        with open("csv_data/campaign_metrics.csv", 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for idx, metric in enumerate(all_metrics, 1):
                row = {"id": idx}  # Add numeric primary ID
                for field in fieldnames[1:]:  # Skip 'id' since we just added it
                    value = metric.get(field)
                    row[field] = serialize_for_csv(value)
                writer.writerow(row)
        
        # Generate agent executions
        print(f"\n🤖 Generating agent executions...")
        agent_executions = generate_agent_executions(50)
        
        # Save agent executions with numeric primary ID
        fieldnames = [
            "id", "execution_id", "workflow_type", "status", "execution_time_seconds",
            "input_data", "output_data", "error_details",
            "created_at", "completed_at"
        ]
        
        with open("csv_data/agent_executions.csv", 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for idx, execution in enumerate(agent_executions, 1):
                row = {"id": idx}  # Add numeric primary ID
                for field in fieldnames[1:]:  # Skip 'id' since we just added it
                    value = execution.get(field)
                    row[field] = serialize_for_csv(value)
                writer.writerow(row)
        
        total_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("🎉 FAST CSV data generation completed!")
        print(f"⚡ Total time: {total_time:.1f} seconds")
        if HAS_LANGSMITH:
            print("📊 Check LangSmith dashboard for token usage details")
        else:
            print("📊 LangSmith tracing was disabled - no token monitoring available")
        print("\nGenerated files:")
        print("  📁 csv_data/")
        print("    📊 campaigns.csv (with numeric primary IDs)")
        print("    📈 campaign_metrics.csv (with numeric primary IDs)")
        print("    🤖 agent_executions.csv (with numeric primary IDs)")
        
        # Show file sizes
        csv_dir = Path("csv_data")
        total_size = 0
        for csv_file in csv_dir.glob("*.csv"):
            size = csv_file.stat().st_size
            total_size += size
            print(f"   📄 {csv_file.name}: {size/1024:.1f} KB")
        
        print(f"\n💾 Total size: {total_size/1024:.1f} KB")
        print(f"🚀 Speed: {len(all_campaigns)/(total_time/60):.0f} campaigns/minute")
        print("✨ Ready for upload to Supabase!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation interrupted by user!")
        total_time = time.time() - start_time
        print(f"⏱️  Ran for {total_time:.1f} seconds")
        print("📁 Check csv_data/ directory for any partial data")
        
    except Exception as e:
        print(f"\n\n❌ Error during generation: {e}")
        raise

if __name__ == "__main__":
    main() 