"""
Facebook Campaign Management API Tool for LangChain/LangGraph agents.

This tool simulates Facebook's Campaign Management API endpoints,
providing agents with the ability to manage Facebook campaigns.
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
def get_facebook_campaigns(
    limit: int = 10,
    status: str = "all",
    objective: str = "all"
) -> str:
    """
    Get Facebook campaigns with filtering options.
    
    Use this tool to retrieve Facebook campaign data for analysis and optimization.
    
    Args:
        limit: Maximum number of campaigns to return (default: 10, max: 50)
        status: Filter by campaign status - 'active', 'paused', 'archived', or 'all' (default: 'all')
        objective: Filter by campaign objective - 'engagement', 'conversions', 'traffic', or 'all' (default: 'all')
        
    Returns:
        JSON string containing Facebook campaign data with performance metrics
    """
    try:
        logger.info(f"Fetching Facebook campaigns: limit={limit}, status={status}, objective={objective}")
        
        # Build query
        query = supabase.table('campaigns').select('*').eq('platform', 'facebook')
        
        # Apply filters
        if status != "all":
            query = query.eq('status', status)
        
        if objective != "all":
            query = query.eq('objective', objective)
        
        # Apply limit (max 50 for safety)
        limit = min(limit, 50)
        query = query.limit(limit)
        
        # Execute query
        response = query.execute()
        campaigns = response.data or []
        
        # Format response
        result = {
            "platform": "facebook",
            "total_campaigns": len(campaigns),
            "filters_applied": {
                "status": status,
                "objective": objective,
                "limit": limit
            },
            "campaigns": []
        }
        
        for campaign in campaigns:
            campaign_data = {
                "campaign_id": campaign['campaign_id'],
                "name": campaign['name'],
                "status": campaign['status'],
                "objective": campaign['objective'],
                "campaign_type": campaign['campaign_type'],
                "budget": {
                    "type": campaign['budget_type'],
                    "amount": campaign['budget_amount'],
                    "spent": campaign['spend_amount'],
                    "remaining": campaign['remaining_budget']
                },
                "performance": {
                    "impressions": campaign['impressions'],
                    "clicks": campaign['clicks'],
                    "conversions": campaign['conversions'],
                    "revenue": campaign['revenue'],
                    "ctr": campaign['ctr'],
                    "cpc": campaign['cpc'],
                    "cpm": campaign['cpm'],
                    "roas": campaign['roas']
                },
                "engagement": {
                    "likes": campaign['likes'],
                    "shares": campaign['shares'],
                    "comments": campaign['comments_count'],
                    "total_engagement": campaign['total_engagement'],
                    "engagement_rate": campaign['engagement_rate']
                },
                "dates": {
                    "start_date": campaign['start_date'],
                    "end_date": campaign['end_date'],
                    "created_at": campaign['created_at']
                }
            }
            result["campaigns"].append(campaign_data)
        
        logger.info(f"Successfully retrieved {len(campaigns)} Facebook campaigns")
        return str(result)
        
    except Exception as e:
        error_msg = f"Failed to get Facebook campaigns: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@tool
def get_facebook_campaign_details(campaign_id: str) -> str:
    """
    Get detailed information for a specific Facebook campaign.
    
    Use this tool to get comprehensive details about a single Facebook campaign,
    including targeting, creative settings, and optimization status.
    
    Args:
        campaign_id: The Facebook campaign ID to retrieve details for
        
    Returns:
        JSON string containing detailed campaign information
    """
    try:
        logger.info(f"Fetching Facebook campaign details for: {campaign_id}")
        
        # Get campaign data
        response = supabase.table('campaigns').select('*').eq('campaign_id', campaign_id).eq('platform', 'facebook').execute()
        
        if not response.data:
            return f"Error: Facebook campaign '{campaign_id}' not found"
        
        campaign = response.data[0]
        
        # Format detailed response
        result = {
            "campaign_id": campaign['campaign_id'],
            "name": campaign['name'],
            "platform": "facebook",
            "status": campaign['status'],
            "objective": campaign['objective'],
            "campaign_type": campaign['campaign_type'],
            "budget_details": {
                "type": campaign['budget_type'],
                "daily_budget": campaign['budget_amount'],
                "total_spent": campaign['spend_amount'],
                "remaining_budget": campaign['remaining_budget']
            },
            "performance_metrics": {
                "impressions": campaign['impressions'],
                "clicks": campaign['clicks'],
                "conversions": campaign['conversions'],
                "revenue": campaign['revenue'],
                "ctr_percent": campaign['ctr'],
                "cost_per_click": campaign['cpc'],
                "cost_per_mille": campaign['cpm'],
                "cost_per_acquisition": campaign['cpa'],
                "return_on_ad_spend": campaign['roas']
            },
            "engagement_metrics": {
                "likes": campaign['likes'],
                "shares": campaign['shares'],
                "saves": campaign['saves'],
                "comments": campaign['comments_count'],
                "total_engagement": campaign['total_engagement'],
                "engagement_rate_percent": campaign['engagement_rate']
            },
            "sentiment_analysis": {
                "overall_sentiment": campaign['overall_sentiment'],
                "sentiment_score": campaign['sentiment_score'],
                "positive_comments": campaign['positive_comments'],
                "neutral_comments": campaign['neutral_comments'],
                "negative_comments": campaign['negative_comments']
            },
            "optimization": {
                "is_optimized": campaign['is_optimized'],
                "optimization_score": campaign['optimization_score'],
                "last_optimization_date": campaign.get('last_optimization_date')
            },
            "targeting": campaign.get('target_audience', {}),
            "creative": campaign.get('ad_creative', {}),
            "settings": campaign.get('campaign_settings', {}),
            "schedule": {
                "start_date": campaign['start_date'],
                "end_date": campaign['end_date'],
                "created_at": campaign['created_at'],
                "updated_at": campaign['updated_at']
            }
        }
        
        logger.info(f"Successfully retrieved details for Facebook campaign: {campaign_id}")
        return str(result)
        
    except Exception as e:
        error_msg = f"Failed to get Facebook campaign details: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@tool
def update_facebook_campaign(
    campaign_id: str,
    status: Optional[str] = None,
    budget_amount: Optional[float] = None,
    name: Optional[str] = None
) -> str:
    """
    Update a Facebook campaign's settings.
    
    Use this tool to modify Facebook campaign settings like status, budget, or name.
    
    Args:
        campaign_id: The Facebook campaign ID to update
        status: New campaign status - 'active', 'paused', or 'archived' (optional)
        budget_amount: New daily budget amount (optional)
        name: New campaign name (optional)
        
    Returns:
        JSON string confirming the update or error message
    """
    try:
        logger.info(f"Updating Facebook campaign: {campaign_id}")
        
        # Check if campaign exists
        response = supabase.table('campaigns').select('*').eq('campaign_id', campaign_id).eq('platform', 'facebook').execute()
        
        if not response.data:
            return f"Error: Facebook campaign '{campaign_id}' not found"
        
        # Build update data
        update_data = {"updated_at": datetime.utcnow().isoformat()}
        
        if status:
            if status not in ['active', 'paused', 'archived']:
                return "Error: Status must be 'active', 'paused', or 'archived'"
            update_data['status'] = status
        
        if budget_amount is not None:
            if budget_amount <= 0:
                return "Error: Budget amount must be greater than 0"
            update_data['budget_amount'] = budget_amount
        
        if name:
            update_data['name'] = name
        
        # Perform update
        update_response = supabase.table('campaigns').update(update_data).eq('campaign_id', campaign_id).eq('platform', 'facebook').execute()
        
        if update_response.data:
            result = {
                "success": True,
                "campaign_id": campaign_id,
                "platform": "facebook",
                "updated_fields": list(update_data.keys()),
                "message": f"Facebook campaign '{campaign_id}' updated successfully"
            }
            logger.info(f"Successfully updated Facebook campaign: {campaign_id}")
            return str(result)
        else:
            return f"Error: Failed to update Facebook campaign '{campaign_id}'"
        
    except Exception as e:
        error_msg = f"Failed to update Facebook campaign: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


def get_facebook_campaign_tools():
    """Get all Facebook campaign management tools."""
    return [
        get_facebook_campaigns,
        get_facebook_campaign_details,
        update_facebook_campaign
    ] 