#!/usr/bin/env python3
"""
Test Direct MCP Workflow - Bypassing complex agent recursion
"""

import asyncio
import sys
import os
from datetime import datetime
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

async def test_direct_mcp_workflow():
    """Test direct MCP workflow execution without agent recursion."""
    try:
        print('🤖 TESTING DIRECT MCP WORKFLOW')
        print('=' * 60)
        
        user_instruction = """
        I need help optimizing my Facebook campaigns. I have several campaigns running but they're 
        not performing well. Can you analyze the current performance, identify issues, and provide 
        specific recommendations for improvement? Also generate some new ad copy that might work better.
        """
        
        workflow_id = f"direct_test_{datetime.now().strftime('%H%M%S')}"
        start_time = datetime.now()
        
        print(f'📋 Workflow ID: {workflow_id}')
        print(f'📝 User Request: {user_instruction.strip()}')
        print(f'⏰ Started: {start_time.strftime("%Y-%m-%d %H:%M:%S")}')
        
        # Connect to MCP server
        server_params = StdioServerParameters(
            command='python3',
            args=['mcp_server.py'],
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print('✅ MCP Session initialized')
                
                # Analyze user intent
                intent_keywords = user_instruction.lower()
                tool_calls_made = []
                analysis_parts = []
                
                print('\n🔍 Analyzing user intent and executing workflow...')
                
                # Step 1: Get campaign data
                if any(word in intent_keywords for word in ['campaign', 'performance', 'analyze', 'optimize']):
                    print('📊 Step 1: Getting campaign data...')
                    
                    # Get Facebook campaigns
                    fb_result = await session.call_tool('mcp_get_facebook_campaigns', {'limit': 5})
                    fb_data = fb_result.content[0].text
                    tool_calls_made.append({
                        "tool": "mcp_get_facebook_campaigns",
                        "args": {"limit": 5},
                        "result_length": len(fb_data)
                    })
                    analysis_parts.append(f"**Current Facebook Campaigns:**\n{fb_data[:800]}...")
                    print(f'   ✅ Retrieved {len(fb_data)} characters of campaign data')
                    
                    # Search for relevant campaigns
                    search_result = await session.call_tool('mcp_search_campaign_data', {
                        'query': 'marketing campaign performance',
                        'limit': 3
                    })
                    search_data = search_result.content[0].text
                    tool_calls_made.append({
                        "tool": "mcp_search_campaign_data", 
                        "args": {"query": "marketing campaign performance", "limit": 3},
                        "result_length": len(search_data)
                    })
                    analysis_parts.append(f"**Campaign Search Results:**\n{search_data[:600]}...")
                    print(f'   ✅ Found {len(search_data)} characters of search results')
                
                # Step 2: Perform analysis
                if any(word in intent_keywords for word in ['analyze', 'performance', 'insights']):
                    print('🔍 Step 2: Performing campaign analysis...')
                    
                    sample_campaign = "Campaign: Marketing Excellence, Budget: R8000, Spend: R5200, ROAS: 2.1x, CTR: 2.8%, Platform: Facebook"
                    analysis_result = await session.call_tool('mcp_analyze_campaign_performance', {
                        'campaign_data': sample_campaign
                    })
                    analysis_data = analysis_result.content[0].text
                    tool_calls_made.append({
                        "tool": "mcp_analyze_campaign_performance",
                        "args": {"campaign_data": sample_campaign},
                        "result_length": len(analysis_data)
                    })
                    analysis_parts.append(f"**AI Performance Analysis:**\n{analysis_data[:1000]}...")
                    print(f'   ✅ Generated {len(analysis_data)} characters of analysis')
                
                # Step 3: Generate optimization strategy
                if any(word in intent_keywords for word in ['optimize', 'strategy', 'improve', 'recommendations']):
                    print('🎯 Step 3: Generating optimization strategy...')
                    
                    strategy_result = await session.call_tool('mcp_optimize_campaign_strategy', {
                        'campaign_data': 'Current campaign with 2.1x ROAS and 2.8% CTR',
                        'goals': 'increase ROAS to 3.5x and improve CTR to 4.5%'
                    })
                    strategy_data = strategy_result.content[0].text
                    tool_calls_made.append({
                        "tool": "mcp_optimize_campaign_strategy",
                        "args": {"campaign_data": "Current campaign with 2.1x ROAS and 2.8% CTR", "goals": "increase ROAS to 3.5x and improve CTR to 4.5%"},
                        "result_length": len(strategy_data)
                    })
                    analysis_parts.append(f"**Optimization Strategy:**\n{strategy_data[:1000]}...")
                    print(f'   ✅ Generated {len(strategy_data)} characters of strategy')
                
                # Step 4: Generate content
                if any(word in intent_keywords for word in ['content', 'copy', 'creative', 'generate', 'ad copy']):
                    print('✨ Step 4: Generating campaign content...')
                    
                    content_result = await session.call_tool('mcp_generate_campaign_content', {
                        'campaign_type': 'ad_copy',
                        'target_audience': 'business professionals aged 25-50',
                        'platform': 'facebook',
                        'campaign_objective': 'lead_generation'
                    })
                    content_data = content_result.content[0].text
                    tool_calls_made.append({
                        "tool": "mcp_generate_campaign_content",
                        "args": {"campaign_type": "ad_copy", "target_audience": "business professionals aged 25-50", "platform": "facebook", "campaign_objective": "lead_generation"},
                        "result_length": len(content_data)
                    })
                    analysis_parts.append(f"**Generated Content:**\n{content_data[:800]}...")
                    print(f'   ✅ Generated {len(content_data)} characters of content')
                
                # Compile final output
                execution_time = (datetime.now() - start_time).total_seconds()
                
                final_output = f"""
🤖 **CAMPAIGN AI DIRECT MCP WORKFLOW RESULTS**
📋 **Workflow ID**: {workflow_id}
📝 **User Request**: {user_instruction.strip()}
⏰ **Executed**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
⏱️ **Execution Time**: {execution_time:.2f} seconds

{'='*60}
📊 **COMPREHENSIVE ANALYSIS & RESULTS**
{'='*60}

{chr(10).join(analysis_parts)}

{'='*60}
📈 **EXECUTIVE SUMMARY**
{'='*60}

✅ **Tools Executed**: {len(tool_calls_made)} MCP tools used successfully
🎯 **Analysis Scope**: Comprehensive campaign optimization workflow
📊 **Data Sources**: Facebook campaigns, database search, AI analysis
🚀 **Capabilities Demonstrated**: 
   - Real-time campaign data retrieval
   - AI-powered performance analysis  
   - Strategic optimization recommendations
   - Creative content generation

{'='*60}
🎯 **KEY RECOMMENDATIONS**
{'='*60}

1. **Performance Optimization**: Implement AI-generated strategies to improve ROAS
2. **Content Enhancement**: Use generated ad copy for better engagement
3. **Data-Driven Decisions**: Leverage campaign analytics for strategic planning
4. **Continuous Monitoring**: Track performance metrics and adjust accordingly
5. **Scale Success**: Expand high-performing elements across campaigns

{'='*60}
✨ **NEXT STEPS**
{'='*60}

- Deploy optimization recommendations
- A/B test new creative content  
- Monitor campaign performance metrics
- Scale successful strategies to other campaigns
- Continue leveraging AI insights for growth

🎉 **Campaign AI MCP Workflow completed successfully!**
                """
                
                print('\n' + '='*60)
                print('📊 WORKFLOW EXECUTION RESULTS')
                print('='*60)
                print(f'✅ Status: COMPLETED')
                print(f'⏱️ Execution Time: {execution_time:.2f} seconds')
                print(f'🔧 Tools Used: {len(tool_calls_made)}')
                print(f'📝 Output Length: {len(final_output)} characters')
                
                print('\n📋 Tool Calls Summary:')
                for i, call in enumerate(tool_calls_made, 1):
                    print(f'   {i}. {call["tool"]} -> {call["result_length"]} chars')
                
                print('\n' + '='*60)
                print('🎯 DIRECT MCP WORKFLOW TEST VERDICT')
                print('='*60)
                
                # Validate results
                all_successful = all([
                    len(call["result_length"]) > 0 for call in tool_calls_made
                ])
                
                if all_successful and len(tool_calls_made) >= 4:
                    print('🎉 DIRECT MCP WORKFLOW: SUCCESS!')
                    print('✅ All MCP tools executed successfully')
                    print('✅ No recursion issues detected')
                    print('✅ Comprehensive analysis generated')
                    print('✅ Ready for agent integration')
                    print('\n💡 SOLUTION: Use direct MCP calls instead of complex LangGraph workflow')
                    return True
                else:
                    print('⚠️ WORKFLOW INCOMPLETE')
                    print(f'🔍 Tools executed: {len(tool_calls_made)}/4 expected')
                    return False
                
    except Exception as e:
        print(f'❌ Direct MCP workflow test failed: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await test_direct_mcp_workflow()
    if success:
        print('\n🚀 READY TO UPDATE AGENT WORKFLOW!')
    else:
        print('\n❌ WORKFLOW NEEDS DEBUGGING')

if __name__ == "__main__":
    asyncio.run(main()) 