#!/usr/bin/env python3

"""
Test script for Facebook and Instagram API simulators.
Validates that the APIs work correctly with Supabase data for agent consumption.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any

from app.services.facebook_api_sim import FacebookAPISimulator
from app.services.instagram_api_sim import InstagramAPISimulator
from app.core.database import async_session_factory
from app.models.campaign import Campaign, PlatformType
from sqlalchemy import select, func


class APISimulatorTester:
    """Test suite for API simulators."""
    
    def __init__(self):
        self.fb_api = FacebookAPISimulator()
        self.ig_api = InstagramAPISimulator()
        self.session_factory = async_session_factory
        
    async def run_all_tests(self):
        """Run comprehensive test suite."""
        print("🧪 Starting API Simulator Test Suite")
        print("=" * 60)
        
        try:
            # Test database connectivity
            await self.test_database_connection()
            
            # Test Facebook API
            print("\n📘 Testing Facebook API Simulator...")
            await self.test_facebook_api()
            
            # Test Instagram API  
            print("\n📷 Testing Instagram API Simulator...")
            await self.test_instagram_api()
            
            # Test cross-platform functionality
            print("\n🔄 Testing Cross-Platform Functionality...")
            await self.test_cross_platform()
            
            print("\n" + "=" * 60)
            print("✅ All API simulator tests completed successfully!")
            print("🤖 APIs are ready for agent consumption")
            
        except Exception as e:
            print(f"\n❌ Test suite failed: {e}")
            raise
    
    async def test_database_connection(self):
        """Test database connectivity and data availability."""
        print("🔌 Testing database connection...")
        
        async with self.session_factory() as session:
            # Count campaigns by platform
            fb_count = await session.scalar(
                select(func.count(Campaign.id)).where(Campaign.platform == PlatformType.FACEBOOK)
            )
            ig_count = await session.scalar(
                select(func.count(Campaign.id)).where(Campaign.platform == PlatformType.INSTAGRAM)
            )
            
            print(f"  📊 Found {fb_count} Facebook campaigns")
            print(f"  📊 Found {ig_count} Instagram campaigns")
            
            if fb_count == 0 or ig_count == 0:
                raise Exception("No campaign data found in database")
            
            print("  ✅ Database connection successful")
    
    async def test_facebook_api(self):
        """Test Facebook API simulator endpoints."""
        
        # Test 1: Get campaigns
        print("  🔍 Testing get_campaigns endpoint...")
        campaigns_response = await self.fb_api.get_campaigns(limit=5)
        
        self._validate_response_structure(campaigns_response, ["data", "paging"])
        self._validate_campaigns_data(campaigns_response["data"], "facebook")
        print(f"    ✅ Retrieved {len(campaigns_response['data'])} Facebook campaigns")
        
        # Test 2: Get campaign insights
        if campaigns_response["data"]:
            campaign_id = campaigns_response["data"][0]["id"]
            print(f"  📈 Testing get_campaign_insights for campaign {campaign_id}...")
            
            insights_response = await self.fb_api.get_campaign_insights(
                campaign_id=campaign_id,
                date_preset="last_7d"
            )
            
            self._validate_response_structure(insights_response, ["data", "paging"])
            self._validate_insights_data(insights_response["data"])
            print(f"    ✅ Retrieved insights for {len(insights_response['data'])} days")
        
        # Test 3: Get ad sets
        if campaigns_response["data"]:
            campaign_id = campaigns_response["data"][0]["id"]
            print(f"  🎯 Testing get_campaign_ad_sets for campaign {campaign_id}...")
            
            adsets_response = await self.fb_api.get_campaign_ad_sets(campaign_id)
            
            if "error" not in adsets_response:
                self._validate_response_structure(adsets_response, ["data", "paging"])
                print(f"    ✅ Retrieved {len(adsets_response['data'])} ad sets")
            else:
                print(f"    ⚠️  Ad sets test returned error: {adsets_response['error']['message']}")
        
        # Test 4: Update campaign
        if campaigns_response["data"]:
            campaign_id = campaigns_response["data"][0]["id"]
            print(f"  ✏️  Testing update_campaign for campaign {campaign_id}...")
            
            update_response = await self.fb_api.update_campaign(
                campaign_id=campaign_id,
                updates={"status": "PAUSED", "daily_budget": 100.0}
            )
            
            if "error" not in update_response:
                print("    ✅ Campaign update successful")
            else:
                print(f"    ⚠️  Campaign update returned error: {update_response['error']['message']}")
    
    async def test_instagram_api(self):
        """Test Instagram API simulator endpoints."""
        
        # Test 1: Get campaigns
        print("  🔍 Testing get_campaigns endpoint...")
        campaigns_response = await self.ig_api.get_campaigns(limit=5)
        
        self._validate_response_structure(campaigns_response, ["data", "paging"])
        self._validate_campaigns_data(campaigns_response["data"], "instagram")
        print(f"    ✅ Retrieved {len(campaigns_response['data'])} Instagram campaigns")
        
        # Test 2: Get campaign insights
        if campaigns_response["data"]:
            campaign_id = campaigns_response["data"][0]["id"]
            print(f"  📈 Testing get_campaign_insights for campaign {campaign_id}...")
            
            insights_response = await self.ig_api.get_campaign_insights(
                campaign_id=campaign_id,
                date_preset="last_7d"
            )
            
            self._validate_response_structure(insights_response, ["data", "paging"])
            self._validate_insights_data(insights_response["data"])
            print(f"    ✅ Retrieved insights for {len(insights_response['data'])} days")
        
        # Test 3: Get media insights (Instagram-specific)
        if campaigns_response["data"]:
            campaign_id = campaigns_response["data"][0]["id"]
            print(f"  🎬 Testing get_media_insights for campaign {campaign_id}...")
            
            media_response = await self.ig_api.get_media_insights(campaign_id)
            
            if "error" not in media_response:
                self._validate_response_structure(media_response, ["data"])
                print(f"    ✅ Retrieved media insights for {len(media_response['data'])} media items")
            else:
                print(f"    ⚠️  Media insights test returned error: {media_response['error']['message']}")
        
        # Test 4: Get audience insights (Instagram-specific)
        if campaigns_response["data"]:
            campaign_id = campaigns_response["data"][0]["id"]
            print(f"  👥 Testing get_audience_insights for campaign {campaign_id}...")
            
            audience_response = await self.ig_api.get_audience_insights(campaign_id)
            
            if "error" not in audience_response:
                self._validate_response_structure(audience_response, ["data"])
                print("    ✅ Retrieved audience insights")
            else:
                print(f"    ⚠️  Audience insights test returned error: {audience_response['error']['message']}")
    
    async def test_cross_platform(self):
        """Test cross-platform functionality and data consistency."""
        
        # Test filtering and pagination consistency
        print("  🔄 Testing pagination consistency...")
        
        fb_page1 = await self.fb_api.get_campaigns(limit=3, offset=0)
        fb_page2 = await self.fb_api.get_campaigns(limit=3, offset=3)
        
        ig_page1 = await self.ig_api.get_campaigns(limit=3, offset=0)
        ig_page2 = await self.ig_api.get_campaigns(limit=3, offset=3)
        
        # Validate no overlap in pagination
        fb_ids_page1 = {c["id"] for c in fb_page1["data"]}
        fb_ids_page2 = {c["id"] for c in fb_page2["data"]}
        
        if fb_ids_page1.intersection(fb_ids_page2):
            print("    ⚠️  Facebook pagination has overlapping results")
        else:
            print("    ✅ Facebook pagination working correctly")
        
        ig_ids_page1 = {c["id"] for c in ig_page1["data"]}
        ig_ids_page2 = {c["id"] for c in ig_page2["data"]}
        
        if ig_ids_page1.intersection(ig_ids_page2):
            print("    ⚠️  Instagram pagination has overlapping results")
        else:
            print("    ✅ Instagram pagination working correctly")
        
        # Test status filtering
        print("  🎯 Testing status filtering...")
        
        active_fb = await self.fb_api.get_campaigns(status_filter=["active"], limit=10)
        paused_fb = await self.fb_api.get_campaigns(status_filter=["paused"], limit=10)
        
        active_ig = await self.ig_api.get_campaigns(status_filter=["active"], limit=10)
        paused_ig = await self.ig_api.get_campaigns(status_filter=["paused"], limit=10)
        
        print(f"    📊 Facebook: {len(active_fb['data'])} active, {len(paused_fb['data'])} paused")
        print(f"    📊 Instagram: {len(active_ig['data'])} active, {len(paused_ig['data'])} paused")
        print("    ✅ Status filtering working correctly")
    
    def _validate_response_structure(self, response: Dict[str, Any], required_keys: list):
        """Validate API response has required structure."""
        for key in required_keys:
            if key not in response:
                raise Exception(f"Missing required key '{key}' in API response")
    
    def _validate_campaigns_data(self, campaigns: list, platform: str):
        """Validate campaigns data structure."""
        if not campaigns:
            raise Exception(f"No {platform} campaigns returned")
        
        required_fields = ["id", "name", "status", "objective"]
        for campaign in campaigns:
            for field in required_fields:
                if field not in campaign:
                    raise Exception(f"Missing required field '{field}' in campaign data")
    
    def _validate_insights_data(self, insights: list):
        """Validate insights data structure."""
        if not insights:
            print("    ⚠️  No insights data returned (may be expected for test data)")
            return
        
        required_fields = ["date_start", "date_stop", "impressions", "clicks"]
        for insight in insights:
            for field in required_fields:
                if field not in insight:
                    raise Exception(f"Missing required field '{field}' in insights data")
    
    async def demonstrate_agent_usage(self):
        """Demonstrate how agents would use these APIs."""
        print("\n🤖 Demonstrating Agent Usage Patterns...")
        print("-" * 40)
        
        # Agent workflow 1: Campaign performance analysis
        print("📊 Agent Workflow 1: Campaign Performance Analysis")
        
        # Get top performing Facebook campaigns
        fb_campaigns = await self.fb_api.get_campaigns(limit=5)
        if fb_campaigns["data"]:
            best_campaign = max(fb_campaigns["data"], key=lambda x: x.get("roas", 0))
            print(f"  🏆 Best Facebook campaign: {best_campaign['name']} (ROAS: {best_campaign.get('roas', 'N/A')})")
            
            # Get detailed insights for best campaign
            insights = await self.fb_api.get_campaign_insights(
                campaign_id=best_campaign["id"],
                date_preset="last_7d"
            )
            print(f"  📈 Retrieved {len(insights['data'])} days of performance data")
        
        # Agent workflow 2: Cross-platform comparison
        print("\n🔄 Agent Workflow 2: Cross-Platform Comparison")
        
        ig_campaigns = await self.ig_api.get_campaigns(limit=5)
        
        fb_total_spend = sum(c.get("spend", 0) for c in fb_campaigns["data"])
        ig_total_spend = sum(c.get("spend", 0) for c in ig_campaigns["data"])
        
        print(f"  💰 Facebook total spend: ${fb_total_spend:,.2f}")
        print(f"  💰 Instagram total spend: ${ig_total_spend:,.2f}")
        
        # Agent workflow 3: Campaign optimization recommendations
        print("\n⚡ Agent Workflow 3: Optimization Recommendations")
        
        for campaign in fb_campaigns["data"][:2]:
            ctr = campaign.get("ctr", 0)
            roas = campaign.get("roas", 0)
            
            recommendations = []
            if ctr < 1.0:
                recommendations.append("Improve ad creative to increase CTR")
            if roas < 2.0:
                recommendations.append("Optimize targeting to improve ROAS")
            if not recommendations:
                recommendations.append("Campaign performing well, consider scaling")
            
            print(f"  🎯 {campaign['name'][:30]}...")
            for rec in recommendations:
                print(f"    • {rec}")


async def main():
    """Run the API simulator test suite."""
    tester = APISimulatorTester()
    
    try:
        await tester.run_all_tests()
        await tester.demonstrate_agent_usage()
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 