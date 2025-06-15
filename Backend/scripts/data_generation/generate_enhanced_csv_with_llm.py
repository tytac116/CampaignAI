"""
Generate realistic enhanced campaign data with rich content, comments, and sentiment analysis.
Uses GPT-4o mini for realistic content generation and CSV output for Supabase import.
REQUIRES OpenAI API key - no fallback options.
"""

import csv
import json
import os
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
import shutil
from typing import List, Dict, Any
import re

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed - using system environment variables only")

# LangSmith tracing setup (optional)
HAS_LANGSMITH = False
try:
    from langsmith import traceable
    import langsmith
    
    # Initialize LangSmith if API key is available
    if os.getenv("LANGCHAIN_API_KEY"):
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "CampaignAI-Enhanced-DataGeneration"
        HAS_LANGSMITH = True
        print("✅ LangSmith tracing enabled")
    else:
        print("⚠️  LangSmith API key not found - tracing disabled")
        def traceable(name=None):
            def decorator(func):
                return func
            return decorator
        
except ImportError:
    print("⚠️  LangSmith not installed - tracing disabled")
    def traceable(name=None):
        def decorator(func):
            return func
        return decorator

# OpenAI setup - MANDATORY
try:
    from openai import OpenAI
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("❌ OPENAI_API_KEY environment variable is required! No fallback options available.")
    
    client = OpenAI(api_key=openai_api_key)
    print("✅ OpenAI API key found - LLM content generation enabled")
    
except ImportError:
    raise ImportError("❌ OpenAI package is required! Install with: pip install openai")

from faker import Faker
fake = Faker()

def clean_csv_directory():
    """Clean up existing CSV files."""
    csv_dir = Path("enhanced_csv_data")
    if csv_dir.exists():
        print("🧹 Cleaning up existing CSV files...")
        shutil.rmtree(csv_dir)
    
    csv_dir.mkdir(exist_ok=True)
    print("✅ Enhanced CSV directory ready")

def serialize_for_csv(obj):
    """Convert complex objects to JSON strings for CSV storage."""
    if isinstance(obj, (dict, list)):
        return json.dumps(obj, ensure_ascii=False)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, bool):
        return str(obj).lower()
    elif obj is None:
        return ""
    else:
        return str(obj)

@traceable(name="generate_rich_content_with_llm")
def generate_rich_content_with_llm(campaign_type: str, platform: str, campaign_name: str, batch_size: int = 5) -> List[Dict[str, Any]]:
    """Generate rich content using GPT-4o mini for multiple campaigns at once."""
    
    prompt = f"""Generate {batch_size} marketing campaigns for {platform}.

Campaign type: {campaign_type}
Base name: {campaign_name}

For each campaign, return:
- title: Campaign name variation
- description: 50-100 words about AI marketing for South African businesses
- hashtags: 3-4 relevant hashtags as array
- type_specific_content: empty object {{}}

IMPORTANT: Return ONLY valid JSON array. No markdown, no explanations.

[{{"title": "Campaign Name", "description": "Description here...", "hashtags": ["#AI", "#Marketing"], "type_specific_content": {{}}}}]

Generate {batch_size} campaigns total."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a creative marketing expert specializing in AI marketing campaigns for South African businesses. Generate realistic, engaging content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=1500
        )
        
        content_json = response.choices[0].message.content
        # Extract JSON from response (handle potential markdown formatting)
        if "```json" in content_json:
            content_json = content_json.split("```json")[1].split("```")[0]
        elif "```" in content_json:
            content_json = content_json.split("```")[1].split("```")[0]
        
        # Clean up the JSON string
        content_json = content_json.strip()
        
        # Try to parse JSON with better error handling
        try:
            return json.loads(content_json)
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parsing failed, attempting to fix: {e}")
            
            # Try to extract JSON array using regex
            json_match = re.search(r'\[.*?\]', content_json, re.DOTALL)
            if json_match:
                content_json = json_match.group(0)
                print(f"Extracted JSON array, trying again...")
                try:
                    return json.loads(content_json)
                except json.JSONDecodeError:
                    pass
            
            # Try to fix common JSON issues
            content_json = content_json.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            # Remove any trailing commas
            content_json = content_json.replace(',}', '}').replace(',]', ']')
            try:
                return json.loads(content_json)
            except json.JSONDecodeError:
                print(f"❌ Could not parse LLM response as JSON: {content_json[:200]}...")
                raise
        
    except Exception as e:
        raise RuntimeError(f"❌ LLM content generation failed and no fallback available: {e}")

@traceable(name="generate_comments_with_sentiment")
def generate_comments_with_sentiment(campaign_description: str, impressions: int, platform: str) -> List[Dict[str, Any]]:
    """Generate realistic comments with sentiment analysis using GPT-4o mini."""
    
    # Calculate number of comments based on engagement (0.5-2% of impressions)
    comment_count = max(1, int(impressions * random.uniform(0.005, 0.02)))
    comment_count = min(comment_count, 5)  # Cap at 5 comments for faster processing
    
    prompt = f"""Generate {comment_count} social media comments for: {campaign_description[:100]}

