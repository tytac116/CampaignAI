from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import os
from dotenv import load_dotenv
from supabase import create_client, Client


class InstagramAPISimulator:
    """
    Simulates Instagram Basic Display API and Instagram Graph API responses using data from Supabase.
    This service acts as if it were the real Instagram API for agent consumption.
    """
    
    def __init__(self):
        # Load environment and create Supabase client
        load_dotenv()
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_anon_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment")
            
        self.supabase: Client = create_client(supabase_url, supabase_anon_key)
        self.api_version = "v18.0"
        self.base_url = "https://graph.instagram.com"
    
    async def get_campaigns(
        self,
        limit: int = 25,
        offset: int = 0,
        status_filter: Optional[List[str]] = None,
        date_preset: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Simulate GET /campaigns endpoint for Instagram.
        Returns Instagram-formatted campaign data.
        """
        try:
            # Build query
            query = self.supabase.table('campaigns').select('*').eq('platform', 'instagram')
            
            # Apply status filter
            if status_filter:
                # Convert to lowercase to match our data
                status_values = [status.lower() for status in status_filter]
                query = query.in_('status', status_values)
            
            # Apply date filtering
            if date_preset:
                start_date, end_date = self._get_date_range_from_preset(date_preset)
                if start_date and end_date:
                    query = query.gte('start_date', start_date.isoformat()).lte('start_date', end_date.isoformat())
            
            # Apply pagination
            query = query.range(offset, offset + limit - 1)
            
            # Execute query
            response = query.execute()
            campaigns = response.data or []
            
            # Format response like Instagram API
            instagram_campaigns = []
            for campaign in campaigns:
                campaign_data = await self._format_campaign_for_instagram(campaign, fields)
                instagram_campaigns.append(campaign_data)
            
            return {
                "data": instagram_campaigns,
                "paging": {
                    "cursors": {
                        "before": f"ig_cursor_before_{offset}",
                        "after": f"ig_cursor_after_{offset + len(instagram_campaigns)}"
                    },
                    "next": f"{self.base_url}/{self.api_version}/campaigns?limit={limit}&offset={offset + limit}" if len(instagram_campaigns) == limit else None
                }
            }
            
        except Exception as e:
            return {"error": {"message": f"Failed to get campaigns: {str(e)}", "code": 500}}
    
    async def get_campaign_insights(
        self,
        campaign_id: int,
        date_preset: str = "last_7d",
        time_increment: int = 1,
        breakdowns: Optional[List[str]] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Simulate GET /campaign/insights endpoint for Instagram.
        Returns Instagram-formatted insights data.
        """
        try:
            # Get date range
            start_date, end_date = self._get_date_range_from_preset(date_preset)
            
            # Convert campaign_id to string format used in metrics
            campaign_string_id = f"ig_camp_{campaign_id:04d}"
            
            # Query campaign metrics
            query = self.supabase.table('campaign_metrics').select('*').eq('campaign_id', campaign_string_id)
            
            if start_date and end_date:
                query = query.gte('metric_date', start_date.isoformat()).lte('metric_date', end_date.isoformat())
            
            response = query.execute()
            metrics = response.data or []
            
            # Format insights data
            insights_data = []
            
            if time_increment == 1:  # Daily data
                daily_metrics = self._aggregate_metrics_by_day(metrics)
                for date_str, day_metrics in daily_metrics.items():
                    insight = await self._format_insights_for_instagram(
                        day_metrics, date_str, breakdowns, fields
                    )
                    insights_data.append(insight)
            else:  # Individual records
                for metric in metrics:
                    insight = await self._format_insights_for_instagram(
                        [metric], metric['metric_date'], breakdowns, fields
                    )
                    insights_data.append(insight)
            
            return {
                "data": insights_data,
                "paging": {
                    "cursors": {
                        "before": "ig_insights_cursor_before",
                        "after": "ig_insights_cursor_after"
                    }
                }
            }
            
        except Exception as e:
            return {"error": {"message": f"Failed to get insights: {str(e)}", "code": 500}}
    
    async def get_media_insights(self, campaign_id: int) -> Dict[str, Any]:
        """
        Simulate GET /media/insights endpoint for Instagram.
        Returns Instagram-specific media insights (Stories, Reels, Posts).
        """
        try:
            # Get campaign to ensure it exists and get base metrics
            response = self.supabase.table('campaigns').select('*').eq('id', campaign_id).eq('platform', 'instagram').execute()
            
            if not response.data:
                return {"error": {"message": "Campaign not found", "code": 100}}
            
            campaign = response.data[0]
            
            # Generate mock media insights based on campaign creative type
            media_insights = []
            
            # Determine media types based on campaign creative
            creative_type = campaign.get('ad_creative', {}).get('type', 'image') if isinstance(campaign.get('ad_creative'), dict) else 'image'
            campaign_type = campaign.get('campaign_type', 'image_post')
            
            # Use campaign_type to determine media type
            if 'video' in campaign_type or 'reel' in campaign_type:
                # Video/Reels insights
                media_insights.append({
                    "id": f"ig_video_{campaign_id}",
                    "media_type": "VIDEO",
                    "insights": {
                        "data": [{
                            "name": "video_views",
                            "values": [{"value": campaign.get('impressions', 0) * 0.6}]  # 60% view rate
                        }, {
                            "name": "video_plays",
                            "values": [{"value": campaign.get('impressions', 0) * 0.8}]
                        }, {
                            "name": "video_completion_rate",
                            "values": [{"value": 0.45}]  # 45% completion rate
                        }, {
                            "name": "saves",
                            "values": [{"value": campaign.get('clicks', 0) * 0.1}]  # 10% save rate
                        }]
                    }
                })
            elif 'carousel' in campaign_type:
                # Carousel insights
                media_insights.append({
                    "id": f"ig_carousel_{campaign_id}",
                    "media_type": "CAROUSEL_ALBUM",
                    "insights": {
                        "data": [{
                            "name": "carousel_album_impressions",
                            "values": [{"value": campaign.get('impressions', 0)}]
                        }, {
                            "name": "carousel_album_reach",
                            "values": [{"value": campaign.get('impressions', 0) * 0.7}]
                        }, {
                            "name": "carousel_album_engagement",
                            "values": [{"value": campaign.get('clicks', 0) + (campaign.get('impressions', 0) * 0.02)}]  # Clicks + likes
                        }]
                    }
                })
            else:
                # Standard image post insights
                media_insights.append({
                    "id": f"ig_image_{campaign_id}",
                    "media_type": "IMAGE",
                    "insights": {
                        "data": [{
                            "name": "impressions",
                            "values": [{"value": campaign.get('impressions', 0)}]
                        }, {
                            "name": "reach",
                            "values": [{"value": campaign.get('impressions', 0) * 0.6}]  # Instagram reach typically lower
                        }, {
                            "name": "engagement",
                            "values": [{"value": campaign.get('clicks', 0) + (campaign.get('impressions', 0) * 0.03)}]  # Clicks + likes/comments
                        }, {
                            "name": "saves",
                            "values": [{"value": campaign.get('clicks', 0) * 0.15}]  # 15% save rate
                        }, {
                            "name": "profile_visits",
                            "values": [{"value": campaign.get('clicks', 0) * 0.25}]  # 25% profile visit rate
                        }]
                    }
                })
            
            return {
                "data": media_insights,
                "paging": {
                    "cursors": {
                        "before": f"ig_media_cursor_before_{campaign_id}",
                        "after": f"ig_media_cursor_after_{campaign_id}"
                    }
                }
            }
            
        except Exception as e:
            return {"error": {"message": f"Failed to get media insights: {str(e)}", "code": 500}}
    
    async def get_audience_insights(self, campaign_id: int) -> Dict[str, Any]:
        """
        Simulate GET /audience_insights endpoint for Instagram.
        Returns demographic and audience data.
        """
        try:
            # Get campaign to ensure it exists
            response = self.supabase.table('campaigns').select('*').eq('id', campaign_id).eq('platform', 'instagram').execute()
            
            if not response.data:
                return {"error": {"message": "Campaign not found", "code": 100}}
            
            campaign = response.data[0]
            
            # Generate mock audience insights
            audience_data = {
                "demographics": {
                    "age": {
                        "18-24": {"percentage": 25, "impressions": campaign.get('impressions', 0) * 0.25},
                        "25-34": {"percentage": 35, "impressions": campaign.get('impressions', 0) * 0.35},
                        "35-44": {"percentage": 25, "impressions": campaign.get('impressions', 0) * 0.25},
                        "45-54": {"percentage": 15, "impressions": campaign.get('impressions', 0) * 0.15}
                    },
                    "gender": {
                        "male": {"percentage": 45, "impressions": campaign.get('impressions', 0) * 0.45},
                        "female": {"percentage": 55, "impressions": campaign.get('impressions', 0) * 0.55}
                    },
                    "country": {
                        "ZA": {"percentage": 80, "impressions": campaign.get('impressions', 0) * 0.80},
                        "US": {"percentage": 15, "impressions": campaign.get('impressions', 0) * 0.15},
                        "GB": {"percentage": 5, "impressions": campaign.get('impressions', 0) * 0.05}
                    }
                },
                "interests": [
                    {"name": "Business", "percentage": 30},
                    {"name": "Technology", "percentage": 25},
                    {"name": "Marketing", "percentage": 20},
                    {"name": "Entrepreneurship", "percentage": 15},
                    {"name": "AI & Machine Learning", "percentage": 10}
                ],
                "behaviors": [
                    {"name": "Small business owners", "percentage": 40},
                    {"name": "Digital marketing professionals", "percentage": 30},
                    {"name": "Tech early adopters", "percentage": 20},
                    {"name": "Online shoppers", "percentage": 10}
                ],
                "device_usage": {
                    "mobile": {"percentage": 85, "impressions": campaign.get('impressions', 0) * 0.85},
                    "desktop": {"percentage": 15, "impressions": campaign.get('impressions', 0) * 0.15}
                }
            }
            
            return {
                "data": audience_data,
                "paging": {
                    "cursors": {
                        "before": f"ig_audience_cursor_before_{campaign_id}",
                        "after": f"ig_audience_cursor_after_{campaign_id}"
                    }
                }
            }
            
        except Exception as e:
            return {"error": {"message": f"Failed to get audience insights: {str(e)}", "code": 500}}
    
    async def update_campaign(self, campaign_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate POST /campaign endpoint for updates.
        Updates campaign data in Supabase.
        """
        try:
            # Get campaign first
            response = self.supabase.table('campaigns').select('*').eq('id', campaign_id).eq('platform', 'instagram').execute()
            
            if not response.data:
                return {"error": {"message": "Campaign not found", "code": 100}}
            
            # Prepare update data
            update_data = {}
            if 'name' in updates:
                update_data['name'] = updates['name']
            if 'status' in updates:
                update_data['status'] = updates['status'].lower()
            if 'budget' in updates:
                update_data['budget'] = float(updates['budget'])
            if 'daily_budget' in updates:
                update_data['daily_budget'] = float(updates['daily_budget'])
            
            # Add updated timestamp
            update_data['updated_at'] = datetime.now().isoformat()
            
            # Update campaign
            update_response = self.supabase.table('campaigns').update(update_data).eq('id', campaign_id).execute()
            
            if update_response.data:
                return {
                    "success": True,
                    "data": update_response.data[0]
                }
            else:
                return {"error": {"message": "Update failed", "code": 500}}
                
        except Exception as e:
            return {"error": {"message": f"Failed to update campaign: {str(e)}", "code": 500}}
    
    def _get_date_range_from_preset(self, date_preset: str) -> tuple[date, date]:
        """Convert date preset to actual date range."""
        end_date = datetime.now().date()
        
        if date_preset == "yesterday":
            start_date = end_date - timedelta(days=1)
            end_date = start_date
        elif date_preset == "last_7d":
            start_date = end_date - timedelta(days=7)
        elif date_preset == "last_14d":
            start_date = end_date - timedelta(days=14)
        elif date_preset == "last_30d":
            start_date = end_date - timedelta(days=30)
        elif date_preset == "this_month":
            start_date = end_date.replace(day=1)
        elif date_preset == "last_month":
            first_day_this_month = end_date.replace(day=1)
            end_date = first_day_this_month - timedelta(days=1)
            start_date = end_date.replace(day=1)
        else:
            # Default to last 7 days
            start_date = end_date - timedelta(days=7)
        
        return start_date, end_date
    
    def _aggregate_metrics_by_day(self, metrics: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group metrics by day."""
        daily_metrics = {}
        for metric in metrics:
            date_str = metric['metric_date']
            if date_str not in daily_metrics:
                daily_metrics[date_str] = []
            daily_metrics[date_str].append(metric)
        return daily_metrics
    
    async def _format_campaign_for_instagram(self, campaign: Dict[str, Any], fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Format campaign data like Instagram API response."""
        
        # Base Instagram campaign format
        ig_campaign = {
            "id": str(campaign['id']),
            "name": campaign['name'],
            "status": campaign['status'].upper(),
            "objective": self._map_objective_to_instagram(campaign.get('objective', 'REACH')),
            "created_time": campaign['created_at'],
            "updated_time": campaign['updated_at'],
            "start_time": campaign.get('start_date'),
            "stop_time": campaign.get('end_date'),
            "budget_remaining": str(max(0, campaign.get('budget', 0) - campaign.get('spend', 0))),
            "daily_budget": str(campaign.get('daily_budget', 0)),
            "lifetime_budget": str(campaign.get('budget', 0)),
            "campaign_type": campaign.get('campaign_type', 'image_post'),
            "instagram_actor_id": f"ig_actor_{campaign['id']}",
            "special_ad_categories": []
        }
        
        # Add specific fields if requested
        if fields:
            filtered_campaign = {}
            for field in fields:
                if field in ig_campaign:
                    filtered_campaign[field] = ig_campaign[field]
            return filtered_campaign
        
        return ig_campaign
    
    async def _format_insights_for_instagram(
        self, 
        metrics: List[Dict[str, Any]], 
        date_str: str,
        breakdowns: Optional[List[str]] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Format metrics data like Instagram insights response."""
        
        # Aggregate metrics for the day
        total_impressions = sum(m.get('impressions', 0) for m in metrics)
        total_clicks = sum(m.get('clicks', 0) for m in metrics)
        total_spend = sum(m.get('spend', 0) for m in metrics)
        total_conversions = sum(m.get('conversions', 0) for m in metrics)
        total_revenue = sum(m.get('revenue', 0) for m in metrics)
        
        # Calculate Instagram-specific metrics
        reach = int(total_impressions * 0.6)  # Instagram typically has lower reach than Facebook
        engagement = total_clicks + int(total_impressions * 0.02)  # Clicks + estimated likes/comments
        saves = int(total_clicks * 0.15)  # 15% save rate
        profile_visits = int(total_clicks * 0.3)  # 30% profile visit rate
        story_exits = int(total_clicks * 0.1)  # 10% story exit rate
        story_replies = int(total_clicks * 0.05)  # 5% story reply rate
        
        # Base insight format
        insight = {
            "date_start": date_str,
            "date_stop": date_str,
            "impressions": str(total_impressions),
            "reach": str(reach),
            "clicks": str(total_clicks),
            "spend": str(total_spend),
            "engagement": str(engagement),
            "saves": str(saves),
            "profile_visits": str(profile_visits),
            "story_exits": str(story_exits),
            "story_replies": str(story_replies),
            "video_views": str(int(total_impressions * 0.4)),  # 40% video view rate
            "website_clicks": str(total_clicks),
            "conversions": str(total_conversions),
            "revenue": str(total_revenue)
        }
        
        # Add breakdowns if requested
        if breakdowns:
            for breakdown in breakdowns:
                if breakdown == "age":
                    insight["age"] = "25-34"  # Mock breakdown
                elif breakdown == "gender":
                    insight["gender"] = "female"  # Mock breakdown
                elif breakdown == "country":
                    insight["country"] = "ZA"  # South Africa
                elif breakdown == "placement":
                    insight["placement"] = "instagram_feed"
        
        # Filter fields if requested
        if fields:
            filtered_insight = {}
            for field in fields:
                if field in insight:
                    filtered_insight[field] = insight[field]
            return filtered_insight
        
        return insight
    
    def _map_objective_to_instagram(self, objective: Optional[str]) -> str:
        """Map general objectives to Instagram-specific ones."""
        if not objective:
            return "REACH"
        
        mapping = {
            "TRAFFIC": "REACH",
            "CONVERSIONS": "REACH", 
            "BRAND_AWARENESS": "REACH",
            "REACH": "REACH",
            "ENGAGEMENT": "REACH",
            "VIDEO_VIEWS": "REACH",
            "LEAD_GENERATION": "REACH"
        }
        
        return mapping.get(objective.upper(), "REACH") 