#!/usr/bin/env python3
"""
Test Full Agent Workflow with MCP Tools
"""

import asyncio
import sys
import os
from app.agents.campaign_agent import CampaignAgent

async def test_agent_workflow():
    try:
        print('🤖 Testing full agent workflow with MCP tools...')
        
        # Create campaign agent
        agent = CampaignAgent(model="gpt-4o-mini", temperature=0.3)
        print(f'✅ Created agent: {agent.agent_id}')
        
        # Test MCP connection
        connection_success = await agent.initialize_mcp_connection()
        if not connection_success:
            print('❌ Failed to initialize MCP connection')
            return
        
        print(f'✅ MCP connection initialized with {len(agent.mcp_tools)} tools')
        
        # Test workflow execution
        print('\n🧪 Testing workflow: "Show me the best performing campaigns"')
        result = await agent.execute_campaign_workflow(
            user_instruction="Show me the best performing campaigns with highest ROAS",
            campaign_context={"focus": "performance_analysis"}
        )
        
        print(f'\n📊 Workflow Results:')
        print(f'   Status: {result["status"]}')
        print(f'   Tool calls made: {len(result["tool_calls"])}')
        print(f'   Execution time: {result.get("execution_time_seconds", 0):.2f}s')
        print(f'   Validation passed: {result["validation_results"].get("is_valid", False)}')
        
        # Show tool calls
        if result["tool_calls"]:
            print(f'\n🛠️ Tools used:')
            for i, tool_call in enumerate(result["tool_calls"], 1):
                tool_name = tool_call.get("name", tool_call.get("tool", "unknown_tool"))
                print(f'   {i}. {tool_name}')
        
        # Show final output (first 300 chars)
        if result["final_output"]:
            print(f'\n💬 Agent Response (preview):')
            print(f'   {result["final_output"][:300]}...')
        
        print('\n🎉 Full agent workflow test completed successfully!')
        
    except Exception as e:
        print(f'❌ Agent workflow test failed: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent_workflow()) 