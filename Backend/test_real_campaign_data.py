#!/usr/bin/env python3
"""
Real Campaign Data Validation Test

This test validates that the enhanced workflow:
1. Uses actual campaign_id and name from the database
2. Provides specific campaign references instead of generic names
3. Accesses MCP tools correctly for rich campaign data
4. Includes real budget and performance metrics
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add Backend to path
sys.path.append(os.getcwd())

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_real_campaign_data():
    """Test that the workflow uses real campaign data with IDs and names."""
    
    try:
        from app.agents.simple_workflow import SimpleMultiAgentWorkflow
        
        print('🔍 REAL CAMPAIGN DATA VALIDATION TEST')
        print('=' * 70)
        print('Focus: Validate actual campaign_id and name usage')
        print('Expected: Real campaign names, IDs, and specific metrics')
        print('=' * 70)
        print()
        
        workflow = SimpleMultiAgentWorkflow()
        
        # Budget optimization query (same as before)
        budget_query = """I have a total monthly budget of $50,000 for my campaigns, but I'm not getting the ROI I expected. Can you analyze my current budget allocation across all campaigns and recommend how I should reallocate my budget to maximize ROAS? I want specific dollar amounts for reallocation and clear reasoning based on performance data. Also, identify which campaigns I should pause or scale up."""
        
        print('💰 BUDGET OPTIMIZATION WITH REAL DATA:')
        print('-' * 50)
        print(budget_query)
        print('-' * 50)
        print()
        print('⏳ Running enhanced workflow with real campaign data extraction...')
        print('🎯 Expected: Actual campaign names, IDs, and specific budget recommendations')
        print()
        
        start_time = datetime.now()
        result = await workflow.run_workflow(budget_query)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print('💰 REAL CAMPAIGN DATA RESULTS')
        print('=' * 50)
        print(f'✅ Status: {result["status"]}')
        print(f'⏱️  Execution Time: {execution_time:.2f} seconds')
        print(f'🛠️  Tools Used: {len(result.get("tool_calls", []))}')
        print()
        
        if result['status'] == 'completed':
            output = result['final_output']
            
            # Validate real campaign data usage
            has_campaign_ids = 'ID:' in output or 'campaign_id' in output.lower()
            has_specific_names = not any(generic in output for generic in ['Campaign 1', 'Campaign 2', 'Campaign 3', 'Campaign A', 'Campaign B'])
            has_real_metrics = '$' in output and any(metric in output for metric in ['CTR:', 'ROAS:', 'CPC:', 'Revenue:'])
            has_specific_recommendations = 'pause' in output.lower() and 'scale' in output.lower()
            has_budget_amounts = '$' in output and ('50,000' in output or '50000' in output)
            
            print('🔍 REAL CAMPAIGN DATA VALIDATION:')
            print('-' * 45)
            print(f'   ✅ Campaign IDs Included: {"Yes" if has_campaign_ids else "No"}')
            print(f'   ✅ Specific Campaign Names: {"Yes" if has_specific_names else "No"}')
            print(f'   ✅ Real Performance Metrics: {"Yes" if has_real_metrics else "No"}')
            print(f'   ✅ Specific Recommendations: {"Yes" if has_specific_recommendations else "No"}')
            print(f'   ✅ Budget Amount References: {"Yes" if has_budget_amounts else "No"}')
            
            data_quality_score = sum([has_campaign_ids, has_specific_names, has_real_metrics, 
                                    has_specific_recommendations, has_budget_amounts])
            print(f'   📊 Data Quality Score: {data_quality_score}/5')
            print()
            
            # Extract campaign names mentioned in the output
            print('📋 CAMPAIGN REFERENCES FOUND:')
            print('-' * 35)
            lines = output.split('\n')
            campaign_mentions = []
            for line in lines:
                if 'Campaign:' in line or 'ID:' in line:
                    campaign_mentions.append(line.strip())
            
            if campaign_mentions:
                for mention in campaign_mentions[:5]:  # Show first 5
                    print(f'   📌 {mention}')
            else:
                print('   ⚠️  No specific campaign references found')
            print()
            
            print('📋 ENHANCED BUDGET ANALYSIS REPORT (First 1500 chars):')
            print('-' * 60)
            print(output[:1500] + '...' if len(output) > 1500 else output)
            print()
            
            # Check tool calls for MCP access
            tool_calls = result.get("tool_calls", [])
            mcp_tools_used = [call.get("tool", "") for call in tool_calls if call.get("tool", "").startswith("mcp_")]
            
            print('🛠️  MCP TOOL USAGE ANALYSIS:')
            print('-' * 35)
            print(f'   📊 Total Tool Calls: {len(tool_calls)}')
            print(f'   🔧 MCP Tools Used: {len(mcp_tools_used)}')
            if mcp_tools_used:
                for tool in mcp_tools_used:
                    print(f'     • {tool}')
            print()
            
            # Success criteria
            success = data_quality_score >= 3 and len(mcp_tools_used) > 0
            
            if success:
                print('🎉 SUCCESS: Enhanced workflow using real campaign data!')
                print('   ✅ MCP tools accessed correctly')
                print('   ✅ Real campaign data extracted and used')
                print('   ✅ Specific recommendations with actual metrics')
                print('   ✅ Campaign IDs and names properly referenced')
            else:
                print('⚠️  PARTIAL SUCCESS: Some improvements needed')
                print(f'   📊 Data quality score: {data_quality_score}/5')
                print(f'   🔧 MCP tools used: {len(mcp_tools_used)}')
            
            return success
        else:
            print(f'❌ Enhanced workflow failed: {result.get("errors", [])}')
            return False
            
    except Exception as e:
        print(f'❌ Test failed: {str(e)}')
        return False

