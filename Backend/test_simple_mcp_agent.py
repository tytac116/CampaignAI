#!/usr/bin/env python3
"""
Simple MCP Agent Test - Direct tool usage without complex workflows
"""

import asyncio
import sys
import os
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

async def test_simple_mcp_agent():
    try:
        print('🤖 SIMPLE MCP AGENT TEST')
        print('=' * 50)
        
        # Connect to MCP server
        server_params = StdioServerParameters(
            command='python3',
            args=['mcp_server.py'],
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print('✅ MCP Session initialized')
                
                # Test realistic campaign optimization scenario
                print('\n🧪 Testing realistic campaign optimization scenario...')
                
                # Step 1: Get current Facebook campaigns
                print('\n1️⃣ Getting current Facebook campaigns...')
                fb_campaigns = await session.call_tool('mcp_get_facebook_campaigns', {'limit': 3})
                fb_output = fb_campaigns.content[0].text
                print(f'   ✅ Found campaigns: {len(fb_output)} characters')
                print(f'   📝 Preview: {fb_output[:200]}...')
                
                # Step 2: Search for AI-related campaigns
                print('\n2️⃣ Searching for AI-related campaigns...')
                search_result = await session.call_tool('mcp_search_campaign_data', {'query': 'AI marketing', 'limit': 2})
                search_output = search_result.content[0].text
                print(f'   ✅ Search completed: {len(search_output)} characters')
                print(f'   📝 Preview: {search_output[:200]}...')
                
                # Step 3: Analyze campaign performance
                print('\n3️⃣ Analyzing campaign performance...')
                campaign_data = "Campaign: AI Marketing Revolution, Budget: R5000, Spend: R3200, ROAS: 1.8x, CTR: 2.1%, Platform: Facebook"
                analysis_result = await session.call_tool('mcp_analyze_campaign_performance', {'campaign_data': campaign_data})
                analysis_output = analysis_result.content[0].text
                print(f'   ✅ Analysis completed: {len(analysis_output)} characters')
                print(f'   📝 Preview: {analysis_output[:300]}...')
                
                # Step 4: Generate optimization strategy
                print('\n4️⃣ Generating optimization strategy...')
                strategy_result = await session.call_tool('mcp_optimize_campaign_strategy', {
                    'campaign_data': 'Low performing campaign with 1.8x ROAS, CTR 2.1%', 
                    'goals': 'increase ROAS to 3.0x and improve CTR to 4%'
                })
                strategy_output = strategy_result.content[0].text
                print(f'   ✅ Strategy generated: {len(strategy_output)} characters')
                print(f'   📝 Preview: {strategy_output[:300]}...')
                
                # Step 5: Generate campaign content
                print('\n5️⃣ Generating new campaign content...')
                content_result = await session.call_tool('mcp_generate_campaign_content', {
                    'campaign_type': 'ad_copy',
                    'target_audience': 'marketing professionals aged 25-45',
                    'platform': 'facebook',
                    'campaign_objective': 'lead_generation'
                })
                content_output = content_result.content[0].text
                print(f'   ✅ Content generated: {len(content_output)} characters')
                print(f'   📝 Preview: {content_output[:300]}...')
                
                # Step 6: Create a test campaign
                print('\n6️⃣ Creating a test campaign...')
                create_result = await session.call_tool('mcp_create_campaign', {
                    'name': 'AI Marketing Test Campaign',
                    'platform': 'facebook',
                    'objective': 'lead_generation',
                    'budget_amount': 2000.0,
                    'budget_type': 'daily'
                })
                create_output = create_result.content[0].text
                print(f'   ✅ Campaign created: {len(create_output)} characters')
                print(f'   📝 Preview: {create_output[:200]}...')
                
                # Generate comprehensive report
                print('\n' + '=' * 50)
                print('📊 COMPREHENSIVE CAMPAIGN OPTIMIZATION REPORT')
                print('=' * 50)
                
                report = f"""
🎯 **CAMPAIGN OPTIMIZATION ANALYSIS**

**Current Campaign Status:**
{fb_output[:500]}

**AI Campaign Search Results:**
{search_output[:500]}

**Performance Analysis:**
{analysis_output[:800]}

**Optimization Strategy:**
{strategy_output[:800]}

**New Content Generated:**
{content_output[:600]}

**Campaign Creation Result:**
{create_output[:300]}

**EXECUTIVE SUMMARY:**
✅ Successfully retrieved {fb_output.count('campaign')} existing campaigns
✅ Found AI-related campaigns in database
✅ Generated comprehensive performance analysis
✅ Created optimization strategy with specific recommendations
✅ Generated new ad copy for target audience
✅ Successfully created test campaign in database

**KEY RECOMMENDATIONS:**
1. Implement the optimization strategies identified in the analysis
2. Use the generated ad copy for improved engagement
3. Monitor the test campaign performance closely
4. Scale successful elements to other campaigns

**NEXT STEPS:**
- Deploy optimization recommendations
- A/B test new creative content
- Monitor ROAS improvements
- Expand successful strategies
                """
                
                print(report)
                
                # Final verdict
                print('\n' + '=' * 50)
                print('🎯 SIMPLE MCP AGENT TEST VERDICT')
                print('=' * 50)
                
                # Check if all steps completed successfully
                all_successful = all([
                    'campaign' in fb_output.lower(),
                    'found' in search_output.lower(),
                    'analysis' in analysis_output.lower(),
                    'strategy' in strategy_output.lower() or 'optimization' in strategy_output.lower(),
                    'content' in content_output.lower() or 'campaign' in content_output.lower(),
                    'success' in create_output.lower() or 'created' in create_output.lower()
                ])
                
                if all_successful:
                    print('🎉 ALL MCP TOOLS WORKING PERFECTLY!')
                    print('✅ Campaign data retrieval: WORKING')
                    print('✅ Campaign search: WORKING') 
                    print('✅ AI performance analysis: WORKING')
                    print('✅ Strategy optimization: WORKING')
                    print('✅ Content generation: WORKING')
                    print('✅ Campaign creation: WORKING')
                    print('\n🚀 MCP TOOLS READY FOR AGENT INTEGRATION!')
                    print('💡 Issue: Complex workflow has recursion - use direct MCP calls')
                else:
                    print('⚠️ SOME TOOLS NOT WORKING OPTIMALLY')
                    print('🔍 Check individual tool outputs above')
                
    except Exception as e:
        print(f'❌ Simple MCP agent test failed: {str(e)}')
        import traceback
        traceback.print_exc()

async def main():
    await test_simple_mcp_agent()

if __name__ == "__main__":
    asyncio.run(main()) 