#!/usr/bin/env python3
"""
Direct MCP Connection Test
"""

import asyncio
import sys
import os
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

async def test_mcp_connection():
    try:
        print('🔗 Testing MCP connection...')
        
        # Create server parameters
        server_params = StdioServerParameters(
            command='python3',
            args=['mcp_server.py'],
        )
        
        print(f'📍 Server path: {os.path.abspath("mcp_server.py")}')
        print(f'🚀 Starting server with: python3 mcp_server.py')
        
        # Connect to MCP server
        async with stdio_client(server_params) as (read, write):
            print('✅ stdio_client connected')
            async with ClientSession(read, write) as session:
                print('✅ ClientSession created')
                await session.initialize()
                print('✅ Session initialized')
                
                # List tools
                tools_result = await session.list_tools()
                print(f'✅ Found {len(tools_result.tools)} tools:')
                for tool in tools_result.tools:
                    print(f'   🛠️ {tool.name}: {tool.description[:50]}...')
                
                # Test a simple tool
                test_result = await session.call_tool('test_connection', {})
                print(f'✅ Test tool result: {test_result.content}')
                
    except Exception as e:
        print(f'❌ MCP connection failed: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_connection()) 