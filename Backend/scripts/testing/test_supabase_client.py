import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client, Client

async def test_supabase_client():
    """Test Supabase connection using the official client."""
    
    # Load environment variables
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
    
    print("🔍 Checking Supabase client connection...")
    print(f"SUPABASE_URL: {supabase_url}")
    print(f"SUPABASE_ANON_KEY: {supabase_anon_key[:50] + '...' if supabase_anon_key else 'Not found'}")
    
    if not supabase_url or not supabase_anon_key:
        print("❌ Supabase credentials not found in environment")
        return False
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_anon_key)
        
        # Test query - get campaign count
        print("\n🔌 Testing Supabase client connection...")
        
        # Query campaigns table
        response = supabase.table('campaigns').select('id, name, platform, status').limit(5).execute()
        
        if response.data:
            print(f"✅ Connected successfully! Found {len(response.data)} campaigns (showing first 5)")
            
            for campaign in response.data:
                print(f"  📊 {campaign['name']} ({campaign['platform']}) - {campaign['status']}")
            
            # Get total count
            total_response = supabase.table('campaigns').select('id', count='exact').execute()
            print(f"\n📈 Total campaigns in database: {total_response.count}")
            
            # Get platform breakdown
            fb_response = supabase.table('campaigns').select('id', count='exact').eq('platform', 'facebook').execute()
            ig_response = supabase.table('campaigns').select('id', count='exact').eq('platform', 'instagram').execute()
            
            print(f"📘 Facebook campaigns: {fb_response.count}")
            print(f"📷 Instagram campaigns: {ig_response.count}")
            
            return True
        else:
            print("⚠️  No data returned from campaigns table")
            return False
            
    except Exception as e:
        print(f"❌ Supabase client connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_campaign_metrics():
    """Test campaign metrics table."""
    
    load_dotenv()
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
    
    try:
        supabase: Client = create_client(supabase_url, supabase_anon_key)
        
        print("\n📈 Testing campaign_metrics table...")
        
        # Get metrics count
        metrics_response = supabase.table('campaign_metrics').select('id', count='exact').limit(1).execute()
        print(f"✅ Found {metrics_response.count} campaign metrics records")
        
        # Get sample metrics
        sample_response = supabase.table('campaign_metrics').select('campaign_id, metric_date, impressions, clicks').limit(3).execute()
        
        if sample_response.data:
            print("📊 Sample metrics:")
            for metric in sample_response.data:
                print(f"  Campaign {metric['campaign_id']}: {metric['impressions']} impressions, {metric['clicks']} clicks on {metric['metric_date']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Metrics test failed: {e}")
        return False

async def test_agent_executions():
    """Test agent executions table."""
    
    load_dotenv()
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
    
    try:
        supabase: Client = create_client(supabase_url, supabase_anon_key)
        
        print("\n🤖 Testing agent_executions table...")
        
        # Get executions count
        exec_response = supabase.table('agent_executions').select('id', count='exact').limit(1).execute()
        print(f"✅ Found {exec_response.count} agent execution records")
        
        # Get sample executions
        sample_response = supabase.table('agent_executions').select('execution_id, workflow_type, status').limit(3).execute()
        
        if sample_response.data:
            print("🔧 Sample executions:")
            for execution in sample_response.data:
                print(f"  {execution['execution_id']}: {execution['workflow_type']} - {execution['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent executions test failed: {e}")
        return False

async def main():
    """Run all Supabase tests."""
    print("🧪 Testing Supabase Connection with Official Client")
    print("=" * 55)
    
    # Test main connection
    client_success = await test_supabase_client()
    
    if client_success:
        # Test other tables
        metrics_success = await test_campaign_metrics()
        executions_success = await test_agent_executions()
        
        print("\n" + "=" * 55)
        if client_success and metrics_success and executions_success:
            print("🎉 All Supabase tests passed!")
            print("✅ Database is working correctly")
            print("🚀 Ready to test API simulators")
        else:
            print("⚠️  Some tests failed")
    else:
        print("\n❌ Basic connection failed - cannot proceed with other tests")

if __name__ == "__main__":
    asyncio.run(main()) 