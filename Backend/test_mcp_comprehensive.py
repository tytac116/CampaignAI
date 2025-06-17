#!/usr/bin/env python3
"""
Comprehensive MCP Tools Test - Verify actual outputs
"""

import asyncio
import sys
import os
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

async def test_comprehensive_mcp():
    try:
        print('🔍 COMPREHENSIVE MCP TOOLS TEST')
        print('=' * 50)
        
        # Create server parameters
        server_params = StdioServerParameters(
            command='python3',
            args=['mcp_server.py'],
        )
        
        # Connect to MCP server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print('✅ MCP Session initialized')
                
                # Test 1: List all available tools
                print('\n📋 Test 1: Available Tools')
                tools_result = await session.list_tools()
                print(f'Found {len(tools_result.tools)} tools:')
                for tool in tools_result.tools:
                    print(f'  - {tool.name}')
                
                # Test 2: Test basic connection
                print('\n🔗 Test 2: Basic Connection Test')
                test_result = await session.call_tool('test_connection', {})
                print(f'Connection test: {test_result.content[0].text}')
                
                # Test 3: List campaigns by criteria (should return real data)
                print('\n📊 Test 3: List Facebook Campaigns')
                campaigns_result = await session.call_tool('mcp_list_campaigns_by_criteria', {
                    'platform': 'facebook',
                    'limit': 5
                })
                campaigns_output = campaigns_result.content[0].text
                print(f'Campaigns result length: {len(campaigns_output)} characters')
                print(f'First 500 chars: {campaigns_output[:500]}...')
                
                # Check if we got real data
                if 'Found' in campaigns_output and 'campaigns' in campaigns_output:
                    print('✅ SUCCESS: Got real campaign data!')
                else:
                    print('❌ FAILED: No real campaign data returned')
                    print(f'Full output: {campaigns_output}')
                
                # Test 4: Search for specific campaign
                print('\n🔍 Test 4: Search for "hospitality" campaigns')
                search_result = await session.call_tool('mcp_search_campaign_data', {
                    'query': 'hospitality',
                    'limit': 3
                })
                search_output = search_result.content[0].text
                print(f'Search result length: {len(search_output)} characters')
                print(f'First 300 chars: {search_output[:300]}...')
                
                # Check if we found the hospitality campaign
                if 'hospitality' in search_output.lower() and 'Found' in search_output:
                    print('✅ SUCCESS: Found hospitality campaign!')
                else:
                    print('❌ FAILED: No hospitality campaign found')
                    print(f'Full output: {search_output}')
                
                # Test 5: AI Analysis Tool
                print('\n🤖 Test 5: AI Campaign Analysis')
                analysis_result = await session.call_tool('mcp_analyze_campaign_performance', {
                    'campaign_data': 'Campaign: AI in Hospitality, Budget: R6056, Spend: R2869, ROAS: 2.1x, CTR: 3.2%, Platform: Instagram'
                })
                analysis_output = analysis_result.content[0].text
                print(f'Analysis result length: {len(analysis_output)} characters')
                print(f'First 400 chars: {analysis_output[:400]}...')
                
                # Check if AI analysis worked
                if 'analysis' in analysis_output.lower() and len(analysis_output) > 500:
                    print('✅ SUCCESS: AI analysis generated comprehensive output!')
                else:
                    print('❌ FAILED: AI analysis did not work properly')
                
                # Test 6: Get Instagram campaigns
                print('\n📱 Test 6: Get Instagram Campaigns')
                instagram_result = await session.call_tool('mcp_get_instagram_campaigns', {
                    'limit': 3
                })
                instagram_output = instagram_result.content[0].text
                print(f'Instagram result length: {len(instagram_output)} characters')
                print(f'First 300 chars: {instagram_output[:300]}...')
                
                # Summary
                print('\n' + '=' * 50)
                print('📋 TEST SUMMARY:')
                print(f'✅ Tools available: {len(tools_result.tools)}')
                print(f'✅ Connection test: {"PASS" if "successful" in test_result.content[0].text else "FAIL"}')
                print(f'✅ Campaign listing: {"PASS" if "Found" in campaigns_output else "FAIL"}')
                print(f'✅ Campaign search: {"PASS" if "Found" in search_output else "FAIL"}')
                print(f'✅ AI analysis: {"PASS" if len(analysis_output) > 500 else "FAIL"}')
                print(f'✅ Instagram campaigns: {"PASS" if len(instagram_output) > 100 else "FAIL"}')
                
                # Final verdict
                all_tests_passed = (
                    len(tools_result.tools) == 18 and
                    "successful" in test_result.content[0].text and
                    "Found" in campaigns_output and
                    "Found" in search_output and
                    len(analysis_output) > 500
                )
                
                print('\n🎯 FINAL VERDICT:')
                if all_tests_passed:
                    print('🎉 ALL TESTS PASSED - MCP TOOLS ARE WORKING CORRECTLY!')
                else:
                    print('❌ SOME TESTS FAILED - MCP TOOLS NEED FIXING')
                
    except Exception as e:
        print(f'❌ Comprehensive test failed: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_comprehensive_mcp()) 