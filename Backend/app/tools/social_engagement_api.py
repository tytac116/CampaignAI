"""
Social Engagement API Tools for Facebook and Instagram campaigns.

This tool provides social engagement analysis capabilities including
comments, sentiment analysis, and user interaction insights.
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
def get_campaign_comments(
    campaign_id: str,
    sentiment_filter: str = "all",
    limit: int = 20
) -> str:
    """
    Get comments and engagement data for a specific campaign.
    
    Use this tool to analyze user comments, sentiment, and engagement patterns for a campaign.
    
    Args:
        campaign_id: The campaign ID to retrieve comments for (works for both Facebook and Instagram)
        sentiment_filter: Filter by sentiment - 'positive', 'negative', 'neutral', or 'all' (default: 'all')
        limit: Maximum number of comments to return (default: 20, max: 100)
        
    Returns:
        JSON string containing comments and engagement analysis
    """
    try:
        logger.info(f"Fetching comments for campaign: {campaign_id}")
        
        # Get campaign info
        campaign_response = supabase.table('campaigns').select('*').eq('campaign_id', campaign_id).execute()
        
        if not campaign_response.data:
            return f"Error: Campaign '{campaign_id}' not found"
        
        campaign = campaign_response.data[0]
        
        # Build comments query
        comments_query = supabase.table('campaign_comments').select('*').eq('campaign_id', campaign_id)
        
        # Apply sentiment filter
        if sentiment_filter != "all":
            if sentiment_filter == "positive":
                comments_query = comments_query.gte('sentiment_score', 0.1)
            elif sentiment_filter == "negative":
                comments_query = comments_query.lt('sentiment_score', -0.1)
            else:  # neutral
                comments_query = comments_query.gte('sentiment_score', -0.1).lt('sentiment_score', 0.1)
        
        # Apply limit and order
        limit = min(limit, 100)
        comments_query = comments_query.order('created_at', desc=True).limit(limit)
        
        # Execute query
        comments_response = comments_query.execute()
        comments = comments_response.data or []
        
        # Calculate sentiment distribution
        all_comments_response = supabase.table('campaign_comments').select('sentiment_score').eq('campaign_id', campaign_id).execute()
        all_comments = all_comments_response.data or []
        
        positive_count = sum(1 for c in all_comments if c['sentiment_score'] > 0.1)
        negative_count = sum(1 for c in all_comments if c['sentiment_score'] < -0.1)
        neutral_count = len(all_comments) - positive_count - negative_count
        
        # Format response
        result = {
            "campaign_id": campaign_id,
            "campaign_name": campaign['name'],
            "platform": campaign['platform'],
            "engagement_summary": {
                "total_comments": len(all_comments),
                "comments_returned": len(comments),
                "sentiment_filter": sentiment_filter,
                "sentiment_distribution": {
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count,
                    "positive_percentage": round((positive_count / len(all_comments) * 100), 1) if all_comments else 0,
                    "negative_percentage": round((negative_count / len(all_comments) * 100), 1) if all_comments else 0
                },
                "overall_sentiment": campaign['overall_sentiment'],
                "average_sentiment_score": campaign['sentiment_score']
            },
            "comments": []
        }
        
        for comment in comments:
            # Determine sentiment label
            sentiment_score = comment['sentiment_score']
            if sentiment_score > 0.1:
                sentiment_label = "positive"
            elif sentiment_score < -0.1:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
            
            comment_data = {
                "comment_id": comment['comment_id'],
                "username": comment['username'],
                "comment_text": comment['comment_text'],
                "sentiment": {
                    "score": sentiment_score,
                    "label": sentiment_label
                },
                "engagement": {
                    "likes": comment['likes'],
                    "replies": comment.get('replies', 0)
                },
                "created_at": comment['created_at']
            }
            result["comments"].append(comment_data)
        
        logger.info(f"Successfully retrieved {len(comments)} comments for campaign: {campaign_id}")
        return str(result)
        
    except Exception as e:
        error_msg = f"Failed to get campaign comments: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@tool
def analyze_sentiment_trends(
    platform: str = "all",
    date_range: str = "last_30_days",
    limit: int = 50
) -> str:
    """
    Analyze sentiment trends across campaigns and platforms.
    
    Use this tool to identify sentiment patterns and trends for optimization insights.
    
    Args:
        platform: Platform filter - 'facebook', 'instagram', or 'all' (default: 'all')
        date_range: Time period - 'last_7_days', 'last_30_days', 'last_90_days' (default: 'last_30_days')
        limit: Number of campaigns to analyze (default: 50, max: 100)
        
    Returns:
        JSON string containing sentiment trend analysis
    """
    try:
        logger.info(f"Analyzing sentiment trends: platform={platform}, date_range={date_range}")
        
        # Calculate date range
        end_date = datetime.now().date()
        if date_range == "last_7_days":
            start_date = end_date - timedelta(days=7)
        elif date_range == "last_30_days":
            start_date = end_date - timedelta(days=30)
        else:  # last_90_days
            start_date = end_date - timedelta(days=90)
        
        # Get campaigns
        campaigns_query = supabase.table('campaigns').select('*')
        
        if platform != "all":
            campaigns_query = campaigns_query.eq('platform', platform)
        
        limit = min(limit, 100)
        campaigns_response = campaigns_query.limit(limit).execute()
        campaigns = campaigns_response.data or []
        
        if not campaigns:
            return "Error: No campaigns found for sentiment analysis"
        
        # Get comments for these campaigns within date range
        campaign_ids = [c['campaign_id'] for c in campaigns]
        comments_response = supabase.table('campaign_comments').select('*').in_('campaign_id', campaign_ids).gte('created_at', start_date.isoformat()).execute()
        comments = comments_response.data or []
        
        # Analyze sentiment by campaign
        campaign_sentiment = {}
        for campaign in campaigns:
            campaign_id = campaign['campaign_id']
            campaign_comments = [c for c in comments if c['campaign_id'] == campaign_id]
            
            if not campaign_comments:
                continue
            
            positive = sum(1 for c in campaign_comments if c['sentiment_score'] > 0.1)
            negative = sum(1 for c in campaign_comments if c['sentiment_score'] < -0.1)
            neutral = len(campaign_comments) - positive - negative
            avg_sentiment = sum(c['sentiment_score'] for c in campaign_comments) / len(campaign_comments)
            
            campaign_sentiment[campaign_id] = {
                "campaign_name": campaign['name'],
                "platform": campaign['platform'],
                "total_comments": len(campaign_comments),
                "positive_comments": positive,
                "negative_comments": negative,
                "neutral_comments": neutral,
                "average_sentiment": round(avg_sentiment, 3),
                "sentiment_distribution": {
                    "positive_percentage": round((positive / len(campaign_comments) * 100), 1),
                    "negative_percentage": round((negative / len(campaign_comments) * 100), 1),
                    "neutral_percentage": round((neutral / len(campaign_comments) * 100), 1)
                },
                "performance_metrics": {
                    "roas": campaign['roas'],
                    "engagement_rate": campaign['engagement_rate'],
                    "total_engagement": campaign['total_engagement']
                }
            }
        
        # Calculate overall trends
        all_sentiment_scores = [c['sentiment_score'] for c in comments]
        overall_positive = sum(1 for score in all_sentiment_scores if score > 0.1)
        overall_negative = sum(1 for score in all_sentiment_scores if score < -0.1)
        overall_neutral = len(all_sentiment_scores) - overall_positive - overall_negative
        
        # Platform comparison
        platform_sentiment = {}
        if platform == "all":
            for plt in ['facebook', 'instagram']:
                plt_comments = [c for c in comments if any(camp['platform'] == plt and camp['campaign_id'] == c['campaign_id'] for camp in campaigns)]
                if plt_comments:
                    plt_positive = sum(1 for c in plt_comments if c['sentiment_score'] > 0.1)
                    plt_negative = sum(1 for c in plt_comments if c['sentiment_score'] < -0.1)
                    plt_avg = sum(c['sentiment_score'] for c in plt_comments) / len(plt_comments)
                    
                    platform_sentiment[plt] = {
                        "total_comments": len(plt_comments),
                        "positive_percentage": round((plt_positive / len(plt_comments) * 100), 1),
                        "negative_percentage": round((plt_negative / len(plt_comments) * 100), 1),
                        "average_sentiment": round(plt_avg, 3)
                    }
        
        # Format response
        result = {
            "analysis_period": {
                "date_range": date_range,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "campaigns_analyzed": len(campaigns),
                "total_comments_analyzed": len(comments)
            },
            "overall_sentiment": {
                "total_comments": len(all_sentiment_scores),
                "positive_comments": overall_positive,
                "negative_comments": overall_negative,
                "neutral_comments": overall_neutral,
                "positive_percentage": round((overall_positive / len(all_sentiment_scores) * 100), 1) if all_sentiment_scores else 0,
                "negative_percentage": round((overall_negative / len(all_sentiment_scores) * 100), 1) if all_sentiment_scores else 0,
                "average_sentiment": round(sum(all_sentiment_scores) / len(all_sentiment_scores), 3) if all_sentiment_scores else 0
            },
            "platform_comparison": platform_sentiment,
            "campaign_sentiment_analysis": dict(list(campaign_sentiment.items())[:20]),  # Top 20 campaigns
            "insights": {
                "most_positive_campaigns": sorted(campaign_sentiment.items(), key=lambda x: x[1]['average_sentiment'], reverse=True)[:5],
                "most_negative_campaigns": sorted(campaign_sentiment.items(), key=lambda x: x[1]['average_sentiment'])[:5],
                "highest_engagement_positive": sorted([c for c in campaign_sentiment.items() if c[1]['average_sentiment'] > 0], key=lambda x: x[1]['performance_metrics']['engagement_rate'], reverse=True)[:3]
            }
        }
        
        logger.info(f"Successfully analyzed sentiment trends for {len(comments)} comments")
        return str(result)
        
    except Exception as e:
        error_msg = f"Failed to analyze sentiment trends: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@tool
def get_engagement_insights(
    campaign_id: str
) -> str:
    """
    Get comprehensive engagement insights for a specific campaign.
    
    Use this tool to analyze all engagement metrics including likes, shares, comments, and user interactions.
    
    Args:
        campaign_id: The campaign ID to analyze engagement for (works for both Facebook and Instagram)
        
    Returns:
        JSON string containing comprehensive engagement analysis
    """
    try:
        logger.info(f"Analyzing engagement for campaign: {campaign_id}")
        
        # Get campaign data
        campaign_response = supabase.table('campaigns').select('*').eq('campaign_id', campaign_id).execute()
        
        if not campaign_response.data:
            return f"Error: Campaign '{campaign_id}' not found"
        
        campaign = campaign_response.data[0]
        
        # Get comments data
        comments_response = supabase.table('campaign_comments').select('*').eq('campaign_id', campaign_id).execute()
        comments = comments_response.data or []
        
        # Get daily metrics
        metrics_response = supabase.table('campaign_metrics').select('*').eq('campaign_id', campaign_id).order('metric_date').execute()
        daily_metrics = metrics_response.data or []
        
        # Calculate engagement insights
        total_comment_likes = sum(c['likes'] for c in comments)
        total_comment_replies = sum(c.get('replies', 0) for c in comments)
        
        # Engagement rate calculation
        total_impressions = campaign['impressions']
        total_engagement = campaign['total_engagement']
        engagement_rate = (total_engagement / total_impressions * 100) if total_impressions > 0 else 0
        
        # Comment engagement rate
        comment_engagement_rate = (len(comments) / total_impressions * 100) if total_impressions > 0 else 0
        
        # Daily engagement trends
        daily_engagement = []
        for metric in daily_metrics:
            daily_total = metric['likes'] + metric['shares'] + metric['saves']
            daily_rate = (daily_total / metric['impressions'] * 100) if metric['impressions'] > 0 else 0
            
            daily_engagement.append({
                "date": metric['metric_date'],
                "impressions": metric['impressions'],
                "likes": metric['likes'],
                "shares": metric['shares'],
                "saves": metric['saves'],
                "total_engagement": daily_total,
                "engagement_rate": round(daily_rate, 2)
            })
        
        # Top engaging comments
        top_comments = sorted(comments, key=lambda x: x['likes'], reverse=True)[:5]
        
        # Format response
        result = {
            "campaign_id": campaign_id,
            "campaign_name": campaign['name'],
            "platform": campaign['platform'],
            "campaign_status": campaign['status'],
            "engagement_overview": {
                "total_impressions": total_impressions,
                "total_engagement": total_engagement,
                "engagement_rate": round(engagement_rate, 2),
                "engagement_breakdown": {
                    "likes": campaign['likes'],
                    "shares": campaign['shares'],
                    "saves": campaign['saves'],
                    "comments": len(comments),
                    "profile_visits": campaign['profile_visits'],
                    "website_clicks": campaign['website_clicks']
                }
            },
            "comment_analysis": {
                "total_comments": len(comments),
                "comment_engagement_rate": round(comment_engagement_rate, 4),
                "total_comment_likes": total_comment_likes,
                "total_comment_replies": total_comment_replies,
                "average_likes_per_comment": round(total_comment_likes / len(comments), 1) if comments else 0,
                "sentiment_summary": {
                    "overall_sentiment": campaign['overall_sentiment'],
                    "sentiment_score": campaign['sentiment_score'],
                    "positive_comments": campaign['positive_comments'],
                    "negative_comments": campaign['negative_comments'],
                    "neutral_comments": campaign.get('neutral_comments', 0)
                }
            },
            "performance_metrics": {
                "click_through_rate": campaign['ctr'],
                "cost_per_engagement": round(campaign['spend_amount'] / total_engagement, 2) if total_engagement > 0 else 0,
                "return_on_ad_spend": campaign['roas'],
                "cost_per_click": campaign['cpc']
            },
            "daily_engagement_trends": daily_engagement,
            "top_engaging_comments": [
                {
                    "comment_text": comment['comment_text'][:100] + "..." if len(comment['comment_text']) > 100 else comment['comment_text'],
                    "likes": comment['likes'],
                    "sentiment_score": comment['sentiment_score'],
                    "username": comment['username']
                }
                for comment in top_comments
            ],
            "optimization_insights": {
                "engagement_vs_industry_avg": "above_average" if engagement_rate > 3.0 else "below_average",
                "best_performing_content_type": campaign['campaign_type'],
                "sentiment_health": "healthy" if campaign['sentiment_score'] > 0.2 else "needs_attention",
                "comment_moderation_needed": len([c for c in comments if c['sentiment_score'] < -0.5]) > 0
            }
        }
        
        logger.info(f"Successfully analyzed engagement for campaign: {campaign_id}")
        return str(result)
        
    except Exception as e:
        error_msg = f"Failed to analyze engagement: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


def get_social_engagement_tools():
    """Get all social engagement API tools."""
    return [
        get_campaign_comments,
        analyze_sentiment_trends,
        get_engagement_insights
    ] 