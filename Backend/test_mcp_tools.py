#!/usr/bin/env python3
"""
Test MCP Campaign Tools
"""

import asyncio
import sys
import os
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

async def test_campaign_tools():
    try:
        print('🔗 Testing MCP campaign tools...')
        
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
                
                # Test 1: List campaigns by criteria
                print('\n🧪 Test 1: List campaigns by criteria')
                result1 = await session.call_tool('mcp_list_campaigns_by_criteria', {
                    'platform': 'facebook',
                    'limit': 3
                })
                print(f'✅ Result: {result1.content[0].text[:200]}...')
                
                # Test 2: Search campaign data
                print('\n🧪 Test 2: Search campaign data')
                result2 = await session.call_tool('mcp_search_campaign_data', {
                    'query': 'hospitality',
                    'limit': 2
                })
                print(f'✅ Result: {result2.content[0].text[:200]}...')
                
                # Test 3: Analyze campaign performance
                print('\n🧪 Test 3: Analyze campaign performance')
                result3 = await session.call_tool('mcp_analyze_campaign_performance', {
                    'campaign_data': 'Campaign: AI in Hospitality, Budget: R6000, Spend: R2800, ROAS: 2.1x, CTR: 3.2%'
                })
                print(f'✅ Result: {result3.content[0].text[:200]}...')
                
                print('\n🎉 All MCP tools working successfully!')
                
    except Exception as e:
        print(f'❌ MCP tools test failed: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_campaign_tools()) 