Mix: 65% positive, 25% neutral, 10% negative reactions.

Return ONLY this JSON format (no markdown, no extra text):
[{{"comment_text": "Great AI solution!", "sentiment_score": 0.8, "username": "user123"}}]

Each comment needs:
- comment_text: 10-30 words
- sentiment_score: number from -1.0 to 1.0  
- username: simple name like user123

Make {comment_count} comments total."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a social media expert who understands authentic user engagement patterns and South African online culture."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=800  # Reduced for speed
        )
        
        comments_json = response.choices[0].message.content
        # Extract JSON from response
        if "```json" in comments_json:
            comments_json = comments_json.split("```json")[1].split("```")[0]
        elif "```" in comments_json:
            comments_json = comments_json.split("```")[1].split("```")[0]
        
        # Clean up the JSON string
        comments_json = comments_json.strip()
        
        # Try to parse JSON with better error handling
        try:
            comments_data = json.loads(comments_json)
        except json.JSONDecodeError as e:
            print(f"❌ Comment JSON parsing failed: {e}")
            print(f"Raw response (first 500 chars): {comments_json[:500]}")
            raise RuntimeError(f"LLM returned invalid JSON for comments: {e}")
        
        # Add metadata to each comment
        for comment in comments_data:
            comment.update({
                'comment_id': f"comment_{random.randint(100000, 999999)}",
                'created_at': fake.date_time_between(start_date='-30d', end_date='now'),
                'likes': random.randint(0, max(1, int(impressions * 0.001))),
                'replies': random.randint(0, 3) if random.random() < 0.3 else 0
            })
        
        return comments_data
        
    except Exception as e:
        raise RuntimeError(f"❌ LLM comment generation failed and no fallback available: {e}")

