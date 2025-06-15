"""
AI-powered data generator using OpenAI to create realistic campaign data for CampaignAI.
"""

import os
import random
import json
from datetime import datetime, timedelta, date
from typing import List, Dict, Any
from faker import Faker
import sys

# LangSmith tracing setup (optional)
HAS_LANGSMITH = False
try:
    from langsmith import traceable
    from langsmith.wrappers import wrap_openai
    import langsmith
    
    # Initialize LangSmith if API key is available
    if os.getenv("LANGCHAIN_API_KEY"):
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "CampaignAI-DataGeneration"
        HAS_LANGSMITH = True
        print("✅ LangSmith tracing enabled")
    else:
        print("⚠️  LangSmith API key not found - tracing disabled")
        # Create dummy decorator if LangSmith not available
        def traceable(name=None):
            def decorator(func):
                return func
            return decorator
        
except ImportError:
    print("⚠️  LangSmith not installed - tracing disabled")
    # Create dummy decorator if LangSmith not available
    def traceable(name=None):
        def decorator(func):
            return func
        return decorator

# Add the app directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, os.path.join(app_dir, 'app'))

from core.config import settings

fake = Faker('en_US')  # Use US locale (closest to South African English)
Faker.seed(42)  # For reproducible data

# OpenAI setup with LangSmith tracing
HAS_OPENAI = False
openai = None

try:
    import openai as openai_module
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and len(api_key) > 10:
        # Wrap OpenAI client with LangSmith tracing if available
        openai_module.api_key = api_key
        if HAS_LANGSMITH:
            openai = wrap_openai(openai_module)
            print(f"✅ OpenAI initialized with LangSmith tracing - API key length: {len(api_key)}")
        else:
            openai = openai_module
            print(f"✅ OpenAI initialized - API key length: {len(api_key)}")
        HAS_OPENAI = True
    else:
        print("⚠️  OpenAI API key not found or invalid")
        
except ImportError:
    print("⚠️  OpenAI package not installed")

def clean_json_response(response_text: str) -> str:
    """Clean AI response by removing markdown code blocks and extra whitespace."""
    # Remove markdown code blocks
    response_text = response_text.strip()
    
    # Remove ```json and ``` markers
    if response_text.startswith('```json'):
        response_text = response_text[7:]  # Remove ```json
    elif response_text.startswith('```'):
        response_text = response_text[3:]   # Remove ```
    
    if response_text.endswith('```'):
        response_text = response_text[:-3]  # Remove trailing ```
    
    return response_text.strip()

@traceable(name="generate_campaigns")
def get_ai_generated_campaigns(platform: str, count: int) -> List[Dict[str, Any]]:
    """Generate realistic campaigns using AI - optimized for speed."""
    
    # Generate larger batches to reduce API calls
    actual_count = min(count, 25)  # Increased from 10 to 25
    
    prompt = f"""
You are generating realistic social media campaign data for CampaignAI, an AI-based marketing services company in South Africa.

Company Context:
- Name: CampaignAI
- Industry: AI Marketing & Automation Services
- Location: South Africa (focus on local market but also broader African market)
- Services: AI campaign optimization, automated social media, predictive analytics, AI chatbots, ML targeting

Generate {actual_count} realistic {platform.title()} campaigns that CampaignAI would run to:
1. Promote their AI services
2. Generate leads from potential clients
3. Build brand awareness in South Africa
4. Showcase AI expertise and case studies
5. Attract businesses looking to automate their marketing

For each campaign, provide:
- name: Creative, professional campaign name (max 60 chars)
- objective: One of [conversions, traffic, brand_awareness, reach, engagement, lead_generation, video_views]
- description: Brief description of what the campaign promotes (max 150 chars)
- target_business: Type of business we're targeting (e.g., "e-commerce stores", "local restaurants")
- campaign_type: Type of content - one of [video_ad, image_post, carousel_post, story_ad, reel_video, podcast_episode, webinar_promo, case_study_post, testimonial_video, demo_video, infographic_post, live_stream]

Return as JSON array with exactly {actual_count} campaigns. Make them diverse and realistic for a growing AI company.
"""
    
    if HAS_OPENAI:
        try:
            print(f"🤖 Generating {actual_count} {platform} campaigns with AI...")
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a marketing expert helping create realistic campaign data. Always return valid JSON array only, no additional text or markdown formatting."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,  # Increased for larger batches
                temperature=0.8
            )
            
            response_text = response.choices[0].message.content.strip()
            print(f"✅ AI response received: {len(response_text)} characters")
            
            # Clean the response text
            clean_response = clean_json_response(response_text)
            
            # Try to parse JSON response
            ai_campaigns = json.loads(clean_response)
            
            # If we got fewer campaigns than requested, duplicate with variations
            while len(ai_campaigns) < count:
                base_campaigns = ai_campaigns.copy()
                for base_campaign in base_campaigns:
                    if len(ai_campaigns) >= count:
                        break
                    # Create variation
                    variation = base_campaign.copy()
                    variation["name"] = f"{base_campaign['name']} - Enhanced"
                    ai_campaigns.append(variation)
            
            return ai_campaigns[:count]  # Return exactly the requested count
            
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parsing failed: {e}")
            print(f"Raw response: {response_text[:200]}...")
            return get_fallback_campaigns(platform, count)
        except Exception as e:
            print(f"⚠️  AI generation failed: {e}")
            return get_fallback_campaigns(platform, count)
    
    # Fallback campaign generation
    return get_fallback_campaigns(platform, count)

