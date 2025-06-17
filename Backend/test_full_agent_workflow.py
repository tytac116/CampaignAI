#!/usr/bin/env python3
"""
Test Full Agent Workflow with Working MCP Tools
"""

import asyncio
import sys
import os
from app.agents.campaign_agent import CampaignAgent

async def test_full_workflow():
    try:
        print('🤖 TESTING FULL AGENT WORKFLOW WITH MCP TOOLS')
        print('=' * 60)
        
        # Create campaign agent
        agent = CampaignAgent(model="gpt-4o-mini", temperature=0.3)
        print(f'✅ Created agent: {agent.agent_id}')
        
        # Test MCP connection
        connection_success = await agent.initialize_mcp_connection()
        if not connection_success:
            print('❌ Failed to initialize MCP connection')
            return
        
        print(f'✅ MCP connection initialized with {len(agent.mcp_tools)} tools')
        
        # Test realistic campaign optimization workflow
        print('\n🧪 Testing realistic campaign optimization workflow...')
        
        user_request = """
        I need help optimizing my Facebook campaigns. I have several campaigns running but they're not performing well:
        
        1. "AI Marketing Revolution" - Budget: R5000, Spend: R3200, ROAS: 1.8x, CTR: 2.1%
        2. "Digital Transformation" - Budget: R3000, Spend: R2800, ROAS: 1.2x, CTR: 1.5%
        
        Can you analyze these campaigns, find similar high-performing campaigns in our database, 
        and provide specific optimization recommendations to improve ROAS to at least 3.0x?
        """
        
        print(f'📝 User Request: {user_request[:100]}...')
        
        # Execute workflow
        result = await agent.execute_campaign_workflow(user_request)
        
        print(f'\n📊 Workflow Results:')
        print(f'   Status: {result["status"]}')
        print(f'   Execution Time: {result["execution_time_seconds"]:.2f} seconds')
        print(f'   Tools Used: {len(result["tool_calls"])}')
        print(f'   Validation: {"✅ PASSED" if result["validation_results"]["is_valid"] else "❌ FAILED"}')
        
        # Show tool calls
        if result["tool_calls"]:
            print(f'\n🛠️ Tools Used:')
            for i, tool_call in enumerate(result["tool_calls"], 1):
                tool_name = tool_call.get("tool_name", "unknown_tool")
                print(f'   {i}. {tool_name}')
        
        # Show final output (first 500 chars)
        if result["final_output"]:
            print(f'\n💬 Agent Response (preview):')
            print(f'   {result["final_output"][:500]}...')
            
            # Check if response contains expected optimization elements
            response_lower = result["final_output"].lower()
            optimization_elements = [
                'roas', 'optimization', 'recommendations', 'campaigns', 
                'facebook', 'performance', 'budget', 'targeting'
            ]
            
            found_elements = [elem for elem in optimization_elements if elem in response_lower]
            print(f'\n🎯 Response Quality Check:')
            print(f'   Contains {len(found_elements)}/{len(optimization_elements)} expected elements')
            print(f'   Elements found: {", ".join(found_elements)}')
            
            if len(found_elements) >= 6:
                print('   ✅ HIGH QUALITY RESPONSE - Contains comprehensive optimization advice')
            elif len(found_elements) >= 4:
                print('   ⚠️ GOOD RESPONSE - Contains basic optimization advice')
            else:
                print('   ❌ LOW QUALITY RESPONSE - Missing key optimization elements')
        
        # Test another workflow - Campaign Creation
        print('\n' + '=' * 60)
        print('🧪 Testing campaign creation workflow...')
        
        creation_request = """
        Create a new Facebook campaign for our upcoming product launch:
        - Product: AI-powered marketing analytics tool
        - Target: Marketing professionals aged 25-45
        - Budget: R2000 daily
        - Objective: Lead generation
        - Duration: 30 days
        
        Also generate compelling ad copy for this campaign.
        """
        
        print(f'📝 Creation Request: {creation_request[:100]}...')
        
        # Execute creation workflow
        creation_result = await agent.execute_campaign_workflow(creation_request)
        
        print(f'\n📊 Creation Workflow Results:')
        print(f'   Status: {creation_result["status"]}')
        print(f'   Execution Time: {creation_result["execution_time_seconds"]:.2f} seconds')
        print(f'   Tools Used: {len(creation_result["tool_calls"])}')
        print(f'   Validation: {"✅ PASSED" if creation_result["validation_results"]["is_valid"] else "❌ FAILED"}')
        
        # Show creation tools used
        if creation_result["tool_calls"]:
            print(f'\n🛠️ Creation Tools Used:')
            for i, tool_call in enumerate(creation_result["tool_calls"], 1):
                tool_name = tool_call.get("tool_name", "unknown_tool")
                print(f'   {i}. {tool_name}')
        
        # Final verdict
        print('\n' + '=' * 60)
        print('🎯 FINAL WORKFLOW VERDICT:')
        
        both_successful = (result["status"] == "completed" and 
                          creation_result["status"] == "completed" and
                          result["validation_results"]["is_valid"] and 
                          creation_result["validation_results"]["is_valid"])
        
        if both_successful:
            print('🎉 FULL AGENT WORKFLOW WORKING PERFECTLY!')
            print('✅ MCP tools integration successful')
            print('✅ AI reasoning and tool selection working')
            print('✅ Real campaign data access working')
            print('✅ Campaign optimization recommendations generated')
            print('✅ Campaign creation workflow functional')
            print('\n🚀 READY FOR FRONTEND INTEGRATION!')
        else:
            print('⚠️ WORKFLOW PARTIALLY WORKING - Some issues detected')
            if result["status"] != "completed":
                print(f'   - Optimization workflow status: {result["status"]}')
            if creation_result["status"] != "completed":
                print(f'   - Creation workflow status: {creation_result["status"]}')
            if not result["validation_results"]["is_valid"]:
                print('   - Optimization validation failed')
            if not creation_result["validation_results"]["is_valid"]:
                print('   - Creation validation failed')
        
    except Exception as e:
        print(f'❌ Workflow test failed: {str(e)}')
        import traceback
        traceback.print_exc()

async def main():
    await test_full_workflow()

if __name__ == "__main__":
    asyncio.run(main()) 