def calculate_enhanced_metrics(impressions: int, clicks: int, spend: float, conversions: int, revenue: float, comments: List[Dict]) -> Dict[str, Any]:
    """Calculate enhanced metrics including sentiment analysis."""
    
    # Base engagement calculations
    likes = int(impressions * random.uniform(0.06, 0.12))
    shares = int(impressions * random.uniform(0.003, 0.008))
    saves = int(impressions * random.uniform(0.002, 0.006))
    
    # Sentiment analysis
    if comments:
        positive_comments = len([c for c in comments if c.get('sentiment_score', 0) > 0.2])
        neutral_comments = len([c for c in comments if -0.2 <= c.get('sentiment_score', 0) <= 0.2])
        negative_comments = len([c for c in comments if c.get('sentiment_score', 0) < -0.2])
        avg_sentiment = sum(c.get('sentiment_score', 0) for c in comments) / len(comments)
        
        # Sentiment affects engagement
        sentiment_multiplier = 1.0 + (avg_sentiment * 0.2)
        likes = int(likes * sentiment_multiplier)
        shares = int(shares * sentiment_multiplier)
    else:
        positive_comments = 0
        neutral_comments = 0
        negative_comments = 0
        avg_sentiment = 0.0
    
    total_engagement = likes + shares + saves + len(comments)
    engagement_rate = round(total_engagement / impressions * 100, 2) if impressions > 0 else 0
    
    overall_sentiment = 'positive' if avg_sentiment > 0.2 else 'negative' if avg_sentiment < -0.2 else 'neutral'
    
    return {
        'likes': likes,
        'shares': shares,
        'saves': saves,
        'comments_count': len(comments),
        'total_engagement': total_engagement,
        'engagement_rate': engagement_rate,
        'sentiment_score': round(avg_sentiment, 2),
        'overall_sentiment': overall_sentiment,
        'positive_comments': positive_comments,
        'neutral_comments': neutral_comments,
        'negative_comments': negative_comments,
        'video_views': int(impressions * 0.4) if random.choice([True, False]) else 0,
        'video_completion_rate': round(random.uniform(0.3, 0.8), 2) if random.choice([True, False]) else 0,
        'profile_visits': int(clicks * 0.3),
        'website_clicks': clicks
    }