def get_fallback_campaigns(platform: str, count: int) -> List[Dict[str, Any]]:
    """Fallback campaign generation if AI fails."""
    
    # Campaign types based on platform
    campaign_types = {
        "facebook": ["video_ad", "image_post", "carousel_post", "webinar_promo", "case_study_post", "testimonial_video", "demo_video", "infographic_post", "live_stream"],
        "instagram": ["image_post", "story_ad", "reel_video", "carousel_post", "video_ad", "infographic_post", "testimonial_video", "demo_video"]
    }
    
    campaign_templates = [
        {
            "name": "AI Revolution for SA Businesses",
            "objective": "brand_awareness",
            "description": "Introducing AI-powered marketing automation to South African businesses",
            "target_business": "traditional businesses"
        },
        {
            "name": "Free AI Marketing Audit",
            "objective": "lead_generation", 
            "description": "Get a free AI-powered analysis of your current marketing performance",
            "target_business": "small businesses"
        },
        {
            "name": "CampaignAI Success Stories",
            "objective": "engagement",
            "description": "Real results from businesses using our AI marketing platform",
            "target_business": "potential clients"
        },
        {
            "name": "Transform Your Marketing with AI",
            "objective": "conversions",
            "description": "Boost your marketing ROI with intelligent automation and optimization",
            "target_business": "marketing managers"
        },
        {
            "name": "AI-Powered Customer Targeting",
            "objective": "traffic",
            "description": "Discover how AI can identify your perfect customers automatically",
            "target_business": "e-commerce stores"
        },
        {
            "name": "CampaignAI Demo Week",
            "objective": "lead_generation",
            "description": "Book a free demo and see how AI can transform your campaigns",
            "target_business": "digital agencies"
        },
        {
            "name": "Outsmart Competition with AI",
            "objective": "brand_awareness",
            "description": "Join leading SA businesses using AI to gain competitive advantage",
            "target_business": "business owners"
        },
        {
            "name": "AI Chatbots for Better Customer Service",
            "objective": "conversions",
            "description": "Automate customer support while increasing satisfaction and sales",
            "target_business": "service businesses"
        },
        {
            "name": "Predictive Analytics for Growth",
            "objective": "traffic",
            "description": "Use AI to predict customer behavior and optimize campaigns",
            "target_business": "retail businesses"
        },
        {
            "name": "SA SME AI Marketing Solutions",
            "objective": "lead_generation",
            "description": "Affordable AI marketing tools designed for South African SMEs",
            "target_business": "small businesses"
        }
    ]
    
    fallback_campaigns = []
    for i in range(count):
        template = campaign_templates[i % len(campaign_templates)]
        campaign = template.copy()
        campaign["name"] = f"{template['name']} - {platform.title()} #{i+1}"
        campaign["campaign_type"] = random.choice(campaign_types[platform])
        fallback_campaigns.append(campaign)
        
    return fallback_campaigns

