#!/usr/bin/env python3
"""
Create Sample Campaign Data

This script creates sample campaign data in the Supabase database
for testing the frontend integration.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add Backend directory to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

from app.services.supabase_service import supabase_service

def create_sample_campaigns():
    """Create sample campaign data."""
    print("🚀 Creating sample campaign data...")
    
    client = supabase_service.get_client()
    if not client:
        print("❌ Failed to connect to Supabase")
        return False
    
    # Sample campaigns data
    sample_campaigns = [
        {
            "campaign_id": "facebook_summer_sale_2024",
            "name": "Summer Sale 2024",
            "platform": "facebook",
            "status": "active",
            "objective": "conversions",
            "budget_type": "daily",
            "budget_amount": 150.00,
            "spend_amount": 89.45,
            "remaining_budget": 60.55,
            "impressions": 12450,
            "clicks": 234,
            "conversions": 18,
            "revenue": 1250.00,
            "ctr": 0.0188,
            "cpc": 0.38,
            "cpm": 7.18,
            "cpa": 4.97,
            "roas": 13.97,
            "is_optimized": True,
            "optimization_score": 8.5,
            "target_audience": {
                "age_range": "25-45",
                "interests": ["fashion", "shopping", "lifestyle"],
                "location": "United States"
            },
            "ad_creative": {
                "headline": "Summer Sale - Up to 50% Off!",
                "description": "Don't miss our biggest sale of the year",
                "image_url": "https://example.com/summer-sale.jpg"
            },
            "campaign_settings": {
                "bid_strategy": "lowest_cost",
                "optimization_goal": "conversions"
            },
            "start_date": (datetime.now() - timedelta(days=15)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=15)).isoformat(),
            "created_at": (datetime.now() - timedelta(days=20)).isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "campaign_id": "instagram_brand_awareness_q2",
            "name": "Brand Awareness Q2",
            "platform": "instagram",
            "status": "active",
            "objective": "brand_awareness",
            "budget_type": "daily",
            "budget_amount": 75.00,
            "spend_amount": 52.30,
            "remaining_budget": 22.70,
            "impressions": 8920,
            "clicks": 156,
            "conversions": 8,
            "revenue": 420.00,
            "ctr": 0.0175,
            "cpc": 0.34,
            "cpm": 5.86,
            "cpa": 6.54,
            "roas": 8.03,
            "is_optimized": False,
            "optimization_score": 6.2,
            "target_audience": {
                "age_range": "18-35",
                "interests": ["technology", "innovation", "startups"],
                "location": "North America"
            },
            "ad_creative": {
                "headline": "Discover Innovation",
                "description": "Join the future of technology",
                "image_url": "https://example.com/brand-awareness.jpg"
            },
            "campaign_settings": {
                "bid_strategy": "lowest_cost",
                "optimization_goal": "impressions"
            },
            "start_date": (datetime.now() - timedelta(days=10)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=20)).isoformat(),
            "created_at": (datetime.now() - timedelta(days=12)).isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "campaign_id": "facebook_retargeting_spring",
            "name": "Spring Retargeting Campaign",
            "platform": "facebook",
            "status": "paused",
            "objective": "conversions",
            "budget_type": "lifetime",
            "budget_amount": 500.00,
            "spend_amount": 387.92,
            "remaining_budget": 112.08,
            "impressions": 15680,
            "clicks": 298,
            "conversions": 24,
            "revenue": 1890.00,
            "ctr": 0.0190,
            "cpc": 1.30,
            "cpm": 24.73,
            "cpa": 16.16,
            "roas": 4.87,
            "is_optimized": True,
            "optimization_score": 7.8,
            "target_audience": {
                "age_range": "25-55",
                "interests": ["previous_customers", "website_visitors"],
                "location": "United States, Canada"
            },
            "ad_creative": {
                "headline": "Come Back for More!",
                "description": "Special offer for returning customers",
                "image_url": "https://example.com/retargeting.jpg"
            },
            "campaign_settings": {
                "bid_strategy": "cost_cap",
                "optimization_goal": "conversions"
            },
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=5)).isoformat(),
            "created_at": (datetime.now() - timedelta(days=35)).isoformat(),
            "updated_at": (datetime.now() - timedelta(days=2)).isoformat()
        },
        {
            "campaign_id": "instagram_product_launch_2024",
            "name": "New Product Launch 2024",
            "platform": "instagram",
            "status": "draft",
            "objective": "traffic",
            "budget_type": "daily",
            "budget_amount": 200.00,
            "spend_amount": 0.00,
            "remaining_budget": 200.00,
            "impressions": 0,
            "clicks": 0,
            "conversions": 0,
            "revenue": 0.00,
            "ctr": 0.0,
            "cpc": 0.0,
            "cpm": 0.0,
            "cpa": 0.0,
            "roas": 0.0,
            "is_optimized": False,
            "optimization_score": 0.0,
            "target_audience": {
                "age_range": "22-40",
                "interests": ["product_category", "early_adopters"],
                "location": "Global"
            },
            "ad_creative": {
                "headline": "Revolutionary New Product",
                "description": "Be the first to experience innovation",
                "image_url": "https://example.com/product-launch.jpg"
            },
            "campaign_settings": {
                "bid_strategy": "lowest_cost",
                "optimization_goal": "link_clicks"
            },
            "start_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=37)).isoformat(),
            "created_at": (datetime.now() - timedelta(days=3)).isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "campaign_id": "facebook_holiday_promo_2024",
            "name": "Holiday Promotion 2024",
            "platform": "facebook",
            "status": "completed",
            "objective": "conversions",
            "budget_type": "lifetime",
            "budget_amount": 1000.00,
            "spend_amount": 987.65,
            "remaining_budget": 12.35,
            "impressions": 45230,
            "clicks": 892,
            "conversions": 67,
            "revenue": 4250.00,
            "ctr": 0.0197,
            "cpc": 1.11,
            "cpm": 21.84,
            "cpa": 14.74,
            "roas": 4.30,
            "is_optimized": True,
            "optimization_score": 9.1,
            "target_audience": {
                "age_range": "25-65",
                "interests": ["holidays", "gift_shopping", "family"],
                "location": "United States"
            },
            "ad_creative": {
                "headline": "Perfect Holiday Gifts",
                "description": "Make this holiday season special",
                "image_url": "https://example.com/holiday-promo.jpg"
            },
            "campaign_settings": {
                "bid_strategy": "lowest_cost",
                "optimization_goal": "conversions"
            },
            "start_date": (datetime.now() - timedelta(days=60)).isoformat(),
            "end_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "created_at": (datetime.now() - timedelta(days=65)).isoformat(),
            "updated_at": (datetime.now() - timedelta(days=30)).isoformat()
        }
    ]
    
    try:
        # Insert sample campaigns
        for campaign in sample_campaigns:
            print(f"📝 Creating campaign: {campaign['name']}")
            
            # Check if campaign already exists
            existing = client.table("campaigns").select("campaign_id").eq("campaign_id", campaign["campaign_id"]).execute()
            
            if existing.data:
                print(f"   ⚠️  Campaign {campaign['campaign_id']} already exists, updating...")
                result = client.table("campaigns").update(campaign).eq("campaign_id", campaign["campaign_id"]).execute()
            else:
                print(f"   ✅ Creating new campaign {campaign['campaign_id']}")
                result = client.table("campaigns").insert(campaign).execute()
            
            if result.data:
                print(f"   ✅ Successfully processed campaign: {campaign['name']}")
            else:
                print(f"   ❌ Failed to process campaign: {campaign['name']}")
        
        print("\n🎉 Sample campaign data creation completed!")
        print(f"📊 Created/updated {len(sample_campaigns)} campaigns")
        
        # Display summary
        all_campaigns = client.table("campaigns").select("*").execute()
        if all_campaigns.data:
            total_campaigns = len(all_campaigns.data)
            active_campaigns = len([c for c in all_campaigns.data if c.get('status') == 'active'])
            total_spend = sum(c.get('spend_amount', 0) for c in all_campaigns.data)
            total_revenue = sum(c.get('revenue', 0) for c in all_campaigns.data)
            
            print("\n📈 Database Summary:")
            print(f"   Total Campaigns: {total_campaigns}")
            print(f"   Active Campaigns: {active_campaigns}")
            print(f"   Total Spend: ${total_spend:.2f}")
            print(f"   Total Revenue: ${total_revenue:.2f}")
            print(f"   Overall ROAS: {total_revenue/total_spend:.2f}x" if total_spend > 0 else "   Overall ROAS: N/A")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("🎯 Campaign AI - Sample Data Creator")
    print("=" * 60)
    
    success = create_sample_campaigns()
    
    if success:
        print("\n✅ Sample data creation completed successfully!")
        print("🚀 You can now start the Campaign AI system and see real data in the frontend.")
    else:
        print("\n❌ Sample data creation failed!")
        print("🔧 Please check your Supabase connection and try again.")

if __name__ == "__main__":
    main() 