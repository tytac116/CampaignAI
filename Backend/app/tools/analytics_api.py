"""
Analytics API Tools for Facebook and Instagram campaign insights.

This tool provides comprehensive analytics and reporting capabilities
for both Facebook and Instagram campaigns using historical metrics data.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from langchain_core.tools import tool
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')

if not supabase_url or not supabase_anon_key:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment")

supabase: Client = create_client(supabase_url, supabase_anon_key)


@tool
def get_campaign_analytics(
    campaign_id: str,
    date_range: str = "last_7_days",
    metrics: str = "all"
) -> str:
    """
    Get detailed analytics for a specific campaign (Facebook or Instagram).
    
    Use this tool to analyze campaign performance over time with daily breakdowns.
    
    Args:
        campaign_id: The campaign ID to analyze (works for both Facebook and Instagram)
        date_range: Time period - 'last_7_days', 'last_30_days', 'last_90_days', or 'all_time' (default: 'last_7_days')
        metrics: Metrics to include - 'performance', 'engagement', 'financial', or 'all' (default: 'all')
        
    Returns:
        JSON string containing detailed analytics with daily breakdowns
    """
    try:
        logger.info(f"Fetching analytics for campaign: {campaign_id}")
        
        # First, get campaign info to determine platform
        campaign_response = supabase.table('campaigns').select('*').eq('campaign_id', campaign_id).execute()
        
        if not campaign_response.data:
            return f"Error: Campaign '{campaign_id}' not found"
        
        campaign = campaign_response.data[0]
        platform = campaign['platform']
        
        # Calculate date range
        end_date = datetime.now().date()
        if date_range == "last_7_days":
            start_date = end_date - timedelta(days=7)
        elif date_range == "last_30_days":
            start_date = end_date - timedelta(days=30)
        elif date_range == "last_90_days":
            start_date = end_date - timedelta(days=90)
        else:  # all_time
            start_date = datetime.strptime(campaign['start_date'], '%Y-%m-%d').date()
        
        # Get metrics data
        metrics_response = supabase.table('campaign_metrics').select('*').eq('campaign_id', campaign_id).gte('metric_date', start_date.isoformat()).lte('metric_date', end_date.isoformat()).order('metric_date').execute()
        
        metrics_data = metrics_response.data or []
        
        # Calculate aggregated metrics
        total_metrics = {
            "impressions": sum(m['impressions'] for m in metrics_data),
            "clicks": sum(m['clicks'] for m in metrics_data),
            "spend": sum(m['spend'] for m in metrics_data),
            "conversions": sum(m['conversions'] for m in metrics_data),
            "revenue": sum(m['revenue'] for m in metrics_data),
            "likes": sum(m['likes'] for m in metrics_data),
            "shares": sum(m['shares'] for m in metrics_data),
            "saves": sum(m['saves'] for m in metrics_data),
            "profile_visits": sum(m['profile_visits'] for m in metrics_data)
        }
        
        # Calculate derived metrics
        ctr = (total_metrics['clicks'] / total_metrics['impressions'] * 100) if total_metrics['impressions'] > 0 else 0
        cpc = (total_metrics['spend'] / total_metrics['clicks']) if total_metrics['clicks'] > 0 else 0
        cpm = (total_metrics['spend'] / total_metrics['impressions'] * 1000) if total_metrics['impressions'] > 0 else 0
        roas = (total_metrics['revenue'] / total_metrics['spend']) if total_metrics['spend'] > 0 else 0
        
        # Format response
        result = {
            "campaign_id": campaign_id,
            "campaign_name": campaign['name'],
            "platform": platform,
            "analysis_period": {
                "date_range": date_range,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_days": len(metrics_data)
            },
            "summary_metrics": {
                "performance": {
                    "total_impressions": total_metrics['impressions'],
                    "total_clicks": total_metrics['clicks'],
                    "total_conversions": total_metrics['conversions'],
                    "click_through_rate": round(ctr, 2),
                    "cost_per_click": round(cpc, 2),
                    "cost_per_mille": round(cpm, 2)
                },
                "financial": {
                    "total_spend": round(total_metrics['spend'], 2),
                    "total_revenue": round(total_metrics['revenue'], 2),
                    "return_on_ad_spend": round(roas, 2),
                    "profit": round(total_metrics['revenue'] - total_metrics['spend'], 2)
                },
                "engagement": {
                    "total_likes": total_metrics['likes'],
                    "total_shares": total_metrics['shares'],
                    "total_saves": total_metrics['saves'],
                    "total_profile_visits": total_metrics['profile_visits'],
                    "total_engagement": total_metrics['likes'] + total_metrics['shares'] + total_metrics['saves']
                }
            },
            "daily_breakdown": []
        }
        
        # Add daily breakdown if requested
        if metrics in ["all", "daily"]:
            for metric in metrics_data:
                daily_data = {
                    "date": metric['metric_date'],
                    "impressions": metric['impressions'],
                    "clicks": metric['clicks'],
                    "spend": metric['spend'],
                    "conversions": metric['conversions'],
                    "revenue": metric['revenue'],
                    "likes": metric['likes'],
                    "shares": metric['shares'],
                    "saves": metric['saves'],
                    "profile_visits": metric['profile_visits']
                }
                result["daily_breakdown"].append(daily_data)
        
        logger.info(f"Successfully retrieved analytics for campaign: {campaign_id}")
        return str(result)
        
    except Exception as e:
        error_msg = f"Failed to get campaign analytics: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@tool
def get_platform_performance_comparison(
    date_range: str = "last_30_days",
    limit: int = 10
) -> str:
    """
    Compare performance between Facebook and Instagram campaigns.
    
    Use this tool to analyze which platform is performing better and identify optimization opportunities.
    
    Args:
        date_range: Time period - 'last_7_days', 'last_30_days', 'last_90_days' (default: 'last_30_days')
        limit: Number of top campaigns per platform to include (default: 10, max: 25)
        
    Returns:
        JSON string containing platform comparison analysis
    """
    try:
        logger.info(f"Comparing platform performance: {date_range}")
        
        # Calculate date range
        end_date = datetime.now().date()
        if date_range == "last_7_days":
            start_date = end_date - timedelta(days=7)
        elif date_range == "last_30_days":
            start_date = end_date - timedelta(days=30)
        else:  # last_90_days
            start_date = end_date - timedelta(days=90)
        
        # Get Facebook campaigns
        fb_campaigns = supabase.table('campaigns').select('*').eq('platform', 'facebook').limit(min(limit, 25)).execute()
        
        # Get Instagram campaigns
        ig_campaigns = supabase.table('campaigns').select('*').eq('platform', 'instagram').limit(min(limit, 25)).execute()
        
        # Calculate platform totals
        fb_totals = {
            "campaigns": len(fb_campaigns.data),
            "impressions": sum(c['impressions'] for c in fb_campaigns.data),
            "clicks": sum(c['clicks'] for c in fb_campaigns.data),
            "spend": sum(c['spend_amount'] for c in fb_campaigns.data),
            "revenue": sum(c['revenue'] for c in fb_campaigns.data),
            "conversions": sum(c['conversions'] for c in fb_campaigns.data)
        }
        
        ig_totals = {
            "campaigns": len(ig_campaigns.data),
            "impressions": sum(c['impressions'] for c in ig_campaigns.data),
            "clicks": sum(c['clicks'] for c in ig_campaigns.data),
            "spend": sum(c['spend_amount'] for c in ig_campaigns.data),
            "revenue": sum(c['revenue'] for c in ig_campaigns.data),
            "conversions": sum(c['conversions'] for c in ig_campaigns.data)
        }
        
        # Calculate platform averages
        fb_avg_ctr = (fb_totals['clicks'] / fb_totals['impressions'] * 100) if fb_totals['impressions'] > 0 else 0
        fb_avg_roas = (fb_totals['revenue'] / fb_totals['spend']) if fb_totals['spend'] > 0 else 0
        
        ig_avg_ctr = (ig_totals['clicks'] / ig_totals['impressions'] * 100) if ig_totals['impressions'] > 0 else 0
        ig_avg_roas = (ig_totals['revenue'] / ig_totals['spend']) if ig_totals['spend'] > 0 else 0
        
        # Format response
        result = {
            "analysis_period": {
                "date_range": date_range,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "platform_comparison": {
                "facebook": {
                    "total_campaigns": fb_totals['campaigns'],
                    "total_impressions": fb_totals['impressions'],
                    "total_clicks": fb_totals['clicks'],
                    "total_spend": round(fb_totals['spend'], 2),
                    "total_revenue": round(fb_totals['revenue'], 2),
                    "total_conversions": fb_totals['conversions'],
                    "average_ctr": round(fb_avg_ctr, 2),
                    "average_roas": round(fb_avg_roas, 2)
                },
                "instagram": {
                    "total_campaigns": ig_totals['campaigns'],
                    "total_impressions": ig_totals['impressions'],
                    "total_clicks": ig_totals['clicks'],
                    "total_spend": round(ig_totals['spend'], 2),
                    "total_revenue": round(ig_totals['revenue'], 2),
                    "total_conversions": ig_totals['conversions'],
                    "average_ctr": round(ig_avg_ctr, 2),
                    "average_roas": round(ig_avg_roas, 2)
                }
            },
            "insights": {
                "better_ctr_platform": "facebook" if fb_avg_ctr > ig_avg_ctr else "instagram",
                "better_roas_platform": "facebook" if fb_avg_roas > ig_avg_roas else "instagram",
                "total_spend_difference": round(abs(fb_totals['spend'] - ig_totals['spend']), 2),
                "total_revenue_difference": round(abs(fb_totals['revenue'] - ig_totals['revenue']), 2)
            }
        }
        
        logger.info("Successfully completed platform performance comparison")
        return str(result)
        
    except Exception as e:
        error_msg = f"Failed to compare platform performance: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@tool
def get_top_performing_campaigns(
    platform: str = "all",
    metric: str = "roas",
    limit: int = 10
) -> str:
    """
    Get the top performing campaigns based on a specific metric.
    
    Use this tool to identify the best performing campaigns for optimization insights.
    
    Args:
        platform: Platform filter - 'facebook', 'instagram', or 'all' (default: 'all')
        metric: Metric to rank by - 'roas', 'ctr', 'revenue', 'conversions', or 'engagement_rate' (default: 'roas')
        limit: Number of campaigns to return (default: 10, max: 25)
        
    Returns:
        JSON string containing top performing campaigns ranked by the specified metric
    """
    try:
        logger.info(f"Fetching top performing campaigns: platform={platform}, metric={metric}")
        
        # Build query
        query = supabase.table('campaigns').select('*')
        
        if platform != "all":
            query = query.eq('platform', platform)
        
        # Apply limit
        limit = min(limit, 25)
        
        # Order by metric (descending)
        if metric == "roas":
            query = query.order('roas', desc=True)
        elif metric == "ctr":
            query = query.order('ctr', desc=True)
        elif metric == "revenue":
            query = query.order('revenue', desc=True)
        elif metric == "conversions":
            query = query.order('conversions', desc=True)
        elif metric == "engagement_rate":
            query = query.order('engagement_rate', desc=True)
        else:
            return f"Error: Invalid metric '{metric}'. Use 'roas', 'ctr', 'revenue', 'conversions', or 'engagement_rate'"
        
        query = query.limit(limit)
        
        # Execute query
        response = query.execute()
        campaigns = response.data or []
        
        # Format response
        result = {
            "ranking_criteria": {
                "platform": platform,
                "metric": metric,
                "limit": limit
            },
            "top_campaigns": []
        }
        
        for i, campaign in enumerate(campaigns, 1):
            campaign_data = {
                "rank": i,
                "campaign_id": campaign['campaign_id'],
                "name": campaign['name'],
                "platform": campaign['platform'],
                "status": campaign['status'],
                "ranking_metric_value": campaign.get(metric, 0),
                "key_metrics": {
                    "roas": campaign['roas'],
                    "ctr": campaign['ctr'],
                    "revenue": campaign['revenue'],
                    "conversions": campaign['conversions'],
                    "engagement_rate": campaign['engagement_rate']
                },
                "budget_efficiency": {
                    "budget_amount": campaign['budget_amount'],
                    "spend_amount": campaign['spend_amount'],
                    "budget_utilization": round((campaign['spend_amount'] / campaign['budget_amount'] * 100), 2) if campaign['budget_amount'] > 0 else 0
                }
            }
            result["top_campaigns"].append(campaign_data)
        
        logger.info(f"Successfully retrieved {len(campaigns)} top performing campaigns")
        return str(result)
        
    except Exception as e:
        error_msg = f"Failed to get top performing campaigns: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


def get_analytics_tools():
    """Get all analytics API tools."""
    return [
        get_campaign_analytics,
        get_platform_performance_comparison,
        get_top_performing_campaigns
    ] 