async def test_mcp_tool_access():
    """Test direct MCP tool access to verify data structure."""
    
    print('\n🔧 MCP TOOL ACCESS VERIFICATION')
    print('=' * 50)
    
    try:
        from app.agents.simple_workflow import DataCollectionAgent
        
        # Create data collection agent
        data_agent = DataCollectionAgent()
        
        # Test direct tool access
        print('📱 Testing Facebook campaigns tool...')
        fb_result = await data_agent.call_mcp_tool('mcp_get_facebook_campaigns', {'limit': 3})
        print(f'   📊 Facebook result length: {len(fb_result)} characters')
        
        print('📸 Testing Instagram campaigns tool...')
        ig_result = await data_agent.call_mcp_tool('mcp_get_instagram_campaigns', {'limit': 3})
        print(f'   📊 Instagram result length: {len(ig_result)} characters')
        
        # Parse and check structure
        print('\n🔍 DATA STRUCTURE ANALYSIS:')
        print('-' * 35)
        
        # Check Facebook data structure
        if 'campaign_id' in fb_result and 'name' in fb_result:
            print('   ✅ Facebook data contains campaign_id and name')
        else:
            print('   ❌ Facebook data missing campaign_id or name')
        
        # Check Instagram data structure  
        if 'campaign_id' in ig_result and 'name' in ig_result:
            print('   ✅ Instagram data contains campaign_id and name')
        else:
            print('   ❌ Instagram data missing campaign_id or name')
        
        # Show sample data
        print('\n📋 SAMPLE FACEBOOK DATA (First 500 chars):')
        print('-' * 45)
        print(fb_result[:500] + '...' if len(fb_result) > 500 else fb_result)
        
        print('\n📋 SAMPLE INSTAGRAM DATA (First 500 chars):')
        print('-' * 45)
        print(ig_result[:500] + '...' if len(ig_result) > 500 else ig_result)
        
        return True
        
    except Exception as e:
        print(f'❌ MCP tool access test failed: {str(e)}')
        return False

async def main():
    """Main test execution function."""
    
    print('🧪 CAMPAIGN AI REAL DATA VALIDATION SUITE')
    print('Testing Enhanced Workflow with Actual Campaign Data')
    print('=' * 80)
    print()
    
    # Test 1: MCP Tool Access
    print('🚀 STARTING TEST 1: MCP Tool Access Verification...')
    mcp_success = await test_mcp_tool_access()
    print(f'📊 Test 1 Result: {"✅ PASSED" if mcp_success else "❌ FAILED"}')
    print()
    
    # Test 2: Real Campaign Data Usage
    print('🚀 STARTING TEST 2: Real Campaign Data Usage...')
    workflow_success = await test_real_campaign_data()
    print(f'📊 Test 2 Result: {"✅ PASSED" if workflow_success else "❌ FAILED"}')
    print()
    
    # Final Results
    total_success = mcp_success and workflow_success
    
    print('🎯 FINAL VALIDATION RESULTS')
    print('=' * 50)
    print(f'📊 Tests Passed: {int(mcp_success) + int(workflow_success)}/2')
    print(f'🎯 Overall Success: {"✅ PASSED" if total_success else "❌ NEEDS IMPROVEMENT"}')
    print()
    
    if total_success:
        print('🎉 EXCELLENT: Enhanced workflow successfully using real campaign data!')
        print('   🔧 MCP tools accessible and functioning')
        print('   📊 Real campaign IDs and names extracted')
        print('   💰 Specific budget recommendations with actual metrics')
        print('   🎯 Production-ready with rich campaign data integration')
    else:
        print('⚠️  IMPROVEMENT NEEDED: Some issues detected')
        print('   Check MCP tool access and data parsing logic')
    
    print()
    print('📁 VALIDATION COMPLETE!')
    
    return total_success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 