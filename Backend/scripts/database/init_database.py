#!/usr/bin/env python3

"""
Database initialization and seeding script.
"""

import asyncio
import logging
from dotenv import load_dotenv
from app.services.supabase_service import supabase_service
from app.data.data_generator import CampaignDataGenerator
from app.data.supabase_seeder import SupabaseDataSeeder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def initialize_database():
    """Initialize the database with tables and seed data."""
    
    print("🚀 Starting database initialization...")
    
    # Step 1: Test connection
    print("\n📡 Testing Supabase connection...")
    if not supabase_service.get_client():
        print("❌ Failed to connect to Supabase")
        return False
    print("✅ Connected to Supabase successfully")
    
    # Step 2: Create tables
    print("\n🔨 Creating database tables...")
    if not supabase_service.create_tables():
        print("❌ Failed to create tables")
        return False
    print("✅ Database tables created successfully")
    
    # Step 3: Generate and seed data
    print("\n📊 Generating campaign data...")
    try:
        # Initialize data generator
        data_generator = CampaignDataGenerator()
        
        # Generate Facebook campaigns
        print("📘 Generating Facebook campaigns...")
        facebook_campaigns = data_generator.generate_facebook_campaigns(500)
        print(f"✅ Generated {len(facebook_campaigns)} Facebook campaigns")
        
        # Generate Instagram campaigns
        print("📷 Generating Instagram campaigns...")
        instagram_campaigns = data_generator.generate_instagram_campaigns(500)
        print(f"✅ Generated {len(instagram_campaigns)} Instagram campaigns")
        
        # Initialize data seeder
        seeder = SupabaseDataSeeder(supabase_service.get_client())
        
        # Seed Facebook data
        print("\n💾 Seeding Facebook campaign data...")
        if seeder.seed_campaigns(facebook_campaigns, "facebook"):
            print("✅ Facebook campaigns seeded successfully")
        else:
            print("❌ Failed to seed Facebook campaigns")
            return False
        
        # Seed Instagram data
        print("💾 Seeding Instagram campaign data...")
        if seeder.seed_campaigns(instagram_campaigns, "instagram"):
            print("✅ Instagram campaigns seeded successfully")
        else:
            print("❌ Failed to seed Instagram campaigns")
            return False
        
        # Generate and seed metrics data
        print("\n📈 Generating campaign metrics...")
        all_campaigns = facebook_campaigns + instagram_campaigns
        
        facebook_metrics = data_generator.generate_campaign_metrics(facebook_campaigns[:100], days=30)
        instagram_metrics = data_generator.generate_campaign_metrics(instagram_campaigns[:100], days=30)
        
        print(f"✅ Generated {len(facebook_metrics)} Facebook metrics records")
        print(f"✅ Generated {len(instagram_metrics)} Instagram metrics records")
        
        # Seed metrics data
        print("💾 Seeding campaign metrics...")
        all_metrics = facebook_metrics + instagram_metrics
        if seeder.seed_campaign_metrics(all_metrics):
            print("✅ Campaign metrics seeded successfully")
        else:
            print("❌ Failed to seed campaign metrics")
            return False
        
        print("\n🎉 Database initialization completed successfully!")
        print(f"📊 Summary:")
        print(f"   • Facebook campaigns: {len(facebook_campaigns)}")
        print(f"   • Instagram campaigns: {len(instagram_campaigns)}")
        print(f"   • Total metrics records: {len(all_metrics)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate or seed data: {e}")
        print(f"❌ Error during data generation: {e}")
        return False


if __name__ == "__main__":
    success = initialize_database()
    exit(0 if success else 1) 