@traceable(name="generate_enhanced_campaigns")
def generate_enhanced_campaigns(platform: str, count: int) -> tuple[List[Dict], List[Dict], List[Dict]]:
    """Generate enhanced campaigns with rich content and comments."""
    
    print(f"🎨 Generating {count} enhanced {platform} campaigns with LLM...")
    
    batch_start_time = time.time()
    campaigns = []
    all_content = []
    all_comments = []
    
    # Campaign types
    campaign_types = {
        "facebook": ["video_ad", "image_post", "carousel_post", "infographic_post", "live_stream", "testimonial_video", "demo_video"],
        "instagram": ["image_post", "story_ad", "reel_video", "carousel_post", "video_ad", "testimonial_video", "demo_video"]
    }
    
    # Campaign name templates
    name_templates = [
        "AI Revolution for SA Businesses",
        "Transform Your Marketing with AI",
        "CampaignAI Success Stories",
        "Free AI Marketing Audit",
        "Outsmart Competition with AI",
        "AI-Powered Customer Targeting",
        "Smart Marketing for SMEs",
        "Marketing Automation Made Simple",
        "AI-Driven Lead Generation",
        "Boost ROI with Intelligent Campaigns"
    ]
    
    # Generate in batches for LLM efficiency - balanced for speed and reliability
    batch_size = 5
    for batch_start in range(0, count, batch_size):
        batch_end = min(batch_start + batch_size, count)
        current_batch_size = batch_end - batch_start
        
        print(f"  🔄 Processing batch {batch_start//batch_size + 1}/{(count + batch_size - 1)//batch_size}")
        
        batch_time = time.time()
        
        # Select campaign type for this batch
        campaign_type = random.choice(campaign_types[platform])
        base_name = random.choice(name_templates)
        
        # Generate rich content with LLM
        rich_content_batch = generate_rich_content_with_llm(campaign_type, platform, base_name, current_batch_size)
        
        for i in range(current_batch_size):
            campaign_num = batch_start + i + 1
            if i >= len(rich_content_batch):
                raise RuntimeError(f"❌ LLM generated insufficient content: expected {current_batch_size}, got {len(rich_content_batch)}")
            content = rich_content_batch[i]
            
            # Generate basic campaign metrics
            impressions = random.randint(1000, 100000)
            clicks = int(impressions * random.uniform(0.01, 0.08))
            spend = round(random.uniform(100, 5000), 2)
            conversions = int(clicks * random.uniform(0.02, 0.15))
            revenue = round(conversions * random.uniform(50, 500), 2)
            
            # Generate comments with sentiment (reduced for speed)
            comments = generate_comments_with_sentiment(content['description'], impressions, platform)
            
            # Calculate enhanced metrics
            enhanced_metrics = calculate_enhanced_metrics(impressions, clicks, spend, conversions, revenue, comments)
            
            # Create campaign
            campaign = {
                'campaign_id': f"{platform[:2]}_camp_{campaign_num:04d}",
                'name': content['title'][:100],
                'platform': platform,
                'status': random.choices(['active', 'paused', 'completed'], weights=[70, 20, 10])[0],
                'objective': random.choice(['traffic', 'conversions', 'engagement', 'brand_awareness']),
                'campaign_type': campaign_type,
                'budget_type': 'daily',
                'budget_amount': round(spend * random.uniform(1.2, 3.0), 2),
                'spend_amount': spend,
                'remaining_budget': round(max(0, spend * random.uniform(0.1, 2.0)), 2),
                'impressions': impressions,
                'clicks': clicks,
                'conversions': conversions,
                'revenue': revenue,
                'ctr': round(clicks / impressions * 100, 2),
                'cpc': round(spend / clicks, 2) if clicks > 0 else 0,
                'cpm': round(spend / impressions * 1000, 2),
                'cpa': round(spend / conversions, 2) if conversions > 0 else 0,
                'roas': round(revenue / spend, 2) if spend > 0 else 0,
                'is_optimized': random.choice([True, False]),
                'optimization_score': round(random.uniform(0.3, 0.95), 2),
                'target_audience': json.dumps({
                    'age_range': {'min': random.randint(18, 35), 'max': random.randint(45, 65)},
                    'genders': random.choice(['all', 'male', 'female']),
                    'locations': random.sample(['Cape Town', 'Johannesburg', 'Durban', 'Pretoria'], random.randint(2, 4)),
                    'interests': random.sample(['business', 'marketing', 'technology', 'AI', 'automation'], random.randint(3, 5))
                }),
                'ad_creative': json.dumps({
                    'headline': content['title'],
                    'description': content['description'][:100] + '...' if len(content['description']) > 100 else content['description'],
                    'call_to_action': random.choice(['learn_more', 'sign_up', 'get_quote', 'contact_us'])
                }),
                'campaign_settings': json.dumps({
                    'placements': random.sample(['feed', 'stories', 'reels'], random.randint(1, 3)),
                    'schedule': {'start_time': '09:00', 'end_time': '20:00'},
                    'bid_strategy': random.choice(['lowest_cost', 'cost_cap', 'bid_cap'])
                }),
                'start_date': (datetime.now() - timedelta(days=random.randint(1, 90))).date().isoformat(),
                'end_date': (datetime.now() + timedelta(days=random.randint(1, 60))).date().isoformat() if random.choice([True, False]) else None,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                **enhanced_metrics  # Add all enhanced metrics to campaign
            }
            
            campaigns.append(campaign)
            
            # Store rich content
            content_record = {
                'campaign_id': campaign['campaign_id'],
                'campaign_type': campaign_type,
                'title': content['title'],
                'description': content['description'],
                'hashtags': content['hashtags'],
                **content['type_specific_content'],
                'created_at': datetime.now().isoformat()
            }
            all_content.append(content_record)
            
            # Store comments
            for comment in comments:
                comment['campaign_id'] = campaign['campaign_id']
                all_comments.append(comment)
        
        # Show batch timing
        batch_elapsed = time.time() - batch_time
        total_elapsed = time.time() - batch_start_time
        avg_time_per_batch = total_elapsed / ((batch_start//batch_size) + 1)
        remaining_batches = ((count + batch_size - 1)//batch_size) - ((batch_start//batch_size) + 1)
        eta_seconds = remaining_batches * avg_time_per_batch
        eta_minutes = eta_seconds / 60
        
        print(f"    ⏱️  Batch completed in {batch_elapsed:.1f}s | ETA: {eta_minutes:.1f} minutes")
    
    return campaigns, all_content, all_comments

def generate_daily_metrics(campaigns: List[Dict], days: int = 30) -> List[Dict]:
    """Generate daily metrics for campaigns."""
    
    print(f"📊 Generating {days} days of metrics for {len(campaigns)} campaigns...")
    
    all_metrics = []
    
    for campaign in campaigns:
        base_date = datetime.strptime(campaign['start_date'], '%Y-%m-%d')
        
        for day in range(days):
            metric_date = base_date + timedelta(days=day)
            
            # Distribute campaign totals across days with variation
            daily_impressions = int(campaign['impressions'] / days * random.uniform(0.5, 1.5))
            daily_clicks = int(campaign['clicks'] / days * random.uniform(0.5, 1.5))
            daily_spend = round(campaign['spend_amount'] / days * random.uniform(0.5, 1.5), 2)
            daily_conversions = int(campaign['conversions'] / days * random.uniform(0.3, 1.7))
            daily_revenue = round(campaign['revenue'] / days * random.uniform(0.3, 1.7), 2)
            
            metric = {
                'campaign_id': campaign['campaign_id'],
                'metric_date': metric_date.date().isoformat(),
                'impressions': daily_impressions,
                'clicks': daily_clicks,
                'spend': daily_spend,
                'conversions': daily_conversions,
                'revenue': daily_revenue,
                'likes': int(campaign['likes'] / days * random.uniform(0.5, 1.5)),
                'shares': int(campaign['shares'] / days * random.uniform(0.3, 1.7)),
                'saves': int(campaign['saves'] / days * random.uniform(0.3, 1.7)),
                'comments_count': int(campaign['comments_count'] / days * random.uniform(0.3, 1.7)),
                'video_views': int(campaign['video_views'] / days * random.uniform(0.5, 1.5)) if campaign['video_views'] > 0 else 0,
                'profile_visits': int(campaign['profile_visits'] / days * random.uniform(0.5, 1.5)),
                'created_at': datetime.now().isoformat()
            }
            
            all_metrics.append(metric)
    
    return all_metrics

@traceable(name="generate_enhanced_dataset")
def main():
    """Generate enhanced dataset with rich content, comments, and sentiment analysis."""
    
    print("🚀 Enhanced Campaign Data Generator with GPT-4o Mini")
    print("=" * 70)
    print("🤖 Using AI for realistic content, comments, and sentiment analysis")
    print("📊 Generating rich data for vector DB ingestion")
    if HAS_LANGSMITH:
        print("📈 LangSmith tracing enabled for token monitoring")
    print("=" * 70)
    
    start_time = time.time()
    
    # Clean up existing files
    clean_csv_directory()
    
    try:
        # Generate Facebook campaigns
        facebook_count = 250
        fb_campaigns, fb_content, fb_comments = generate_enhanced_campaigns("facebook", facebook_count)
        
        # Generate Instagram campaigns
        instagram_count = 250
        ig_campaigns, ig_content, ig_comments = generate_enhanced_campaigns("instagram", instagram_count)
        
        # Combine all data
        all_campaigns = fb_campaigns + ig_campaigns
        all_content = fb_content + ig_content
        all_comments = fb_comments + ig_comments
        
        print(f"\n💾 Saving enhanced data to CSV files...")
        
        # Save campaigns
        campaign_fieldnames = [
            "id", "campaign_id", "name", "platform", "status", "objective", "campaign_type",
            "budget_type", "budget_amount", "spend_amount", "remaining_budget",
            "impressions", "clicks", "conversions", "revenue", 
            "ctr", "cpc", "cpm", "cpa", "roas",
            "likes", "shares", "saves", "comments_count", "total_engagement", "engagement_rate",
            "sentiment_score", "overall_sentiment", "positive_comments", "neutral_comments", "negative_comments",
            "video_views", "video_completion_rate", "profile_visits", "website_clicks",
            "is_optimized", "optimization_score",
            "target_audience", "ad_creative", "campaign_settings",
            "start_date", "end_date", "created_at", "updated_at"
        ]
        
        with open("enhanced_csv_data/campaigns.csv", 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=campaign_fieldnames)
            writer.writeheader()
            
            for idx, campaign in enumerate(all_campaigns, 1):
                row = {"id": idx}
                for field in campaign_fieldnames[1:]:
                    value = campaign.get(field)
                    row[field] = serialize_for_csv(value)
                writer.writerow(row)
        
        # Save rich content
        content_fieldnames = [
            "id", "campaign_id", "campaign_type", "title", "description", "hashtags",
            "video_transcript", "video_duration", "image_description", "image_dimensions",
            "carousel_slides", "story_elements", "reel_script", "music_track",
            "episode_topic", "guest_name", "episode_duration", "infographic_data",
            "live_topic", "expected_viewers", "testimonial_quote", "customer_name",
            "business_type", "demo_features", "demo_duration", "created_at"
        ]
        
        with open("enhanced_csv_data/campaign_content.csv", 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=content_fieldnames)
            writer.writeheader()
            
            for idx, content in enumerate(all_content, 1):
                row = {"id": idx}
                for field in content_fieldnames[1:]:
                    value = content.get(field)
                    row[field] = serialize_for_csv(value)
                writer.writerow(row)
        
        # Save comments
        comment_fieldnames = [
            "id", "campaign_id", "comment_id", "comment_text", "sentiment_score",
            "username", "likes", "replies", "created_at"
        ]
        
        with open("enhanced_csv_data/campaign_comments.csv", 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=comment_fieldnames)
            writer.writeheader()
            
            for idx, comment in enumerate(all_comments, 1):
                row = {"id": idx}
                for field in comment_fieldnames[1:]:
                    value = comment.get(field)
                    row[field] = serialize_for_csv(value)
                writer.writerow(row)
        
        # Generate and save metrics (reduced days for speed)
        all_metrics = generate_daily_metrics(all_campaigns, 14)
        
        metric_fieldnames = [
            "id", "campaign_id", "metric_date", "impressions", "clicks", "spend",
            "conversions", "revenue", "likes", "shares", "saves", "comments_count",
            "video_views", "profile_visits", "created_at"
        ]
        
        with open("enhanced_csv_data/campaign_metrics.csv", 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=metric_fieldnames)
            writer.writeheader()
            
            for idx, metric in enumerate(all_metrics, 1):
                row = {"id": idx}
                for field in metric_fieldnames[1:]:
                    value = metric.get(field)
                    row[field] = serialize_for_csv(value)
                writer.writerow(row)
        
        total_time = time.time() - start_time
        
        print("\n" + "=" * 70)
        print("🎉 Enhanced CSV data generation completed!")
        print(f"⚡ Total time: {total_time:.1f} seconds")
        print(f"🤖 Generated with GPT-4o Mini for realistic content")
        if HAS_LANGSMITH:
            print("📊 Check LangSmith dashboard for token usage")
        
        print(f"\n📊 Dataset Summary:")
        print(f"   📋 Campaigns: {len(all_campaigns)} (with rich metadata)")
        print(f"   📝 Content records: {len(all_content)} (LLM-generated)")
        print(f"   💬 Comments: {len(all_comments)} (with sentiment analysis)")
        print(f"   📈 Metrics: {len(all_metrics)} (14 days per campaign)")
        
        print(f"\n📁 Generated files in enhanced_csv_data/:")
        csv_dir = Path("enhanced_csv_data")
        total_size = 0
        for csv_file in csv_dir.glob("*.csv"):
            size = csv_file.stat().st_size
            total_size += size
            print(f"   📄 {csv_file.name}: {size/1024:.1f} KB")
        
        print(f"\n💾 Total size: {total_size/1024:.1f} KB")
        print("✨ Ready for Supabase import!")
        print("\n🔄 Next steps:")
        print("   1. Review the generated CSV files")
        print("   2. Import to Supabase using the dashboard or CLI")
        print("   3. Test API simulators with rich data")
        print("   4. Prepare for vector DB ingestion")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation interrupted by user!")
        total_time = time.time() - start_time
        print(f"⏱️  Ran for {total_time:.1f} seconds")
        print("📁 Check enhanced_csv_data/ directory for partial data")
        
    except Exception as e:
        print(f"\n\n❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main() 