# Add back the original AI function (needed for cache)
@traceable(name="generate_audience_creative")
def get_ai_generated_audience_and_creative(campaign_name: str, target_business: str, platform: str) -> Dict[str, Any]:
    """Generate realistic target audience and ad creative using AI."""
    
    prompt = f"""
For CampaignAI's campaign "{campaign_name}" targeting {target_business} on {platform}, generate:

1. Target Audience:
- age_range: {{min: number, max: number}} (realistic for {target_business})
- genders: "male", "female", or "all"
- locations: Array of South African cities/regions
- interests: Array of 4-6 relevant interests
- behaviors: Array of 3-5 behavioral targeting options

2. Ad Creative:
- headline: Compelling headline (max 40 chars)
- description: Ad description (max 125 chars)
- call_to_action: One of [learn_more, shop_now, sign_up, download, contact_us, book_travel, apply_now, get_quote, subscribe]

Return as JSON with "target_audience" and "ad_creative" objects.
"""
    
    if HAS_OPENAI:
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a digital marketing expert. Return valid JSON only, no additional text or markdown formatting."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content.strip()
            clean_response = clean_json_response(response_text)
            return json.loads(clean_response)
            
        except json.JSONDecodeError as e:
            print(f"⚠️  AI creative JSON parsing failed: {e}")
        except Exception as e:
            print(f"⚠️  AI creative generation failed: {e}")
    
    # Fallback to smart fallback
    return generate_smart_fallback_audience_creative(target_business, platform)

# Cache for audience/creative data to reduce API calls
_audience_creative_cache = {}

def get_optimized_audience_and_creative(campaign_name: str, target_business: str, platform: str) -> Dict[str, Any]:
    """Get audience and creative data with caching for speed optimization."""
    
    # Create a cache key based on target business and platform
    cache_key = f"{target_business}_{platform}"
    
    # Check cache first
    if cache_key in _audience_creative_cache:
        cached_data = _audience_creative_cache[cache_key].copy()
        
        # Vary the headline slightly for uniqueness
        variations = [
            "Transform Your Business with AI",
            "Boost Performance with Smart AI",
            "AI-Powered Growth Solutions",
            "Automate & Optimize with AI",
            "Smart Marketing, Better Results"
        ]
        
        cached_data["ad_creative"]["headline"] = random.choice(variations)
        return cached_data
    
    # Generate new data if not in cache (only for first few calls)
    if len(_audience_creative_cache) < 5:  # Limit AI calls
        ai_data = get_ai_generated_audience_and_creative(campaign_name, target_business, platform)
        _audience_creative_cache[cache_key] = ai_data.copy()
        return ai_data
    
    # Use intelligent fallback for the rest
    return generate_smart_fallback_audience_creative(target_business, platform)

