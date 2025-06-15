import random
import json
from datetime import datetime, timedelta, date
from typing import List, Dict, Any
from faker import Faker
from ..models.campaign import PlatformType, CampaignStatus

fake = Faker()
Faker.seed(42)  # For reproducible data


class CampaignDataGenerator:
    """
    Generates realistic campaign data for Facebook and Instagram platforms.
    """
    
    def __init__(self):
        self.campaign_objectives = [
            "conversions", "traffic", "brand_awareness", "reach", "engagement",
            "app_installs", "video_views", "lead_generation", "catalog_sales"
        ]
        
        self.ad_placements = {
            "facebook": ["news_feed", "right_column", "marketplace", "stories", "reels", "video_feeds"],
            "instagram": ["feed", "stories", "reels", "explore", "shop"]
        }
        
        self.age_groups = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
        self.countries = ["USA", "Canada", "UK", "Australia", "Germany", "France", "Italy", "Spain"]
        self.device_types = ["mobile", "desktop", "tablet"]
        
    def generate_target_audience(self) -> Dict[str, Any]:
        """Generate realistic target audience data."""
        return {
            "age_range": {
                "min": random.randint(18, 25),
                "max": random.randint(35, 65)
            },
            "genders": random.choices(["male", "female", "all"], weights=[30, 30, 40], k=1)[0],
            "locations": random.sample(self.countries, k=random.randint(1, 4)),
            "interests": [
                fake.word() for _ in range(random.randint(3, 8))
            ],
            "behaviors": [
                f"{fake.word()}_behavior" for _ in range(random.randint(2, 5))
            ],
            "custom_audiences": random.choice([True, False]),
            "lookalike_percentage": random.randint(1, 10) if random.choice([True, False]) else None
        }
    
    def generate_ad_creative(self, platform: PlatformType) -> Dict[str, Any]:
        """Generate ad creative data."""
        creative_types = ["image", "video", "carousel", "collection"]
        creative_type = random.choice(creative_types)
        
        creative = {
            "type": creative_type,
            "headline": fake.catch_phrase(),
            "description": fake.text(max_nb_chars=150),
            "call_to_action": random.choice([
                "learn_more", "shop_now", "sign_up", "download", "contact_us",
                "book_travel", "apply_now", "get_quote", "subscribe"
            ])
        }
        
        if creative_type == "image":
            creative["image_url"] = f"https://picsum.photos/1200/628?random={random.randint(1, 1000)}"
        elif creative_type == "video":
            creative["video_url"] = f"https://sample-videos.com/sample-video-{random.randint(1, 100)}.mp4"
            creative["thumbnail_url"] = f"https://picsum.photos/1200/628?random={random.randint(1, 1000)}"
        elif creative_type == "carousel":
            creative["cards"] = [
                {
                    "image_url": f"https://picsum.photos/1200/628?random={random.randint(1, 1000)}",
                    "headline": fake.catch_phrase(),
                    "description": fake.text(max_nb_chars=100)
                }
                for _ in range(random.randint(2, 6))
            ]
        
        return creative
    
    def generate_campaign_settings(self, platform: PlatformType) -> Dict[str, Any]:
        """Generate campaign settings."""
        return {
            "placements": random.sample(
                self.ad_placements[platform.value], 
                k=random.randint(1, len(self.ad_placements[platform.value]))
            ),
            "schedule": {
                "start_time": "06:00",
                "end_time": "23:00",
                "days_of_week": random.sample(
                    ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
                    k=random.randint(5, 7)
                )
            },
            "bid_strategy": random.choice([
                "lowest_cost", "cost_cap", "bid_cap", "target_cost"
            ]),
            "optimization_goal": random.choice([
                "conversions", "clicks", "impressions", "reach", "engagement"
            ]),
            "delivery_type": random.choice(["standard", "accelerated"])
        }
    
    def calculate_realistic_kpis(self, spend: float, platform: PlatformType) -> Dict[str, float]:
        """Calculate realistic KPIs based on spend and platform."""
        # Platform-specific base rates
        base_rates = {
            PlatformType.FACEBOOK: {
                "cpm_range": (8, 15),
                "ctr_range": (0.8, 2.5),
                "conversion_rate_range": (1.5, 4.0),
                "engagement_rate_range": (0.5, 1.5)
            },
            PlatformType.INSTAGRAM: {
                "cpm_range": (10, 18),
                "ctr_range": (0.6, 2.0),
                "conversion_rate_range": (1.2, 3.5),
                "engagement_rate_range": (1.0, 3.0)
            }
        }
        
        rates = base_rates[platform]
        
        # Generate correlated metrics
        cpm = random.uniform(*rates["cpm_range"])
        impressions = int(spend / cpm * 1000)
        
        ctr = random.uniform(*rates["ctr_range"]) / 100
        clicks = int(impressions * ctr)
        cpc = spend / clicks if clicks > 0 else 0
        
        conversion_rate = random.uniform(*rates["conversion_rate_range"]) / 100
        conversions = int(clicks * conversion_rate)
        
        # Revenue modeling (some campaigns might not have revenue)
        has_revenue = random.choice([True, False])
        if has_revenue:
            avg_order_value = random.uniform(25, 200)
            revenue = conversions * avg_order_value
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
            "conversion_rate": round(conversion_rate * 100, 2),
            "revenue": round(revenue, 2),
            "roas": round(roas, 2)
        }
    
    def generate_demographics_data(self, total_impressions: int) -> Dict[str, Dict]:
        """Generate demographic breakdown data."""
        # Age demographics
        age_weights = [0.25, 0.30, 0.20, 0.15, 0.08, 0.02]  # 18-24, 25-34, etc.
        age_distribution = {}
        remaining_impressions = total_impressions
        
        for i, age_group in enumerate(self.age_groups[:-1]):
            impressions = int(total_impressions * age_weights[i])
            remaining_impressions -= impressions
            age_distribution[age_group] = {
                "impressions": impressions,
                "clicks": int(impressions * random.uniform(0.005, 0.025))
            }
        
        # Add remaining to last group
        age_distribution[self.age_groups[-1]] = {
            "impressions": remaining_impressions,
            "clicks": int(remaining_impressions * random.uniform(0.005, 0.025))
        }
        
        # Gender demographics
        gender_split = random.choice([
            {"male": 0.6, "female": 0.4},
            {"male": 0.4, "female": 0.6},
            {"male": 0.5, "female": 0.5}
        ])
        
        gender_distribution = {}
        for gender, percentage in gender_split.items():
            impressions = int(total_impressions * percentage)
            gender_distribution[gender] = {
                "impressions": impressions,
                "clicks": int(impressions * random.uniform(0.005, 0.025))
            }
        
        # Location demographics
        location_weights = [0.4, 0.2, 0.15, 0.1, 0.08, 0.04, 0.02, 0.01]
        location_distribution = {}
        
        for i, country in enumerate(self.countries):
            if i < len(location_weights):
                impressions = int(total_impressions * location_weights[i])
                location_distribution[country] = {
                    "impressions": impressions,
                    "clicks": int(impressions * random.uniform(0.005, 0.025))
                }
        
        # Device demographics
        device_weights = {"mobile": 0.7, "desktop": 0.25, "tablet": 0.05}
        device_distribution = {}
        
        for device, percentage in device_weights.items():
            impressions = int(total_impressions * percentage)
            device_distribution[device] = {
                "impressions": impressions,
                "clicks": int(impressions * random.uniform(0.005, 0.025))
            }
        
        return {
            "age_demographics": age_distribution,
            "gender_demographics": gender_distribution,
            "location_demographics": location_distribution,
            "device_demographics": device_distribution
        }
    
    def generate_campaign(self, platform: PlatformType) -> Dict[str, Any]:
        """Generate a complete campaign with realistic data."""
        # Basic campaign info
        campaign_name = f"{platform.value.title()} {fake.company()} - {fake.catch_phrase()}"
        budget = random.uniform(100, 10000)
        daily_budget = budget / random.randint(7, 30)  # Campaign duration
        spend = random.uniform(budget * 0.1, budget * 0.95)  # Random spend within budget
        
        # Calculate KPIs
        kpis = self.calculate_realistic_kpis(spend, platform)
        
        # Generate demographics
        demographics = self.generate_demographics_data(kpis["impressions"])
        
        # Create campaign data
        campaign_data = {
            "name": campaign_name,
            "platform": platform,
            "status": random.choices(
                list(CampaignStatus), 
                weights=[60, 20, 15, 5]  # active, paused, completed, draft
            )[0],
            "budget": round(budget, 2),
            "daily_budget": round(daily_budget, 2),
            "spend": round(spend, 2),
            "objective": random.choice(self.campaign_objectives),
            "target_audience": self.generate_target_audience(),
            "ad_creative": self.generate_ad_creative(platform),
            "campaign_settings": self.generate_campaign_settings(platform),
            
            # Performance metrics
            "impressions": kpis["impressions"],
            "clicks": kpis["clicks"],
            "conversions": kpis["conversions"],
            "revenue": kpis["revenue"],
            "cpm": kpis["cpm"],
            "cpc": kpis["cpc"],
            "ctr": kpis["ctr"],
            "conversion_rate": kpis["conversion_rate"],
            "roas": kpis["roas"],
            
            # Optimization
            "is_optimized": random.choice([True, False]),
            "optimization_score": random.uniform(60, 95),
            
            # Timestamps
            "start_date": fake.date_between(start_date="-30d", end_date="-1d"),
            "end_date": fake.date_between(start_date="today", end_date="+30d"),
        }
        
        return campaign_data, demographics
    
    def generate_campaign_metrics(self, campaign_id: int, start_date: date, end_date: date, 
                                base_impressions: int) -> List[Dict[str, Any]]:
        """Generate time-series metrics data for a campaign."""
        metrics_data = []
        current_date = start_date
        
        while current_date <= end_date:
            # Daily variance (weekends typically perform differently)
            weekend_multiplier = 0.7 if current_date.weekday() >= 5 else 1.0
            daily_impressions = int(base_impressions * random.uniform(0.8, 1.2) * weekend_multiplier / 
                                  (end_date - start_date).days)
            
            # Generate hourly data for some days
            hours_to_generate = [0] if random.random() > 0.3 else range(0, 24, 4)  # Generate hourly or daily
            
            for hour in hours_to_generate:
                hour_multiplier = 1.0 if hour == 0 else random.uniform(0.02, 0.15)  # Hour 0 = daily total
                hour_impressions = int(daily_impressions * hour_multiplier) if hour > 0 else daily_impressions
                
                # Calculate other metrics based on impressions
                clicks = int(hour_impressions * random.uniform(0.005, 0.025))
                conversions = int(clicks * random.uniform(0.01, 0.05))
                spend = hour_impressions * random.uniform(0.008, 0.015) / 1000
                revenue = conversions * random.uniform(25, 150) if random.random() > 0.3 else 0
                
                # Engagement metrics
                likes = int(hour_impressions * random.uniform(0.001, 0.008))
                shares = int(likes * random.uniform(0.1, 0.3))
                comments = int(likes * random.uniform(0.05, 0.2))
                saves = int(likes * random.uniform(0.02, 0.1))
                
                # Video metrics (if applicable)
                video_views = int(hour_impressions * random.uniform(0.3, 0.8)) if random.random() > 0.5 else 0
                video_completion_rate = random.uniform(0.2, 0.7) if video_views > 0 else 0
                
                # Calculate KPIs
                cpm = (spend / hour_impressions * 1000) if hour_impressions > 0 else 0
                cpc = (spend / clicks) if clicks > 0 else 0
                ctr = (clicks / hour_impressions * 100) if hour_impressions > 0 else 0
                conversion_rate = (conversions / clicks * 100) if clicks > 0 else 0
                roas = (revenue / spend) if spend > 0 else 0
                
                metrics_data.append({
                    "campaign_id": campaign_id,
                    "date": current_date,
                    "hour": hour,
                    "impressions": hour_impressions,
                    "clicks": clicks,
                    "conversions": conversions,
                    "spend": round(spend, 2),
                    "revenue": round(revenue, 2),
                    "likes": likes,
                    "shares": shares,
                    "comments": comments,
                    "saves": saves,
                    "video_views": video_views,
                    "video_completion_rate": round(video_completion_rate, 2),
                    "cpm": round(cpm, 2),
                    "cpc": round(cpc, 2),
                    "ctr": round(ctr, 2),
                    "conversion_rate": round(conversion_rate, 2),
                    "cost_per_conversion": round(spend / conversions, 2) if conversions > 0 else 0,
                    "roas": round(roas, 2),
                    "frequency": round(random.uniform(1.0, 3.5), 2),
                    "reach": int(hour_impressions / random.uniform(1.0, 3.5)),
                    "performance_score": random.uniform(60, 95),
                    "trend_direction": random.choice(["up", "down", "stable"]),
                    "quality_score": random.uniform(5, 10),
                    "relevance_score": random.uniform(5, 10)
                })
            
            current_date += timedelta(days=1)
        
        return metrics_data


