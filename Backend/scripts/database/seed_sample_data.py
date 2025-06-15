#!/usr/bin/env python3

"""
Simple script to seed sample campaign data into Supabase.
"""

import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from app.services.supabase_service import supabase_service
from app.data.data_generator import CampaignDataGenerator
from app.data.supabase_seeder import SupabaseDataSeeder

# Load environment variables
load_dotenv()

def seed_sample_data():
    """Seed sample campaign data."""
    print("🚀 Starting sample data seeding...")
    
    # Test connection
    print("\n📡 Testing Supabase connection...")
    client = supabase_service.get_client()
    if not client:
        print("❌ Failed to connect to Supabase")
        return False
    print("✅ Connected to Supabase successfully")
    
    # Check if tables exist
    try:
        campaigns_result = client.table('campaigns').select('id').limit(1).execute()
        print("✅ Tables are accessible")
    except Exception as e:
        print(f"❌ Error accessing tables: {e}")
        print("💡 Please run the SQL in create_tables.sql in your Supabase dashboard first")
        return False
    
    # Generate sample data
    print("\n📊 Generating sample campaign data...")
    try:
        data_generator = CampaignDataGenerator()
        
        # Generate fewer campaigns for testing
        print("📘 Generating Facebook campaigns...")
        facebook_campaigns = data_generator.generate_facebook_campaigns(50)  # Just 50 for testing
        print(f"✅ Generated {len(facebook_campaigns)} Facebook campaigns")
        
        print("📷 Generating Instagram campaigns...")
        instagram_campaigns = data_generator.generate_instagram_campaigns(50)  # Just 50 for testing
        print(f"✅ Generated {len(instagram_campaigns)} Instagram campaigns")
        
        # Initialize seeder
        seeder = SupabaseDataSeeder(client)
        
        # Seed Facebook campaigns
        print("\n💾 Seeding Facebook campaigns...")
        if seeder.seed_campaigns(facebook_campaigns, "facebook"):
            print("✅ Facebook campaigns seeded successfully")
        else:
            print("❌ Failed to seed Facebook campaigns")
            return False
        
        # Seed Instagram campaigns
        print("💾 Seeding Instagram campaigns...")
        if seeder.seed_campaigns(instagram_campaigns, "instagram"):
            print("✅ Instagram campaigns seeded successfully")
        else:
            print("❌ Failed to seed Instagram campaigns")
            return False
        
        # Generate and seed some metrics
        print("\n📈 Generating campaign metrics...")
        all_campaigns = facebook_campaigns + instagram_campaigns
        sample_campaigns = all_campaigns[:20]  # Just first 20 campaigns
        
        metrics = data_generator.generate_campaign_metrics(sample_campaigns, days=7)  # Just 7 days
        print(f"✅ Generated {len(metrics)} metrics records")
        
        print("💾 Seeding campaign metrics...")
        if seeder.seed_campaign_metrics(metrics):
            print("✅ Campaign metrics seeded successfully")
        else:
            print("❌ Failed to seed campaign metrics")
            return False
        
        print("\n🎉 Sample data seeding completed successfully!")
        print(f"📊 Summary:")
        print(f"   • Facebook campaigns: {len(facebook_campaigns)}")
        print(f"   • Instagram campaigns: {len(instagram_campaigns)}")
        print(f"   • Metrics records: {len(metrics)}")
        print("\n🧪 You can now test the API simulators!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during data generation: {e}")
        return False

if __name__ == "__main__":
    success = seed_sample_data()
    exit(0 if success else 1) 