def generate_smart_fallback_audience_creative(target_business: str, platform: str) -> Dict[str, Any]:
    """Generate intelligent fallback audience and creative data."""
    
    # Smart targeting based on business type
    business_targeting = {
        "small businesses": {
            "age_range": {"min": 25, "max": 55},
            "interests": ["small business", "entrepreneurship", "business growth", "marketing", "automation", "productivity"],
            "behaviors": ["small business owners", "decision makers", "technology adopters"]
        },
        "e-commerce stores": {
            "age_range": {"min": 22, "max": 45},
            "interests": ["e-commerce", "online retail", "digital marketing", "conversion optimization", "customer acquisition"],
            "behaviors": ["online business owners", "e-commerce managers", "digital marketers"]
        },
        "marketing agencies": {
            "age_range": {"min": 25, "max": 50},
            "interests": ["digital marketing", "marketing automation", "client management", "campaign optimization", "analytics"],
            "behaviors": ["marketing professionals", "agency owners", "digital specialists"]
        },
        "traditional businesses": {
            "age_range": {"min": 30, "max": 60},
            "interests": ["business modernization", "digital transformation", "competitive advantage", "efficiency"],
            "behaviors": ["business owners", "executives", "decision makers"]
        }
    }
    
    # Get targeting data or use default
    targeting = business_targeting.get(target_business, business_targeting["small businesses"])
    
    # Platform-specific call-to-actions
    platform_ctas = {
        "facebook": ["learn_more", "contact_us", "get_quote", "book_now"],
        "instagram": ["learn_more", "sign_up", "get_quote", "contact_us"]
    }
    
    headlines = [
        "Transform Your Marketing with AI",
        "Boost ROI with Smart Automation",
        "AI-Powered Growth Solutions",
        "Automate. Optimize. Grow.",
        "Smart Marketing Made Simple",
        "AI That Drives Real Results",
        "Future-Proof Your Marketing",
        "Intelligent Campaign Optimization"
    ]
    
    descriptions = [
        "Join leading SA businesses using AI to boost campaign performance and reduce costs. Get started today!",
        "Discover how AI can transform your marketing ROI and streamline your campaigns automatically.",
        "Advanced AI technology that learns and optimizes your campaigns for maximum performance.",
        "Stop guessing. Start growing. Let AI optimize your marketing campaigns for better results.",
        "Professional AI marketing solutions designed specifically for South African businesses."
    ]
    
    return {
        "target_audience": {
            "age_range": targeting["age_range"],
            "genders": "all",
            "locations": random.sample(["Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth", "Bloemfontein"], k=random.randint(3, 5)),
            "interests": targeting["interests"],
            "behaviors": targeting["behaviors"]
        },
        "ad_creative": {
            "headline": random.choice(headlines),
            "description": random.choice(descriptions),
            "call_to_action": random.choice(platform_ctas[platform])
        }
    }

def generate_realistic_kpis(spend: float, platform: str, objective: str) -> Dict[str, float]:
    """Generate realistic KPIs based on spend, platform, and objective."""
    
    # Platform and objective-specific base rates for CampaignAI (B2B service company)
    base_rates = {
        "facebook": {
            "brand_awareness": {"cpm": (12, 18), "ctr": (1.2, 2.8), "engagement_rate": (2.0, 4.5)},
            "lead_generation": {"cpm": (15, 25), "ctr": (2.5, 4.5), "conversion_rate": (8, 15)},
            "conversions": {"cpm": (18, 28), "ctr": (2.0, 3.8), "conversion_rate": (5, 12)},
            "traffic": {"cpm": (10, 16), "ctr": (1.8, 3.2), "conversion_rate": (3, 8)},
            "engagement": {"cpm": (8, 14), "ctr": (2.5, 5.0), "engagement_rate": (4.0, 8.0)},
            "reach": {"cpm": (8, 12), "ctr": (1.0, 2.0), "engagement_rate": (1.5, 3.0)},
            "video_views": {"cpm": (6, 12), "ctr": (3.0, 6.0), "engagement_rate": (3.0, 7.0)}
        },
        "instagram": {
            "brand_awareness": {"cpm": (14, 22), "ctr": (1.0, 2.5), "engagement_rate": (3.0, 6.0)},
            "lead_generation": {"cpm": (18, 30), "ctr": (2.0, 4.0), "conversion_rate": (6, 12)},
            "conversions": {"cpm": (20, 32), "ctr": (1.8, 3.5), "conversion_rate": (4, 10)},
            "traffic": {"cpm": (12, 20), "ctr": (1.5, 3.0), "conversion_rate": (2, 6)},
            "engagement": {"cpm": (10, 18), "ctr": (3.0, 6.0), "engagement_rate": (5.0, 10.0)},
            "reach": {"cpm": (10, 16), "ctr": (1.2, 2.8), "engagement_rate": (2.5, 5.0)},
            "video_views": {"cpm": (8, 15), "ctr": (4.0, 8.0), "engagement_rate": (4.0, 9.0)}
        }
    }
    
    rates = base_rates.get(platform, base_rates["facebook"]).get(objective, base_rates["facebook"]["conversions"])
    
    # Generate correlated metrics
    cpm = random.uniform(*rates["cpm"])
    impressions = int(spend / cpm * 1000)
    
    ctr = random.uniform(*rates["ctr"]) / 100
    clicks = int(impressions * ctr)
    cpc = spend / clicks if clicks > 0 else 0
    
    # For service business, conversions are typically consultation bookings, demo requests, etc.
    if "conversion_rate" in rates:
        conversion_rate = random.uniform(*rates["conversion_rate"]) / 100
        conversions = int(clicks * conversion_rate)
    else:
        conversions = int(clicks * random.uniform(0.02, 0.08))  # 2-8% default
    
    # Revenue modeling for CampaignAI (service business)
    # Each conversion could be worth R2,000 - R50,000 (consultation to full service contract)
    if conversions > 0:
        avg_contract_value = random.uniform(2000, 50000)  # ZAR
        revenue = conversions * avg_contract_value
        roas = revenue / spend if spend > 0 else 0
    else:
        revenue = 0
        roas = 0
    
    return {
        "impressions": impressions,
        "clicks": clicks,
        "conversions": conversions,
        "cpm": round(cpm, 2),
        "cpc": round(cpc, 2),
        "ctr": round(ctr * 100, 2),
        "revenue": round(revenue, 2),
        "roas": round(roas, 2)
    }

