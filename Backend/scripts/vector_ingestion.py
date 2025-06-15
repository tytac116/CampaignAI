"""
Vector Database Ingestion Script

This script loads campaign data from Supabase and upserts it into Pinecone
for vector-based retrieval by agents. Uses LangChain's Pinecone integration
with OpenAI embeddings.
"""

import os
import json
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv
from tqdm import tqdm
import time

from supabase import create_client, Client
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document

# Load environment variables
load_dotenv()

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vector_ingestion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CampaignVectorIngestion:
    """Handles ingestion of campaign data into Pinecone vector database."""
    
    def __init__(self):
        # Initialize Supabase client
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            dimensions=1536  # Standard dimensions for text-embedding-3-small
        )
        
        # Pinecone index name
        self.index_name = "campaign-optimization"
        
        # Progress tracking
        self.total_documents = 0
        self.processed_documents = 0
        
    def create_campaign_documents(self) -> List[Document]:
        """Create rich documents from campaign data for vector storage."""
        logger.info("🔄 Loading campaigns data from Supabase...")
        
        # Load campaigns with related data
        campaigns_result = self.supabase.table('campaigns').select('*').execute()
        campaigns = campaigns_result.data
        
        logger.info(f"📊 Found {len(campaigns)} campaigns to process")
        
        documents = []
        
        for i, campaign in enumerate(tqdm(campaigns, desc="Processing campaigns")):
            # Create rich text content for embedding with better structure
            content_parts = [
                f"CAMPAIGN OVERVIEW:",
                f"Campaign Name: {campaign['name']}",
                f"Platform: {campaign['platform'].upper()}",
                f"Status: {campaign['status'].upper()}",
                f"Objective: {campaign['objective']}",
                f"Campaign Type: {campaign['campaign_type']}",
                "",
                f"BUDGET & SPEND:",
                f"Budget: ${float(campaign['budget_amount']):,.2f}",
                f"Spend: ${float(campaign['spend_amount']):,.2f}",
                f"Remaining Budget: ${float(campaign['remaining_budget']):,.2f}",
                f"Budget Utilization: {(float(campaign['spend_amount'])/float(campaign['budget_amount'])*100):.1f}%",
                "",
                f"PERFORMANCE METRICS:",
                f"Impressions: {int(campaign['impressions']):,}",
                f"Clicks: {int(campaign['clicks']):,}",
                f"Click-Through Rate: {float(campaign['ctr']):.2f}%",
                f"Cost Per Click: ${float(campaign['cpc']):.2f}",
                f"Cost Per Mille: ${float(campaign['cpm']):.2f}",
                f"Conversions: {int(campaign['conversions']):,}",
                f"Cost Per Acquisition: ${float(campaign['cpa']):.2f}",
                f"Return on Ad Spend: {float(campaign['roas']):.2f}x",
                f"Revenue Generated: ${float(campaign['revenue']):,.2f}",
                "",
                f"ENGAGEMENT METRICS:",
                f"Likes: {int(campaign['likes']):,}",
                f"Shares: {int(campaign['shares']):,}",
                f"Saves: {int(campaign['saves']):,}",
                f"Comments: {int(campaign['comments_count']):,}",
                f"Total Engagement: {int(campaign['total_engagement']):,}",
                f"Engagement Rate: {float(campaign['engagement_rate']):.2f}%",
                "",
                f"SENTIMENT ANALYSIS:",
                f"Overall Sentiment: {campaign['overall_sentiment'].upper()}",
                f"Sentiment Score: {float(campaign['sentiment_score']):.2f}",
                f"Positive Comments: {int(campaign['positive_comments']):,}",
                f"Neutral Comments: {int(campaign['neutral_comments']):,}",
                f"Negative Comments: {int(campaign['negative_comments']):,}",
                "",
                f"ADDITIONAL METRICS:",
                f"Video Views: {int(campaign['video_views']):,}",
                f"Video Completion Rate: {float(campaign['video_completion_rate']):.2f}%",
                f"Profile Visits: {int(campaign['profile_visits']):,}",
                f"Website Clicks: {int(campaign['website_clicks']):,}",
                "",
                f"OPTIMIZATION:",
                f"Is Optimized: {'YES' if campaign['is_optimized'] else 'NO'}",
                f"Optimization Score: {float(campaign['optimization_score']):.2f}/100",
                "",
                f"TARGETING & CREATIVE:",
                f"Target Audience: {campaign['target_audience']}",
                f"Ad Creative Type: {campaign['ad_creative']}",
                f"Campaign Settings: {campaign['campaign_settings']}",
                "",
                f"TIMELINE:",
                f"Start Date: {campaign['start_date']}",
                f"End Date: {campaign['end_date']}",
                f"Created: {campaign['created_at']}",
                f"Last Updated: {campaign['updated_at']}"
            ]
            
            content = "\n".join(content_parts)
            
            # Create comprehensive metadata for filtering and retrieval
            metadata = {
                "doc_type": "campaign",
                "campaign_id": campaign['campaign_id'],
                "campaign_name": campaign['name'],
                "platform": campaign['platform'],
                "status": campaign['status'],
                "objective": campaign['objective'],
                "campaign_type": campaign['campaign_type'],
                "budget_amount": float(campaign['budget_amount']),
                "spend_amount": float(campaign['spend_amount']),
                "budget_utilization": float(campaign['spend_amount'])/float(campaign['budget_amount'])*100,
                "roas": float(campaign['roas']),
                "ctr": float(campaign['ctr']),
                "cpc": float(campaign['cpc']),
                "cpa": float(campaign['cpa']),
                "engagement_rate": float(campaign['engagement_rate']),
                "sentiment": campaign['overall_sentiment'],
                "sentiment_score": float(campaign['sentiment_score']),
                "optimization_score": float(campaign['optimization_score']),
                "is_optimized": bool(campaign['is_optimized']),
                "impressions": int(campaign['impressions']),
                "clicks": int(campaign['clicks']),
                "conversions": int(campaign['conversions']),
                "revenue": float(campaign['revenue']),
                "total_engagement": int(campaign['total_engagement']),
                "start_date": campaign['start_date'],
                "end_date": campaign['end_date'],
                "created_at": campaign['created_at'],
                "performance_tier": self._get_performance_tier(campaign),
                "budget_tier": self._get_budget_tier(campaign['budget_amount']),
                "engagement_tier": self._get_engagement_tier(campaign['engagement_rate'])
            }
            
            doc = Document(
                page_content=content,
                metadata=metadata
            )
            documents.append(doc)
            
            # Progress update
            self.processed_documents += 1
            if (i + 1) % 50 == 0:
                logger.info(f"✅ Processed {i + 1}/{len(campaigns)} campaigns")
            
        logger.info(f"✅ Created {len(documents)} campaign documents")
        return documents
    
    def create_content_documents(self) -> List[Document]:
        """Create documents from campaign content data."""
        logger.info("🔄 Loading campaign content data from Supabase...")
        
        content_result = self.supabase.table('campaign_content').select('*').execute()
        content_data = content_result.data
        
        logger.info(f"📊 Found {len(content_data)} content records to process")
        
        documents = []
        
        for i, content in enumerate(tqdm(content_data, desc="Processing content")):
            # Create rich content description with better structure
            content_parts = [
                f"CAMPAIGN CONTENT ANALYSIS:",
                f"Campaign ID: {content['campaign_id']}",
                f"Content Type: {content['campaign_type'].upper()}",
                "",
                f"CONTENT DETAILS:",
                f"Title: {content['title'] or 'Not specified'}",
                f"Description: {content['description'] or 'Not specified'}",
                f"Hashtags: {content['hashtags'] or 'None'}",
                ""
            ]
            
            # Add type-specific content with better formatting
            if content['video_transcript']:
                content_parts.extend([
                    f"VIDEO CONTENT:",
                    f"Transcript: {content['video_transcript']}",
                    f"Duration: {content['video_duration']} seconds" if content['video_duration'] else "Duration: Not specified"
                ])
                
            if content['image_description']:
                content_parts.extend([
                    f"IMAGE CONTENT:",
                    f"Description: {content['image_description']}",
                    f"Dimensions: {content['image_dimensions']}" if content['image_dimensions'] else "Dimensions: Not specified"
                ])
                
            if content['carousel_slides']:
                content_parts.extend([
                    f"CAROUSEL CONTENT:",
                    f"Slides: {content['carousel_slides']}"
                ])
                
            if content['story_elements']:
                content_parts.extend([
                    f"STORY CONTENT:",
                    f"Elements: {content['story_elements']}"
                ])
                
            if content['reel_script']:
                content_parts.extend([
                    f"REEL CONTENT:",
                    f"Script: {content['reel_script']}",
                    f"Music Track: {content['music_track']}" if content['music_track'] else "Music: Not specified"
                ])
                
            if content['episode_topic']:
                content_parts.extend([
                    f"PODCAST CONTENT:",
                    f"Topic: {content['episode_topic']}",
                    f"Guest: {content['guest_name']}" if content['guest_name'] else "Guest: None",
                    f"Duration: {content['episode_duration']} minutes" if content['episode_duration'] else "Duration: Not specified"
                ])
                
            if content['infographic_data']:
                content_parts.extend([
                    f"INFOGRAPHIC CONTENT:",
                    f"Data: {content['infographic_data']}"
                ])
                
            if content['live_topic']:
                content_parts.extend([
                    f"LIVE CONTENT:",
                    f"Topic: {content['live_topic']}",
                    f"Expected Viewers: {content['expected_viewers']}" if content['expected_viewers'] else "Expected Viewers: Not specified"
                ])
                
            if content['testimonial_quote']:
                content_parts.extend([
                    f"TESTIMONIAL CONTENT:",
                    f"Quote: {content['testimonial_quote']}",
                    f"Customer: {content['customer_name']}" if content['customer_name'] else "Customer: Anonymous",
                    f"Business Type: {content['business_type']}" if content['business_type'] else "Business: Not specified"
                ])
                
            if content['demo_features']:
                content_parts.extend([
                    f"DEMO CONTENT:",
                    f"Features: {content['demo_features']}",
                    f"Duration: {content['demo_duration']} minutes" if content['demo_duration'] else "Duration: Not specified"
                ])
            
            content_text = "\n".join(content_parts)
            
            metadata = {
                "doc_type": "content",
                "campaign_id": content['campaign_id'],
                "content_type": content['campaign_type'],
                "has_video": bool(content['video_transcript']),
                "has_image": bool(content['image_description']),
                "has_carousel": bool(content['carousel_slides']),
                "has_story": bool(content['story_elements']),
                "has_reel": bool(content['reel_script']),
                "has_podcast": bool(content['episode_topic']),
                "has_infographic": bool(content['infographic_data']),
                "has_live": bool(content['live_topic']),
                "has_testimonial": bool(content['testimonial_quote']),
                "has_demo": bool(content['demo_features']),
                "video_duration": content['video_duration'],
                "episode_duration": content['episode_duration'],
                "demo_duration": content['demo_duration'],
                "created_at": content['created_at'],
                "content_complexity": self._get_content_complexity(content)
            }
            
            doc = Document(
                page_content=content_text,
                metadata=metadata
            )
            documents.append(doc)
            
            # Progress update
            self.processed_documents += 1
            if (i + 1) % 50 == 0:
                logger.info(f"✅ Processed {i + 1}/{len(content_data)} content records")
            
        logger.info(f"✅ Created {len(documents)} content documents")
        return documents
    
    def create_metrics_documents(self) -> List[Document]:
        """Create documents from campaign metrics data."""
        logger.info("🔄 Loading campaign metrics data from Supabase...")
        
        # Get recent metrics (last 30 days) to avoid overwhelming the vector DB
        cutoff_date = (datetime.now().date() - timedelta(days=30)).isoformat()
        metrics_result = self.supabase.table('campaign_metrics')\
            .select('*')\
            .gte('metric_date', cutoff_date)\
            .execute()
        metrics_data = metrics_result.data
        
        logger.info(f"📊 Found {len(metrics_data)} metrics records (last 30 days) to process")
        
        # Group metrics by campaign for better context
        campaign_metrics = {}
        for metric in metrics_data:
            campaign_id = metric['campaign_id']
            if campaign_id not in campaign_metrics:
                campaign_metrics[campaign_id] = []
            campaign_metrics[campaign_id].append(metric)
        
        logger.info(f"📊 Grouped into {len(campaign_metrics)} campaigns")
        
        documents = []
        
        for i, (campaign_id, metrics) in enumerate(tqdm(campaign_metrics.items(), desc="Processing metrics")):
            # Calculate aggregated metrics with more detail
            total_impressions = sum(int(m['impressions']) for m in metrics)
            total_clicks = sum(int(m['clicks']) for m in metrics)
            total_spend = sum(float(m['spend']) for m in metrics)
            total_conversions = sum(int(m['conversions']) for m in metrics)
            total_revenue = sum(float(m['revenue']) for m in metrics)
            total_likes = sum(int(m['likes']) for m in metrics)
            total_shares = sum(int(m['shares']) for m in metrics)
            total_saves = sum(int(m['saves']) for m in metrics)
            total_comments = sum(int(m['comments_count']) for m in metrics)
            total_video_views = sum(int(m['video_views']) for m in metrics)
            total_profile_visits = sum(int(m['profile_visits']) for m in metrics)
            
            avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            avg_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
            avg_cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
            roas = (total_revenue / total_spend) if total_spend > 0 else 0
            
            # Calculate trends
            sorted_metrics = sorted(metrics, key=lambda x: x['metric_date'])
            trend_analysis = self._calculate_trends(sorted_metrics)
            
            content_parts = [
                f"CAMPAIGN METRICS ANALYSIS:",
                f"Campaign ID: {campaign_id}",
                f"Analysis Period: Last 30 days ({len(metrics)} data points)",
                f"Date Range: {sorted_metrics[0]['metric_date']} to {sorted_metrics[-1]['metric_date']}",
                "",
                f"PERFORMANCE SUMMARY:",
                f"Total Impressions: {total_impressions:,}",
                f"Total Clicks: {total_clicks:,}",
                f"Average CTR: {avg_ctr:.2f}%",
                f"Total Spend: ${total_spend:,.2f}",
                f"Average CPC: ${avg_cpc:.2f}",
                f"Total Conversions: {total_conversions:,}",
                f"Average CPA: ${avg_cpa:.2f}",
                f"Total Revenue: ${total_revenue:,.2f}",
                f"ROAS: {roas:.2f}x",
                "",
                f"ENGAGEMENT SUMMARY:",
                f"Total Likes: {total_likes:,}",
                f"Total Shares: {total_shares:,}",
                f"Total Saves: {total_saves:,}",
                f"Total Comments: {total_comments:,}",
                f"Total Video Views: {total_video_views:,}",
                f"Total Profile Visits: {total_profile_visits:,}",
                "",
                f"TREND ANALYSIS:",
                f"Impressions Trend: {trend_analysis['impressions_trend']}",
                f"Clicks Trend: {trend_analysis['clicks_trend']}",
                f"Spend Trend: {trend_analysis['spend_trend']}",
                f"Revenue Trend: {trend_analysis['revenue_trend']}",
                f"Performance Stability: {trend_analysis['stability']}",
                "",
                f"DAILY PERFORMANCE:",
                f"Best Performing Day: {trend_analysis['best_day']}",
                f"Worst Performing Day: {trend_analysis['worst_day']}",
                f"Average Daily Spend: ${total_spend/len(metrics):.2f}",
                f"Average Daily Revenue: ${total_revenue/len(metrics):.2f}"
            ]
            
            content_text = "\n".join(content_parts)
            
            metadata = {
                "doc_type": "metrics",
                "campaign_id": campaign_id,
                "days_of_data": len(metrics),
                "total_impressions": int(total_impressions),
                "total_clicks": int(total_clicks),
                "total_spend": float(total_spend),
                "total_conversions": int(total_conversions),
                "total_revenue": float(total_revenue),
                "avg_ctr": float(avg_ctr),
                "avg_cpc": float(avg_cpc),
                "avg_cpa": float(avg_cpa),
                "roas": float(roas),
                "date_range": "last_30_days",
                "start_date": sorted_metrics[0]['metric_date'],
                "end_date": sorted_metrics[-1]['metric_date'],
                "impressions_trend": trend_analysis['impressions_trend'],
                "revenue_trend": trend_analysis['revenue_trend'],
                "performance_stability": trend_analysis['stability'],
                "performance_tier": self._get_metrics_performance_tier(roas, avg_ctr)
            }
            
            doc = Document(
                page_content=content_text,
                metadata=metadata
            )
            documents.append(doc)
            
            # Progress update
            self.processed_documents += 1
            if (i + 1) % 10 == 0:
                logger.info(f"✅ Processed {i + 1}/{len(campaign_metrics)} metric summaries")
            
        logger.info(f"✅ Created {len(documents)} metrics documents")
        return documents
    
    def create_comments_documents(self) -> List[Document]:
        """Create documents from campaign comments data."""
        logger.info("🔄 Loading campaign comments data from Supabase...")
        
        comments_result = self.supabase.table('campaign_comments').select('*').execute()
        comments_data = comments_result.data
        
        logger.info(f"📊 Found {len(comments_data)} comments to process")
        
        # Group comments by campaign for better context
        campaign_comments = {}
        for comment in comments_data:
            campaign_id = comment['campaign_id']
            if campaign_id not in campaign_comments:
                campaign_comments[campaign_id] = []
            campaign_comments[campaign_id].append(comment)
        
        logger.info(f"📊 Grouped into {len(campaign_comments)} campaigns")
        
        documents = []
        
        for i, (campaign_id, comments) in enumerate(tqdm(campaign_comments.items(), desc="Processing comments")):
            # Analyze sentiment distribution with more detail
            positive_comments = [c for c in comments if float(c['sentiment_score']) > 0.1]
            neutral_comments = [c for c in comments if -0.1 <= float(c['sentiment_score']) <= 0.1]
            negative_comments = [c for c in comments if float(c['sentiment_score']) < -0.1]
            
            # Sample representative comments (more samples)
            sample_positive = positive_comments[:5] if positive_comments else []
            sample_negative = negative_comments[:5] if negative_comments else []
            sample_neutral = neutral_comments[:3] if neutral_comments else []
            
            # Calculate engagement metrics
            total_likes = sum(int(c['likes']) for c in comments)
            total_replies = sum(int(c['replies']) for c in comments)
            avg_sentiment = sum(float(c['sentiment_score']) for c in comments) / len(comments)
            
            # Identify key themes
            themes = self._extract_comment_themes(comments)
            
            content_parts = [
                f"CAMPAIGN COMMENTS ANALYSIS:",
                f"Campaign ID: {campaign_id}",
                f"Total Comments: {len(comments):,}",
                f"Analysis Date: {datetime.now().strftime('%Y-%m-%d')}",
                "",
                f"SENTIMENT DISTRIBUTION:",
                f"Positive Comments: {len(positive_comments):,} ({len(positive_comments)/len(comments)*100:.1f}%)",
                f"Neutral Comments: {len(neutral_comments):,} ({len(neutral_comments)/len(comments)*100:.1f}%)",
                f"Negative Comments: {len(negative_comments):,} ({len(negative_comments)/len(comments)*100:.1f}%)",
                f"Average Sentiment Score: {avg_sentiment:.3f}",
                f"Overall Sentiment: {self._get_overall_sentiment(avg_sentiment)}",
                "",
                f"ENGAGEMENT METRICS:",
                f"Total Comment Likes: {total_likes:,}",
                f"Total Comment Replies: {total_replies:,}",
                f"Average Likes per Comment: {total_likes/len(comments):.1f}",
                f"Average Replies per Comment: {total_replies/len(comments):.1f}",
                "",
                f"KEY THEMES IDENTIFIED:",
            ]
            
            for theme, count in themes.items():
                content_parts.append(f"- {theme}: {count} mentions")
            
            if sample_positive:
                content_parts.extend([
                    "",
                    f"SAMPLE POSITIVE COMMENTS:"
                ])
                for j, comment in enumerate(sample_positive, 1):
                    content_parts.append(f"{j}. \"{comment['comment_text'][:150]}...\" (Score: {float(comment['sentiment_score']):.2f}, Likes: {int(comment['likes'])})")
            
            if sample_negative:
                content_parts.extend([
                    "",
                    f"SAMPLE NEGATIVE COMMENTS:"
                ])
                for j, comment in enumerate(sample_negative, 1):
                    content_parts.append(f"{j}. \"{comment['comment_text'][:150]}...\" (Score: {float(comment['sentiment_score']):.2f}, Likes: {int(comment['likes'])})")
            
            if sample_neutral:
                content_parts.extend([
                    "",
                    f"SAMPLE NEUTRAL COMMENTS:"
                ])
                for j, comment in enumerate(sample_neutral, 1):
                    content_parts.append(f"{j}. \"{comment['comment_text'][:150]}...\" (Score: {float(comment['sentiment_score']):.2f})")
            
            content_text = "\n".join(content_parts)
            
            metadata = {
                "doc_type": "comments",
                "campaign_id": campaign_id,
                "total_comments": len(comments),
                "positive_comments": len(positive_comments),
                "neutral_comments": len(neutral_comments),
                "negative_comments": len(negative_comments),
                "positive_percentage": len(positive_comments)/len(comments)*100,
                "negative_percentage": len(negative_comments)/len(comments)*100,
                "avg_sentiment": float(avg_sentiment),
                "overall_sentiment": self._get_overall_sentiment(avg_sentiment),
                "total_likes": int(total_likes),
                "total_replies": int(total_replies),
                "avg_likes_per_comment": float(total_likes/len(comments)),
                "avg_replies_per_comment": float(total_replies/len(comments)),
                "sentiment_distribution": f"{len(positive_comments)}/{len(neutral_comments)}/{len(negative_comments)}",
                "engagement_level": self._get_comment_engagement_level(total_likes, total_replies, len(comments)),
                "key_themes": list(themes.keys())[:5]  # Top 5 themes
            }
            
            doc = Document(
                page_content=content_text,
                metadata=metadata
            )
            documents.append(doc)
            
            # Progress update
            self.processed_documents += 1
            if (i + 1) % 10 == 0:
                logger.info(f"✅ Processed {i + 1}/{len(campaign_comments)} comment analyses")
            
        logger.info(f"✅ Created {len(documents)} comments documents")
        return documents
    
    def _get_performance_tier(self, campaign: Dict) -> str:
        """Classify campaign performance tier."""
        roas = float(campaign['roas'])
        ctr = float(campaign['ctr'])
        
        if roas >= 4.0 and ctr >= 2.0:
            return "high_performer"
        elif roas >= 2.0 and ctr >= 1.0:
            return "medium_performer"
        else:
            return "low_performer"
    
    def _get_budget_tier(self, budget: float) -> str:
        """Classify budget tier."""
        budget = float(budget)
        if budget >= 10000:
            return "high_budget"
        elif budget >= 1000:
            return "medium_budget"
        else:
            return "low_budget"
    
    def _get_engagement_tier(self, engagement_rate: float) -> str:
        """Classify engagement tier."""
        engagement_rate = float(engagement_rate)
        if engagement_rate >= 5.0:
            return "high_engagement"
        elif engagement_rate >= 2.0:
            return "medium_engagement"
        else:
            return "low_engagement"
    
    def _get_content_complexity(self, content: Dict) -> str:
        """Determine content complexity based on elements."""
        complexity_score = 0
        if content['video_transcript']: complexity_score += 2
        if content['image_description']: complexity_score += 1
        if content['carousel_slides']: complexity_score += 2
        if content['story_elements']: complexity_score += 1
        if content['reel_script']: complexity_score += 2
        if content['episode_topic']: complexity_score += 3
        if content['infographic_data']: complexity_score += 2
        if content['live_topic']: complexity_score += 2
        if content['testimonial_quote']: complexity_score += 1
        if content['demo_features']: complexity_score += 2
        
        if complexity_score >= 5:
            return "high_complexity"
        elif complexity_score >= 2:
            return "medium_complexity"
        else:
            return "low_complexity"
    
    def _calculate_trends(self, sorted_metrics: List[Dict]) -> Dict:
        """Calculate performance trends."""
        if len(sorted_metrics) < 2:
            return {
                'impressions_trend': 'stable',
                'clicks_trend': 'stable',
                'spend_trend': 'stable',
                'revenue_trend': 'stable',
                'stability': 'insufficient_data',
                'best_day': sorted_metrics[0]['metric_date'],
                'worst_day': sorted_metrics[0]['metric_date']
            }
        
        # Calculate trends for key metrics
        impressions = [int(m['impressions']) for m in sorted_metrics]
        revenue = [float(m['revenue']) for m in sorted_metrics]
        
        impressions_trend = 'increasing' if impressions[-1] > impressions[0] else 'decreasing' if impressions[-1] < impressions[0] else 'stable'
        revenue_trend = 'increasing' if revenue[-1] > revenue[0] else 'decreasing' if revenue[-1] < revenue[0] else 'stable'
        
        # Find best and worst performing days
        best_day = max(sorted_metrics, key=lambda x: float(x['revenue']))['metric_date']
        worst_day = min(sorted_metrics, key=lambda x: float(x['revenue']))['metric_date']
        
        # Calculate stability (coefficient of variation for revenue)
        import statistics
        revenue_cv = statistics.stdev(revenue) / statistics.mean(revenue) if statistics.mean(revenue) > 0 else 0
        stability = 'stable' if revenue_cv < 0.3 else 'moderate' if revenue_cv < 0.6 else 'volatile'
        
        return {
            'impressions_trend': impressions_trend,
            'clicks_trend': 'stable',  # Simplified for now
            'spend_trend': 'stable',   # Simplified for now
            'revenue_trend': revenue_trend,
            'stability': stability,
            'best_day': best_day,
            'worst_day': worst_day
        }
    
    def _get_metrics_performance_tier(self, roas: float, ctr: float) -> str:
        """Get performance tier based on metrics."""
        if roas >= 4.0 and ctr >= 2.0:
            return "excellent"
        elif roas >= 2.5 and ctr >= 1.5:
            return "good"
        elif roas >= 1.5 and ctr >= 1.0:
            return "average"
        else:
            return "needs_improvement"
    
    def _get_overall_sentiment(self, avg_sentiment: float) -> str:
        """Get overall sentiment classification."""
        if avg_sentiment > 0.2:
            return "positive"
        elif avg_sentiment < -0.2:
            return "negative"
        else:
            return "neutral"
    
    def _extract_comment_themes(self, comments: List[Dict]) -> Dict[str, int]:
        """Extract key themes from comments (simplified)."""
        themes = {}
        keywords = {
            'product_quality': ['quality', 'good', 'excellent', 'amazing', 'perfect'],
            'price_value': ['price', 'expensive', 'cheap', 'value', 'worth'],
            'customer_service': ['service', 'support', 'help', 'staff', 'team'],
            'delivery_shipping': ['delivery', 'shipping', 'fast', 'slow', 'arrived'],
            'user_experience': ['easy', 'difficult', 'simple', 'complicated', 'user-friendly']
        }
        
        for comment in comments:
            text = comment['comment_text'].lower()
            for theme, words in keywords.items():
                if any(word in text for word in words):
                    themes[theme] = themes.get(theme, 0) + 1
        
        return dict(sorted(themes.items(), key=lambda x: x[1], reverse=True))
    
    def _get_comment_engagement_level(self, total_likes: int, total_replies: int, comment_count: int) -> str:
        """Determine comment engagement level."""
        engagement_score = (total_likes + total_replies * 2) / comment_count
        
        if engagement_score >= 5:
            return "high_engagement"
        elif engagement_score >= 2:
            return "medium_engagement"
        else:
            return "low_engagement"
    
    def ingest_all_data(self):
        """Main ingestion method that processes all data types."""
        logger.info("🚀 Starting vector database ingestion...")
        start_time = datetime.now()
        
        try:
            # Collect all documents
            all_documents = []
            
            logger.info("📋 Processing all data types...")
            
            # Add campaign documents
            campaign_docs = self.create_campaign_documents()
            all_documents.extend(campaign_docs)
            
            # Add content documents
            content_docs = self.create_content_documents()
            all_documents.extend(content_docs)
            
            # Add metrics documents
            metrics_docs = self.create_metrics_documents()
            all_documents.extend(metrics_docs)
            
            # Add comments documents
            comments_docs = self.create_comments_documents()
            all_documents.extend(comments_docs)
            
            self.total_documents = len(all_documents)
            logger.info(f"📊 Total documents prepared for ingestion: {self.total_documents}")
            
            # Create or connect to Pinecone vector store
            logger.info("🔗 Connecting to Pinecone and upserting documents...")
            logger.info(f"📍 Using index: {self.index_name}")
            
            # Process in smaller batches to avoid OpenAI token limits
            batch_size = 50  # Reduced batch size
            total_batches = (len(all_documents) + batch_size - 1) // batch_size
            
            logger.info(f"📦 Processing {total_batches} batches of {batch_size} documents each")
            
            # Initialize vector store with first batch
            first_batch = all_documents[:batch_size]
            logger.info(f"🔄 Processing batch 1/{total_batches} ({len(first_batch)} documents)")
            
            vector_store = PineconeVectorStore.from_documents(
                documents=first_batch,
                embedding=self.embeddings,
                index_name=self.index_name
            )
            
            # Process remaining batches
            for i in range(1, total_batches):
                start_idx = i * batch_size
                end_idx = min((i + 1) * batch_size, len(all_documents))
                batch = all_documents[start_idx:end_idx]
                
                logger.info(f"🔄 Processing batch {i+1}/{total_batches} ({len(batch)} documents)")
                
                # Add documents to existing vector store
                vector_store.add_documents(batch)
                
                # Small delay to avoid rate limits
                time.sleep(1)
            
            # Calculate processing time
            end_time = datetime.now()
            processing_time = end_time - start_time
            
            logger.info(f"✅ Successfully ingested {len(all_documents)} documents into Pinecone index '{self.index_name}'")
            logger.info(f"⏱️  Total processing time: {processing_time}")
            
            # Print detailed summary
            doc_types = {}
            for doc in all_documents:
                doc_type = doc.metadata.get('doc_type', 'unknown')
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            logger.info("📈 INGESTION SUMMARY:")
            logger.info("=" * 50)
            for doc_type, count in doc_types.items():
                logger.info(f"  📄 {doc_type.upper()}: {count:,} documents")
            logger.info("=" * 50)
            logger.info(f"  🎯 TOTAL: {len(all_documents):,} documents")
            logger.info(f"  ⚡ RATE: {len(all_documents)/processing_time.total_seconds():.1f} docs/second")
            logger.info(f"  💾 INDEX: {self.index_name}")
            logger.info(f"  🔧 EMBEDDING MODEL: text-embedding-3-small (1536 dimensions)")
            logger.info("=" * 50)
                
            return vector_store
            
        except Exception as e:
            logger.error(f"❌ Error during ingestion: {str(e)}")
            raise

def main():
    """Run the ingestion process."""
    print("🎯 Campaign Data Vector Ingestion")
    print("=" * 50)
    
    ingestion = CampaignVectorIngestion()
    vector_store = ingestion.ingest_all_data()
    
    print("\n🎉 Vector database ingestion completed successfully!")
    print("🔍 Your data is now ready for vector-based retrieval by agents!")

if __name__ == "__main__":
    main() 