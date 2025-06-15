"""
Content Management API Tools for Facebook and Instagram campaigns.

This tool provides content analysis and management capabilities
for both Facebook and Instagram campaigns using content data.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
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
def get_campaign_content(
    campaign_id: str
) -> str:
    """
    Get detailed content information for a specific campaign.
    
    Use this tool to analyze campaign content including titles, descriptions, hashtags, and creative elements.
    
    Args:
        campaign_id: The campaign ID to retrieve content for (works for both Facebook and Instagram)
        
    Returns:
        JSON string containing detailed content information
    """
    try:
        logger.info(f"Fetching content for campaign: {campaign_id}")
        
        # Get campaign content
        content_response = supabase.table('campaign_content').select('*').eq('campaign_id', campaign_id).execute()
        
        if not content_response.data:
            return f"Error: Content for campaign '{campaign_id}' not found"
        
        content = content_response.data[0]
        
        # Get campaign basic info
        campaign_response = supabase.table('campaigns').select('platform, name, status').eq('campaign_id', campaign_id).execute()
        campaign_info = campaign_response.data[0] if campaign_response.data else {}
        
        # Format response
        result = {
            "campaign_id": campaign_id,
            "campaign_name": campaign_info.get('name', 'Unknown'),
            "platform": campaign_info.get('platform', 'Unknown'),
            "campaign_status": campaign_info.get('status', 'Unknown'),
            "content_details": {
                "campaign_type": content['campaign_type'],
                "title": content['title'],
                "description": content['description'],
                "hashtags": content.get('hashtags', []),
                "created_at": content['created_at']
            },
            "creative_elements": {}
        }
        
        # Add type-specific content based on campaign type
        campaign_type = content['campaign_type']
        
        if campaign_type == "demo_video":
            result["creative_elements"] = {
                "type": "demo_video",
                "video_transcript": content.get('video_transcript', ''),
                "video_duration": content.get('video_duration', ''),
                "demo_features": content.get('demo_features', ''),
                "demo_duration": content.get('demo_duration', '')
            }
        elif campaign_type == "carousel":
            result["creative_elements"] = {
                "type": "carousel",
                "carousel_slides": content.get('carousel_slides', [])
            }
        elif campaign_type == "story":
            result["creative_elements"] = {
                "type": "story",
                "story_elements": content.get('story_elements', [])
            }
        elif campaign_type == "reel":
            result["creative_elements"] = {
                "type": "reel",
                "reel_script": content.get('reel_script', ''),
                "music_track": content.get('music_track', '')
            }
        elif campaign_type == "podcast":
            result["creative_elements"] = {
                "type": "podcast",
                "episode_topic": content.get('episode_topic', ''),
                "guest_name": content.get('guest_name', ''),
                "episode_duration": content.get('episode_duration', '')
            }
        elif campaign_type == "infographic":
            result["creative_elements"] = {
                "type": "infographic",
                "infographic_data": content.get('infographic_data', '')
            }
        elif campaign_type == "live_stream":
            result["creative_elements"] = {
                "type": "live_stream",
                "live_topic": content.get('live_topic', ''),
                "expected_viewers": content.get('expected_viewers', '')
            }
        elif campaign_type == "testimonial":
            result["creative_elements"] = {
                "type": "testimonial",
                "testimonial_quote": content.get('testimonial_quote', ''),
                "customer_name": content.get('customer_name', ''),
                "business_type": content.get('business_type', '')
            }
        else:  # image or other
            result["creative_elements"] = {
                "type": "image",
                "image_description": content.get('image_description', ''),
                "image_dimensions": content.get('image_dimensions', '')
            }
        
        logger.info(f"Successfully retrieved content for campaign: {campaign_id}")
        return str(result)
        
    except Exception as e:
        error_msg = f"Failed to get campaign content: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@tool
def analyze_content_performance(
    platform: str = "all",
    content_type: str = "all",
    limit: int = 10
) -> str:
    """
    Analyze content performance across different content types and platforms.
    
    Use this tool to identify which content types perform best for optimization insights.
    
    Args:
        platform: Platform filter - 'facebook', 'instagram', or 'all' (default: 'all')
        content_type: Content type filter - 'demo_video', 'carousel', 'story', 'reel', 'image', or 'all' (default: 'all')
        limit: Number of campaigns to analyze (default: 10, max: 50)
        
    Returns:
        JSON string containing content performance analysis
    """
    try:
        logger.info(f"Analyzing content performance: platform={platform}, content_type={content_type}")
        
        # Build query for campaigns
        query = supabase.table('campaigns').select('*')
        
        if platform != "all":
            query = query.eq('platform', platform)
        
        # Apply limit
        limit = min(limit, 50)
        query = query.limit(limit)
        
        # Execute query
        campaigns_response = query.execute()
        campaigns = campaigns_response.data or []
        
        # Get content data for these campaigns
        campaign_ids = [c['campaign_id'] for c in campaigns]
        
        if not campaign_ids:
            return "Error: No campaigns found for analysis"
        
        # Get content data
        content_query = supabase.table('campaign_content').select('*').in_('campaign_id', campaign_ids)
        
        if content_type != "all":
            content_query = content_query.eq('campaign_type', content_type)
        
        content_response = content_query.execute()
        content_data = content_response.data or []
        
        # Create campaign lookup
        campaign_lookup = {c['campaign_id']: c for c in campaigns}
        
        # Analyze performance by content type
        content_performance = {}
        
        for content in content_data:
            campaign_id = content['campaign_id']
            campaign = campaign_lookup.get(campaign_id)
            
            if not campaign:
                continue
            
            content_type_key = content['campaign_type']
            
            if content_type_key not in content_performance:
                content_performance[content_type_key] = {
                    "count": 0,
                    "total_impressions": 0,
                    "total_clicks": 0,
                    "total_conversions": 0,
                    "total_revenue": 0,
                    "total_engagement": 0,
                    "campaigns": []
                }
            
            perf = content_performance[content_type_key]
            perf["count"] += 1
            perf["total_impressions"] += campaign['impressions']
            perf["total_clicks"] += campaign['clicks']
            perf["total_conversions"] += campaign['conversions']
            perf["total_revenue"] += campaign['revenue']
            perf["total_engagement"] += campaign['total_engagement']
            
            perf["campaigns"].append({
                "campaign_id": campaign_id,
                "name": campaign['name'],
                "platform": campaign['platform'],
                "roas": campaign['roas'],
                "engagement_rate": campaign['engagement_rate']
            })
        
        # Calculate averages and format results
        result = {
            "analysis_criteria": {
                "platform": platform,
                "content_type_filter": content_type,
                "campaigns_analyzed": len(campaigns),
                "content_items_found": len(content_data)
            },
            "content_type_performance": {}
        }
        
        for content_type_key, perf in content_performance.items():
            avg_impressions = perf["total_impressions"] / perf["count"] if perf["count"] > 0 else 0
            avg_clicks = perf["total_clicks"] / perf["count"] if perf["count"] > 0 else 0
            avg_ctr = (perf["total_clicks"] / perf["total_impressions"] * 100) if perf["total_impressions"] > 0 else 0
            avg_revenue = perf["total_revenue"] / perf["count"] if perf["count"] > 0 else 0
            avg_engagement = perf["total_engagement"] / perf["count"] if perf["count"] > 0 else 0
            
            result["content_type_performance"][content_type_key] = {
                "campaign_count": perf["count"],
                "total_metrics": {
                    "impressions": perf["total_impressions"],
                    "clicks": perf["total_clicks"],
                    "conversions": perf["total_conversions"],
                    "revenue": round(perf["total_revenue"], 2),
                    "engagement": perf["total_engagement"]
                },
                "average_metrics": {
                    "impressions": round(avg_impressions, 0),
                    "clicks": round(avg_clicks, 0),
                    "ctr": round(avg_ctr, 2),
                    "revenue": round(avg_revenue, 2),
                    "engagement": round(avg_engagement, 0)
                },
                "top_campaigns": sorted(perf["campaigns"], key=lambda x: x["roas"], reverse=True)[:3]
            }
        
        logger.info(f"Successfully analyzed content performance for {len(content_data)} content items")
        return str(result)
        
    except Exception as e:
        error_msg = f"Failed to analyze content performance: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@tool
def get_hashtag_analysis(
    platform: str = "all",
    limit: int = 20
) -> str:
    """
    Analyze hashtag usage and performance across campaigns.
    
    Use this tool to identify the most effective hashtags for campaign optimization.
    
    Args:
        platform: Platform filter - 'facebook', 'instagram', or 'all' (default: 'all')
        limit: Number of campaigns to analyze (default: 20, max: 100)
        
    Returns:
        JSON string containing hashtag analysis and recommendations
    """
    try:
        logger.info(f"Analyzing hashtag performance: platform={platform}")
        
        # Build query for campaigns
        query = supabase.table('campaigns').select('campaign_id, platform, name, roas, engagement_rate, total_engagement')
        
        if platform != "all":
            query = query.eq('platform', platform)
        
        # Apply limit
        limit = min(limit, 100)
        query = query.limit(limit)
        
        # Execute query
        campaigns_response = query.execute()
        campaigns = campaigns_response.data or []
        
        if not campaigns:
            return "Error: No campaigns found for hashtag analysis"
        
        # Get content data with hashtags
        campaign_ids = [c['campaign_id'] for c in campaigns]
        content_response = supabase.table('campaign_content').select('campaign_id, hashtags').in_('campaign_id', campaign_ids).execute()
        content_data = content_response.data or []
        
        # Create campaign lookup
        campaign_lookup = {c['campaign_id']: c for c in campaigns}
        
        # Analyze hashtags
        hashtag_performance = {}
        
        for content in content_data:
            campaign_id = content['campaign_id']
            campaign = campaign_lookup.get(campaign_id)
            
            if not campaign or not content.get('hashtags'):
                continue
            
            hashtags = content['hashtags']
            if isinstance(hashtags, str):
                # Handle string format
                import json
                try:
                    hashtags = json.loads(hashtags)
                except:
                    hashtags = hashtags.split(',') if ',' in hashtags else [hashtags]
            
            for hashtag in hashtags:
                hashtag = hashtag.strip().lower()
                if not hashtag.startswith('#'):
                    hashtag = '#' + hashtag
                
                if hashtag not in hashtag_performance:
                    hashtag_performance[hashtag] = {
                        "usage_count": 0,
                        "total_roas": 0,
                        "total_engagement": 0,
                        "campaigns": []
                    }
                
                perf = hashtag_performance[hashtag]
                perf["usage_count"] += 1
                perf["total_roas"] += campaign['roas']
                perf["total_engagement"] += campaign['total_engagement']
                perf["campaigns"].append({
                    "campaign_id": campaign_id,
                    "name": campaign['name'],
                    "platform": campaign['platform'],
                    "roas": campaign['roas'],
                    "engagement": campaign['total_engagement']
                })
        
        # Calculate averages and sort
        hashtag_results = []
        for hashtag, perf in hashtag_performance.items():
            avg_roas = perf["total_roas"] / perf["usage_count"] if perf["usage_count"] > 0 else 0
            avg_engagement = perf["total_engagement"] / perf["usage_count"] if perf["usage_count"] > 0 else 0
            
            hashtag_results.append({
                "hashtag": hashtag,
                "usage_count": perf["usage_count"],
                "average_roas": round(avg_roas, 2),
                "average_engagement": round(avg_engagement, 0),
                "total_engagement": perf["total_engagement"],
                "performance_score": round((avg_roas * 0.6) + (avg_engagement * 0.4 / 1000), 2),  # Weighted score
                "top_campaigns": sorted(perf["campaigns"], key=lambda x: x["roas"], reverse=True)[:2]
            })
        
        # Sort by performance score
        hashtag_results.sort(key=lambda x: x["performance_score"], reverse=True)
        
        # Format response
        result = {
            "analysis_criteria": {
                "platform": platform,
                "campaigns_analyzed": len(campaigns),
                "unique_hashtags_found": len(hashtag_results)
            },
            "top_performing_hashtags": hashtag_results[:15],  # Top 15
            "recommendations": {
                "most_used": sorted(hashtag_results, key=lambda x: x["usage_count"], reverse=True)[:5],
                "highest_roas": sorted(hashtag_results, key=lambda x: x["average_roas"], reverse=True)[:5],
                "highest_engagement": sorted(hashtag_results, key=lambda x: x["average_engagement"], reverse=True)[:5]
            }
        }
        
        logger.info(f"Successfully analyzed {len(hashtag_results)} unique hashtags")
        return str(result)
        
    except Exception as e:
        error_msg = f"Failed to analyze hashtags: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


def get_content_management_tools():
    """Get all content management API tools."""
    return [
        get_campaign_content,
        analyze_content_performance,
        get_hashtag_analysis
    ] 