def generate_campaign_settings(platform: str, objective: str) -> Dict[str, Any]:
    """Generate realistic campaign settings."""
    platform_placements = {
        "facebook": ["news_feed", "right_column", "marketplace", "stories", "reels"],
        "instagram": ["feed", "stories", "reels", "explore"]
    }
    
    # Business hours for South African market
    business_schedule = {
        "start_time": "08:00",
        "end_time": "18:00", 
        "days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday"]
    }
    
    # Add weekend for awareness campaigns
    if objective in ["brand_awareness", "engagement", "reach"]:
        business_schedule["days_of_week"].extend(["saturday", "sunday"])
        business_schedule["start_time"] = "09:00"
        business_schedule["end_time"] = "20:00"
    
    return {
        "placements": random.sample(platform_placements[platform], k=random.randint(2, len(platform_placements[platform]))),
        "schedule": business_schedule,
        "bid_strategy": "lowest_cost" if objective in ["brand_awareness", "reach"] else "cost_cap",
        "optimization_goal": objective,
        "delivery_type": "standard"
    }

def generate_agent_executions(count: int = 50) -> List[Dict[str, Any]]:
    """Generate realistic agent execution data."""
    
    workflows = [
        "campaign_optimization",
        "audience_analysis", 
        "budget_reallocation",
        "performance_analysis",
        "competitor_analysis",
        "creative_testing",
        "bid_optimization",
        "keyword_analysis"
    ]
    
    statuses = ["completed", "running", "failed", "pending"]
    
    executions = []
    for i in range(count):
        workflow = random.choice(workflows)
        status = random.choices(statuses, weights=[70, 15, 10, 5])[0]
        
        # Generate realistic execution time based on workflow complexity
        if workflow in ["competitor_analysis", "audience_analysis"]:
            execution_time = random.uniform(45, 180)  # 45s to 3min
        elif workflow in ["performance_analysis", "campaign_optimization"]:
            execution_time = random.uniform(20, 90)   # 20s to 1.5min
        else:
            execution_time = random.uniform(10, 60)   # 10s to 1min
        
        execution = {
            "execution_id": f"exec_{i+1:04d}",
            "workflow_type": workflow,
            "status": status,
            "execution_time_seconds": round(execution_time, 2) if status == "completed" else None,
            "input_data": {
                "campaign_ids": [f"fb_camp_{random.randint(1, 250):04d}", f"ig_camp_{random.randint(1, 250):04d}"],
                "parameters": {
                    "optimization_goal": random.choice(["roas", "cpa", "ctr", "conversions"]),
                    "budget_limit": random.uniform(1000, 20000),
                    "time_range": random.choice(["7d", "14d", "30d"])
                }
            },
            "output_data": {
                "recommendations": [
                    "Increase budget for high-performing ad sets",
                    "Pause underperforming campaigns",
                    "Test new creative variations",
                    "Adjust targeting parameters"
                ][:random.randint(1, 4)],
                "metrics_improved": {
                    "roas_improvement": round(random.uniform(5, 25), 2),
                    "cpa_reduction": round(random.uniform(10, 40), 2),
                    "ctr_improvement": round(random.uniform(3, 15), 2)
                } if status == "completed" else None
            },
            "error_details": random.choice([
                "Network timeout during API call",
                "Insufficient data for analysis",
                "Rate limit exceeded",
                "Invalid campaign configuration"
            ]) if status == "failed" else None,
            "created_at": fake.date_time_between(start_date="-30d", end_date="now"),
            "completed_at": fake.date_time_between(start_date="-29d", end_date="now") if status == "completed" else None
        }
        executions.append(execution)
    
    return executions

