from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import os
from dotenv import load_dotenv
from supabase import create_client, Client


class FacebookAPISimulator:
    """
    Simulates Facebook Marketing API responses using data from Supabase.
    This service acts as if it were the real Facebook API for agent consumption.
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
        self.base_url = "https://graph.facebook.com"
    
    async def get_campaigns(
        self,
        limit: int = 25,
        offset: int = 0,
        status_filter: Optional[List[str]] = None,
        date_preset: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Simulate GET /campaigns endpoint.
        Returns Facebook-formatted campaign data.
        """
        try:
            # Build query
            query = self.supabase.table('campaigns').select('*').eq('platform', 'facebook')
            
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
            
            # Format response like Facebook API
            facebook_campaigns = []
            for campaign in campaigns:
                campaign_data = await self._format_campaign_for_facebook(campaign, fields)
                facebook_campaigns.append(campaign_data)
            
            return {
                "data": facebook_campaigns,
                "paging": {
                    "cursors": {
                        "before": f"cursor_before_{offset}",
                        "after": f"cursor_after_{offset + len(facebook_campaigns)}"
                    },
                    "next": f"{self.base_url}/{self.api_version}/campaigns?limit={limit}&offset={offset + limit}" if len(facebook_campaigns) == limit else None
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
        Simulate GET /campaign/insights endpoint.
        Returns Facebook-formatted insights data.
        """
        try:
            # Get date range
            start_date, end_date = self._get_date_range_from_preset(date_preset)
            
            # Convert campaign_id to string format used in metrics
            campaign_string_id = f"fb_camp_{campaign_id:04d}"
            
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
                    insight = await self._format_insights_for_facebook(
                        day_metrics, date_str, breakdowns, fields
                    )
                    insights_data.append(insight)
            else:  # Individual records
                for metric in metrics:
                    insight = await self._format_insights_for_facebook(
                        [metric], metric['metric_date'], breakdowns, fields
                    )
                    insights_data.append(insight)
            
            return {
                "data": insights_data,
                "paging": {
                    "cursors": {
                        "before": "insights_cursor_before",
                        "after": "insights_cursor_after"
                    }
                }
            }
            
        except Exception as e:
            return {"error": {"message": f"Failed to get insights: {str(e)}", "code": 500}}
    
    async def get_campaign_ad_sets(self, campaign_id: int) -> Dict[str, Any]:
        """
        Simulate GET /campaign/adsets endpoint.
        Returns mock ad sets data since we don't have ad sets in our model.
        """
        try:
            # Get campaign to ensure it exists
            response = self.supabase.table('campaigns').select('*').eq('id', campaign_id).eq('platform', 'facebook').execute()
            
            if not response.data:
                return {"error": {"message": "Campaign not found", "code": 100}}
            
            campaign = response.data[0]
            
            # Generate mock ad sets based on campaign data
            mock_ad_sets = []
            # Use impressions from campaign or default to reasonable number
            impressions = campaign.get('impressions', 5000)
            num_ad_sets = min(5, max(1, impressions // 10000))
            
            for i in range(num_ad_sets):
                ad_set = {
                    "id": f"{campaign_id}_{i + 1}_adset",
                    "name": f"Ad Set {i + 1} - {campaign['name']}",
                    "status": campaign['status'].upper(),
                    "targeting": {
                        "age_min": 18,
                        "age_max": 65,
                        "genders": [1, 2],  # All genders
                        "geo_locations": {"countries": ["ZA"]},  # South Africa
                        "interests": campaign.get('target_audience', {}).get('interests', []) if isinstance(campaign.get('target_audience'), dict) else []
                    },
                    "budget_remaining": str(max(0, campaign.get('budget', 0) - campaign.get('spend', 0))),
                    "daily_budget": str(campaign.get('daily_budget', 0)),
                    "bid_strategy": campaign.get('campaign_settings', {}).get('bid_strategy', 'LOWEST_COST_WITHOUT_CAP') if isinstance(campaign.get('campaign_settings'), dict) else 'LOWEST_COST_WITHOUT_CAP',
                    "optimization_goal": campaign.get('campaign_settings', {}).get('optimization_goal', 'CONVERSIONS') if isinstance(campaign.get('campaign_settings'), dict) else 'CONVERSIONS',
                    "created_time": campaign['created_at'],
                    "updated_time": campaign['updated_at'],
                }
                mock_ad_sets.append(ad_set)
            
            return {
                "data": mock_ad_sets,
                "paging": {
                    "cursors": {
                        "before": f"adset_cursor_before_{campaign_id}",
                        "after": f"adset_cursor_after_{campaign_id}"
                    }
                }
            }
            
        except Exception as e:
            return {"error": {"message": f"Failed to get ad sets: {str(e)}", "code": 500}}
    
    async def update_campaign(self, campaign_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate POST /campaign endpoint for updates.
        Updates campaign data in Supabase.
        """
        try:
            # Get campaign first
            response = self.supabase.table('campaigns').select('*').eq('id', campaign_id).eq('platform', 'facebook').execute()
            
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
    
    async def _format_campaign_for_facebook(self, campaign: Dict[str, Any], fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Format campaign data like Facebook API response."""
        
        # Base Facebook campaign format
        fb_campaign = {
            "id": str(campaign['id']),
            "name": campaign['name'],
            "status": campaign['status'].upper(),
            "objective": campaign.get('objective', 'TRAFFIC').upper(),
            "created_time": campaign['created_at'],
            "updated_time": campaign['updated_at'],
            "start_time": campaign.get('start_date'),
            "stop_time": campaign.get('end_date'),
            "budget_remaining": str(max(0, campaign.get('budget', 0) - campaign.get('spend', 0))),
            "daily_budget": str(campaign.get('daily_budget', 0)),
            "lifetime_budget": str(campaign.get('budget', 0)),
            "campaign_type": campaign.get('campaign_type', 'video_ad'),
            "special_ad_categories": [],
            "bid_strategy": campaign.get('campaign_settings', {}).get('bid_strategy', 'LOWEST_COST_WITHOUT_CAP') if isinstance(campaign.get('campaign_settings'), dict) else 'LOWEST_COST_WITHOUT_CAP'
        }
        
        # Add specific fields if requested
        if fields:
            filtered_campaign = {}
            for field in fields:
                if field in fb_campaign:
                    filtered_campaign[field] = fb_campaign[field]
            return filtered_campaign
        
        return fb_campaign
    
    async def _format_insights_for_facebook(
        self, 
        metrics: List[Dict[str, Any]], 
        date_str: str,
        breakdowns: Optional[List[str]] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Format metrics data like Facebook insights response."""
        
        # Aggregate metrics for the day
        total_impressions = sum(m.get('impressions', 0) for m in metrics)
        total_clicks = sum(m.get('clicks', 0) for m in metrics)
        total_spend = sum(m.get('spend', 0) for m in metrics)
        total_conversions = sum(m.get('conversions', 0) for m in metrics)
        total_revenue = sum(m.get('revenue', 0) for m in metrics)
        
        # Calculate derived metrics
        cpm = round(total_spend / total_impressions * 1000, 2) if total_impressions > 0 else 0
        cpc = round(total_spend / total_clicks, 2) if total_clicks > 0 else 0
        ctr = round(total_clicks / total_impressions * 100, 2) if total_impressions > 0 else 0
        conversion_rate = round(total_conversions / total_clicks * 100, 2) if total_clicks > 0 else 0
        roas = round(total_revenue / total_spend, 2) if total_spend > 0 else 0
        
        # Base insight format
        insight = {
            "date_start": date_str,
            "date_stop": date_str,
            "impressions": str(total_impressions),
            "clicks": str(total_clicks),
            "spend": str(total_spend),
            "conversions": str(total_conversions),
            "revenue": str(total_revenue),
            "reach": str(int(total_impressions * 0.7)),  # Estimated reach
            "frequency": str(round(total_impressions / (total_impressions * 0.7), 2)) if total_impressions > 0 else "1",
            "cpm": str(cpm),
            "cpc": str(cpc),
            "ctr": str(ctr),
            "conversion_rate": str(conversion_rate),
            "cost_per_conversion": str(round(total_spend / total_conversions, 2)) if total_conversions > 0 else "0",
            "return_on_ad_spend": str(roas)
        }
        
        # Add breakdowns if requested
        if breakdowns:
            for breakdown in breakdowns:
                if breakdown == "age":
                    insight["age"] = "25-34"  # Mock breakdown
                elif breakdown == "gender":
                    insight["gender"] = "male"  # Mock breakdown
                elif breakdown == "country":
                    insight["country"] = "ZA"  # South Africa
        
        # Filter fields if requested
        if fields:
            filtered_insight = {}
            for field in fields:
                if field in insight:
                    filtered_insight[field] = insight[field]
            return filtered_insight
        
        return insight 