def generate_realistic_data(facebook_count: int = 500, instagram_count: int = 500) -> Dict[str, List]:
    """
    Generate realistic campaign data for both platforms.
    
    Args:
        facebook_count: Number of Facebook campaigns to generate
        instagram_count: Number of Instagram campaigns to generate
        
    Returns:
        Dictionary containing campaigns, demographics, and metrics data
    """
    generator = CampaignDataGenerator()
    
    campaigns = []
    all_demographics = []
    all_metrics = []
    
    # Generate Facebook campaigns
    for _ in range(facebook_count):
        campaign_data, demographics = generator.generate_campaign(PlatformType.FACEBOOK)
        campaigns.append(campaign_data)
        all_demographics.append(demographics)
    
    # Generate Instagram campaigns
    for _ in range(instagram_count):
        campaign_data, demographics = generator.generate_campaign(PlatformType.INSTAGRAM)
        campaigns.append(campaign_data)
        all_demographics.append(demographics)
    
    # Generate metrics for each campaign
    for i, campaign in enumerate(campaigns):
        start_date = campaign["start_date"]
        end_date = min(campaign["end_date"], date.today())  # Don't generate future metrics
        
        if end_date > start_date:
            campaign_metrics = generator.generate_campaign_metrics(
                campaign_id=i + 1,  # Assuming sequential IDs
                start_date=start_date,
                end_date=end_date,
                base_impressions=campaign["impressions"]
            )
            all_metrics.extend(campaign_metrics)
    
    return {
        "campaigns": campaigns,
        "demographics": all_demographics,
        "metrics": all_metrics
    } 