def generate_campaign_metrics(campaign: Dict[str, Any], days: int = 30) -> List[Dict[str, Any]]:
    """Generate daily metrics for a campaign."""
    metrics = []
    
    # Calculate daily baseline from campaign totals
    total_impressions = campaign["impressions"]
    total_clicks = campaign["clicks"]
    total_spend = campaign["spend_amount"]
    
    daily_impressions = total_impressions / days
    daily_clicks = total_clicks / days
    daily_spend = total_spend / days
    
    start_date = campaign["start_date"]
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date).date()
    
    for day in range(days):
        metric_date = start_date + timedelta(days=day)
        
        # Add some realistic daily variation (±30%)
        day_impressions = int(daily_impressions * random.uniform(0.7, 1.3))
        day_clicks = int(daily_clicks * random.uniform(0.7, 1.3))
        day_spend = daily_spend * random.uniform(0.7, 1.3)
        
        # Generate engagement metrics for Instagram/visual campaigns
        if campaign["platform"] == "instagram":
            likes = int(day_impressions * random.uniform(0.01, 0.03))  # 1-3% engagement
            shares = int(likes * random.uniform(0.1, 0.3))
            comments = int(likes * random.uniform(0.05, 0.15))
            saves = int(likes * random.uniform(0.02, 0.08))
            video_views = int(day_impressions * random.uniform(0.15, 0.35)) if "video" in campaign.get("objective", "") else 0
        else:
            likes = int(day_impressions * random.uniform(0.005, 0.015))  # Lower engagement on Facebook
            shares = int(likes * random.uniform(0.05, 0.2))
            comments = int(likes * random.uniform(0.03, 0.12))
            saves = int(likes * random.uniform(0.01, 0.05))
            video_views = int(day_impressions * random.uniform(0.1, 0.25)) if "video" in campaign.get("objective", "") else 0
        
        conversions = int(day_clicks * random.uniform(0.02, 0.12))  # 2-12% conversion rate
        revenue = conversions * random.uniform(2000, 15000) if conversions > 0 else 0  # CampaignAI service value
        
        metric = {
            "campaign_id": campaign["campaign_id"],
            "metric_date": metric_date,
            "hour_of_day": None,  # Daily aggregation
            "impressions": day_impressions,
            "clicks": day_clicks,
            "conversions": conversions,
            "spend": round(day_spend, 2),
            "revenue": round(revenue, 2),
            "likes": likes,
            "shares": shares,
            "comments": comments,
            "saves": saves,
            "video_views": video_views,
            "demographics": {
                "age_groups": {"25-34": 35, "35-44": 30, "45-54": 20, "55+": 15},
                "genders": {"male": 45, "female": 55},
                "locations": {"gauteng": 40, "western_cape": 25, "kwazulu_natal": 20, "other": 15}
            },
            "geo_data": {
                "countries": {"south_africa": 85, "botswana": 8, "namibia": 4, "other": 3}
            },
            "device_data": {
                "mobile": 75, "desktop": 20, "tablet": 5
            },
            "relevance_score": random.uniform(7.5, 9.5),
            "quality_score": random.uniform(6.8, 9.2),
            "engagement_rate": round((likes + shares + comments) / day_impressions * 100, 2) if day_impressions > 0 else 0,
            "performance_index": random.uniform(65, 95),
            "efficiency_index": random.uniform(70, 88),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        metrics.append(metric)
    
    return metrics

def generate_realistic_ai_data(facebook_count: int = 250, instagram_count: int = 250) -> Dict[str, List]:
    """Generate comprehensive realistic campaign data using AI."""
    
    print("🤖 Using AI to generate realistic CampaignAI campaign data...")
    print(f"📊 Target: {facebook_count} Facebook + {instagram_count} Instagram campaigns")
    
    all_campaigns = []
    all_metrics = []
    
    # Generate Facebook campaigns with progress tracking
    print(f"\n📘 Generating {facebook_count} Facebook campaigns with AI...")
    print("=" * 50)
    
    # Process Facebook campaigns in batches of 10
    batch_size = 10
    facebook_batches = (facebook_count + batch_size - 1) // batch_size  # Ceiling division
    
    for batch_num in range(facebook_batches):
        start_idx = batch_num * batch_size
        end_idx = min((batch_num + 1) * batch_size, facebook_count)
        current_batch_size = end_idx - start_idx
        
        print(f"🔄 Facebook Batch {batch_num + 1}/{facebook_batches} (campaigns {start_idx + 1}-{end_idx})...")
        
        fb_ai_campaigns = get_ai_generated_campaigns("facebook", current_batch_size)
        
        for i, ai_campaign in enumerate(fb_ai_campaigns):
            campaign_idx = start_idx + i
            
            # Show progress every 25 campaigns
            if (campaign_idx + 1) % 25 == 0:
                print(f"  ✓ Processed {campaign_idx + 1}/{facebook_count} Facebook campaigns")
            
            # Get AI-generated audience and creative
            audience_creative = get_optimized_audience_and_creative(
                ai_campaign["name"], 
                ai_campaign["target_business"], 
                "facebook"
            )
            
            # Generate financial data
            budget_amount = random.uniform(500, 15000)  # R500 - R15,000 per campaign
            spend_amount = budget_amount * random.uniform(0.3, 0.95)  # 30-95% of budget spent
            
            # Generate KPIs
            kpis = generate_realistic_kpis(spend_amount, "facebook", ai_campaign["objective"])
            
            campaign = {
                "campaign_id": f"fb_camp_{campaign_idx+1:04d}",
                "name": ai_campaign["name"],
                "platform": "facebook",
                "status": random.choices(["active", "paused", "completed"], weights=[70, 20, 10])[0],
                "objective": ai_campaign["objective"],
                "budget_type": "daily",
                "budget_amount": round(budget_amount, 2),
                "spend_amount": round(spend_amount, 2),
                "remaining_budget": round(budget_amount - spend_amount, 2),
                "impressions": kpis["impressions"],
                "clicks": kpis["clicks"],
                "conversions": kpis["conversions"],
                "revenue": kpis["revenue"],
                "ctr": kpis["ctr"],
                "cpc": kpis["cpc"],
                "cpm": kpis["cpm"],
                "cpa": round(spend_amount / kpis["conversions"], 2) if kpis["conversions"] > 0 else 0,
                "roas": kpis["roas"],
                "is_optimized": random.choice([True, False]),
                "optimization_score": random.uniform(0.6, 0.95),
                "target_audience": audience_creative["target_audience"],
                "ad_creative": audience_creative["ad_creative"],
                "campaign_settings": generate_campaign_settings("facebook", ai_campaign["objective"]),
                "start_date": fake.date_between(start_date="-90d", end_date="-7d"),
                "end_date": fake.date_between(start_date="+7d", end_date="+60d") if random.choice([True, False]) else None,
                "created_at": fake.date_time_between(start_date="-100d", end_date="-90d"),
                "updated_at": fake.date_time_between(start_date="-7d", end_date="now")
            }
            all_campaigns.append(campaign)
    
    print(f"✅ Generated {len([c for c in all_campaigns if c['platform'] == 'facebook'])} Facebook campaigns")
    
    # Generate Instagram campaigns with progress tracking
    print(f"\n📷 Generating {instagram_count} Instagram campaigns with AI...")
    print("=" * 50)
    
    # Process Instagram campaigns in batches of 10
    instagram_batches = (instagram_count + batch_size - 1) // batch_size  # Ceiling division
    
    for batch_num in range(instagram_batches):
        start_idx = batch_num * batch_size
        end_idx = min((batch_num + 1) * batch_size, instagram_count)
        current_batch_size = end_idx - start_idx
        
        print(f"🔄 Instagram Batch {batch_num + 1}/{instagram_batches} (campaigns {start_idx + 1}-{end_idx})...")
        
        ig_ai_campaigns = get_ai_generated_campaigns("instagram", current_batch_size)
        
        for i, ai_campaign in enumerate(ig_ai_campaigns):
            campaign_idx = start_idx + i
            
            # Show progress every 25 campaigns
            if (campaign_idx + 1) % 25 == 0:
                print(f"  ✓ Processed {campaign_idx + 1}/{instagram_count} Instagram campaigns")
            
            # Get AI-generated audience and creative  
            audience_creative = get_optimized_audience_and_creative(
                ai_campaign["name"],
                ai_campaign["target_business"],
                "instagram"
            )
            
            # Generate financial data
            budget_amount = random.uniform(300, 12000)  # R300 - R12,000 per campaign
            spend_amount = budget_amount * random.uniform(0.25, 0.90)
            
            # Generate KPIs
            kpis = generate_realistic_kpis(spend_amount, "instagram", ai_campaign["objective"])
            
            campaign = {
                "campaign_id": f"ig_camp_{campaign_idx+1:04d}",
                "name": ai_campaign["name"],
                "platform": "instagram", 
                "status": random.choices(["active", "paused", "completed"], weights=[75, 15, 10])[0],
                "objective": ai_campaign["objective"],
                "budget_type": "daily",
                "budget_amount": round(budget_amount, 2),
                "spend_amount": round(spend_amount, 2),
                "remaining_budget": round(budget_amount - spend_amount, 2),  
                "impressions": kpis["impressions"],
                "clicks": kpis["clicks"],
                "conversions": kpis["conversions"],
                "revenue": kpis["revenue"],
                "ctr": kpis["ctr"],
                "cpc": kpis["cpc"],
                "cpm": kpis["cpm"],
                "cpa": round(spend_amount / kpis["conversions"], 2) if kpis["conversions"] > 0 else 0,
                "roas": kpis["roas"],
                "is_optimized": random.choice([True, False]),
                "optimization_score": random.uniform(0.5, 0.92),
                "target_audience": audience_creative["target_audience"],
                "ad_creative": audience_creative["ad_creative"],
                "campaign_settings": generate_campaign_settings("instagram", ai_campaign["objective"]),
                "start_date": fake.date_between(start_date="-90d", end_date="-7d"),
                "end_date": fake.date_between(start_date="+7d", end_date="+60d") if random.choice([True, False]) else None,
                "created_at": fake.date_time_between(start_date="-100d", end_date="-90d"),
                "updated_at": fake.date_time_between(start_date="-7d", end_date="now")
            }
            all_campaigns.append(campaign)
    
    print(f"✅ Generated {len([c for c in all_campaigns if c['platform'] == 'instagram'])} Instagram campaigns")
    
    # Generate metrics for campaigns with progress tracking
    print(f"\n📈 Generating campaign metrics...")
    print("=" * 50)
    
    # Generate metrics for all campaigns (30 days each)
    total_campaigns = len(all_campaigns)
    metrics_campaigns = all_campaigns[:min(100, total_campaigns)]  # Limit to 100 campaigns for metrics
    
    print(f"📊 Processing metrics for {len(metrics_campaigns)} campaigns (30 days each)...")
    
    for idx, campaign in enumerate(metrics_campaigns):
        if (idx + 1) % 10 == 0:
            print(f"  ✓ Generated metrics for {idx + 1}/{len(metrics_campaigns)} campaigns")
        
        campaign_metrics = generate_campaign_metrics(campaign, days=30)
        all_metrics.extend(campaign_metrics)
    
    print(f"✅ Generated {len(all_metrics)} metrics records")
    
    # Generate agent executions
    print(f"\n🤖 Generating agent executions...")
    agent_executions = generate_agent_executions(50)
    print(f"✅ Generated {len(agent_executions)} agent execution records")
    
    print(f"\n🎯 FINAL SUMMARY:")
    print(f"   📊 Total campaigns: {len(all_campaigns)}")
    print(f"   📘 Facebook campaigns: {len([c for c in all_campaigns if c['platform'] == 'facebook'])}")
    print(f"   📷 Instagram campaigns: {len([c for c in all_campaigns if c['platform'] == 'instagram'])}")
    print(f"   📈 Metrics records: {len(all_metrics)}")
    print(f"   🤖 Agent executions: {len(agent_executions)}")
    
    return {
        "campaigns": all_campaigns,
        "metrics": all_metrics,
        "agent_executions": agent_executions
    } 