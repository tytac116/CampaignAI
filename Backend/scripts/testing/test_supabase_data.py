#!/usr/bin/env python3

"""
Test script to verify uploaded data in Supabase and test API simulators.
"""

import asyncio
import json
from dotenv import load_dotenv
from app.services.supabase_service import supabase_service
from app.services.facebook_api_sim import FacebookAPISimulator
from app.services.instagram_api_sim import InstagramAPISimulator

# Load environment variables
load_dotenv()

def test_database_tables():
    """Test that data was uploaded correctly to Supabase."""
    print("🚀 Testing Supabase data upload...")
    
    # Test connection
    print("\n📡 Testing Supabase connection...")
    client = supabase_service.get_client()
    if not client:
        print("❌ Failed to connect to Supabase")
        return False
    print("✅ Connected to Supabase successfully")
    
    # Test each table
    tables_to_test = [
        ('campaigns', 'campaign_id'),
        ('campaign_metrics', 'campaign_id'),
        ('agent_executions', 'execution_id')
    ]
    
    for table_name, sample_column in tables_to_test:
        try:
            print(f"\n📊 Testing {table_name} table...")
            
            # Count total records
            result = client.table(table_name).select('*', count='exact').limit(1).execute()
            total_count = result.count
            print(f"✅ {table_name}: {total_count} records found")
            
            # Get sample records
            sample_result = client.table(table_name).select('*').limit(5).execute()
            sample_data = sample_result.data
            
            if sample_data:
                print(f"📋 Sample {table_name} record:")
                # Print first record with nice formatting
                sample_record = sample_data[0]
                for key, value in list(sample_record.items())[:5]:  # First 5 fields
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:100] + "..."
                    print(f"   {key}: {value}")
                if len(sample_record) > 5:
                    print(f"   ... and {len(sample_record) - 5} more fields")
            else:
                print(f"⚠️  No sample data found in {table_name}")
                
        except Exception as e:
            print(f"❌ Error testing {table_name}: {e}")
            return False
    
    return True

async def test_facebook_api():
    """Test Facebook API simulator with uploaded data."""
    print("\n🔵 Testing Facebook API Simulator...")
    
    try:
        facebook_api = FacebookAPISimulator(supabase_service.get_client())
        
        # Test getting campaigns
        print("📋 Getting Facebook campaigns...")
        campaigns = await facebook_api.get_campaigns()
        print(f"✅ Retrieved {len(campaigns)} Facebook campaigns")
        
        if campaigns:
            # Test getting insights for first campaign
            campaign = campaigns[0]
            campaign_id = campaign['id']
            print(f"📊 Testing insights for campaign: {campaign['name']}")
            insights = await facebook_api.get_campaign_insights(campaign_id)
            
            print(f"✅ Campaign insights:")
            print(f"   • Impressions: {insights.get('impressions', 0):,}")
            print(f"   • Clicks: {insights.get('clicks', 0):,}")
            print(f"   • Spend: ${insights.get('spend', 0):,.2f}")
            print(f"   • CTR: {insights.get('ctr', 0):.2f}%")
            print(f"   • CPC: ${insights.get('cpc', 0):.2f}")
            
            # Test getting ad sets
            print(f"📁 Getting ad sets...")
            ad_sets = await facebook_api.get_ad_sets(campaign_id)
            print(f"✅ Retrieved {len(ad_sets)} ad sets")
        
        return True
        
    except Exception as e:
        print(f"❌ Facebook API test failed: {e}")
        return False

async def test_instagram_api():
    """Test Instagram API simulator with uploaded data."""
    print("\n📷 Testing Instagram API Simulator...")
    
    try:
        instagram_api = InstagramAPISimulator(supabase_service.get_client())
        
        # Test getting campaigns
        print("📋 Getting Instagram campaigns...")
        campaigns = await instagram_api.get_campaigns()
        print(f"✅ Retrieved {len(campaigns)} Instagram campaigns")
        
        if campaigns:
            # Test getting insights for first campaign
            campaign = campaigns[0]
            campaign_id = campaign['id']
            print(f"📊 Testing insights for campaign: {campaign['name']}")
            insights = await instagram_api.get_campaign_insights(campaign_id)
            
            print(f"✅ Campaign insights:")
            print(f"   • Impressions: {insights.get('impressions', 0):,}")
            print(f"   • Reach: {insights.get('reach', 0):,}")
            print(f"   • Engagement: {insights.get('engagement', 0):,}")
            print(f"   • Video Views: {insights.get('video_views', 0):,}")
            
            # Test getting media insights
            print(f"🎥 Getting media insights...")
            media_insights = await instagram_api.get_media_insights(campaign_id)
            print(f"✅ Media insights:")
            print(f"   • Likes: {media_insights.get('likes', 0):,}")
            print(f"   • Comments: {media_insights.get('comments', 0):,}")
            print(f"   • Shares: {media_insights.get('shares', 0):,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Instagram API test failed: {e}")
        return False

async def main():
    """Main test function."""
    print("🧪 Starting comprehensive Supabase data verification...\n")
    
    # Test 1: Database tables and data
    database_success = test_database_tables()
    
    if not database_success:
        print("\n❌ Database tests failed. Please ensure:")
        print("1. Tables are created using create_tables.sql")
        print("2. CSV files are uploaded correctly")
        return False
    
    # Test 2: Facebook API simulator
    facebook_success = await test_facebook_api()
    
    # Test 3: Instagram API simulator  
    instagram_success = await test_instagram_api()
    
    # Summary
    print(f"\n{'='*50}")
    print("🧪 TEST SUMMARY:")
    print(f"📊 Database Upload: {'✅ PASSED' if database_success else '❌ FAILED'}")
    print(f"🔵 Facebook API: {'✅ PASSED' if facebook_success else '❌ FAILED'}")
    print(f"📷 Instagram API: {'✅ PASSED' if instagram_success else '❌ FAILED'}")
    
    if database_success and facebook_success and instagram_success:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"🚀 Your backend is ready!")
        print(f"💡 The API simulators are working with your Supabase data")
        print(f"🔗 You can now build your frontend to consume these APIs")
        return True
    else:
        print(f"\n⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1) 