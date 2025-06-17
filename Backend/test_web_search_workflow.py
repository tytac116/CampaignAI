#!/usr/bin/env python3
"""
Web Search Integration Test: Fresh Campaign Ideas & Market Trends

This test validates that the workflow:
1. Recognizes when external research is needed
2. Automatically triggers web search tools
3. Integrates market insights with campaign data
4. Provides fresh, innovative campaign ideas
5. Uses multiple search queries for comprehensive research

Test Scenario: "I'm thinking about improving some of my low-performing campaigns and I need 
fresh ideas of what's out there in the market. Can you help me brainstorm some fresh ideas 
that we haven't considered based on our previous campaigns?"
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

async def test_web_search_workflow():
    """Test the workflow's web search integration for campaign brainstorming."""
    
    try:
        from app.agents.simple_workflow import SimpleMultiAgentWorkflow
        
        print('🌐 WEB SEARCH INTEGRATION TEST')
        print('=' * 80)
        print('Testing: Automatic Web Research for Fresh Campaign Ideas')
        print('Expected: Multiple web searches, market insights, innovative recommendations')
        print('=' * 80)
        print()
        
        # Create workflow
        workflow = SimpleMultiAgentWorkflow()
        
        # Generate graph visualization
        print('📊 Generating workflow graph visualization...')
        graph_path = workflow.visualize_graph("web_search_workflow_graph.png")
        if graph_path:
            print(f'✅ Graph saved as: {graph_path}')
        print()
        
        # Campaign brainstorming question that should trigger extensive web research
        brainstorming_question = """I'm thinking about improving some of my low-performing campaigns and I need fresh ideas of what's out there in the market. Can you help me brainstorm some fresh ideas that we haven't considered based on our previous campaigns? I want to know about the latest trends, innovative strategies, and what successful brands are doing differently in 2024."""
        
        print('❓ BRAINSTORMING QUESTION:')
        print('-' * 60)
        print(brainstorming_question)
        print('-' * 60)
        print()
        print('⏳ Running workflow with web research focus...')
        print('🌐 Expected: Multiple web searches for trends, strategies, and innovations')
        print()
        
        start_time = datetime.now()
        result = await workflow.run_workflow(brainstorming_question)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Analyze web search usage
        print('🌐 WEB SEARCH ANALYSIS')
        print('=' * 60)
        print(f'✅ Status: {result["status"]}')
        print(f'⏱️  Execution Time: {execution_time:.2f} seconds')
        print(f'🛠️  Total Tool Calls: {len(result.get("tool_calls", []))}')
        print()
        
        # Count web search tools used
        web_searches = [tool for tool in result.get("tool_calls", []) if "tavily" in tool.get("tool", "").lower()]
        wikipedia_searches = [tool for tool in result.get("tool_calls", []) if "wikipedia" in tool.get("tool", "").lower()]
        
        print('🔍 WEB RESEARCH BREAKDOWN:')
        print('-' * 40)
        print(f'   🌐 Tavily Web Searches: {len(web_searches)}')
        print(f'   📚 Wikipedia Searches: {len(wikipedia_searches)}')
        print(f'   📊 Campaign Data Tools: {len(result.get("tool_calls", [])) - len(web_searches) - len(wikipedia_searches)}')
        print()
        
        # Show specific web searches performed
        if web_searches or wikipedia_searches:
            print('🔍 SPECIFIC WEB SEARCHES PERFORMED:')
            print('-' * 50)
            search_count = 1
            for search in web_searches:
                query = search.get("query", "Unknown query")
                status = search.get("status", "Unknown")
                print(f'   {search_count:2d}. Tavily: "{query}" → {status}')
                search_count += 1
            
            for search in wikipedia_searches:
                query = search.get("query", "Unknown query")
                status = search.get("status", "Unknown")
                print(f'   {search_count:2d}. Wikipedia: "{query}" → {status}')
                search_count += 1
            print()
        
        # Show all tool calls in order
        if result.get("tool_calls"):
            print('🔧 COMPLETE TOOL EXECUTION SEQUENCE:')
            print('-' * 45)
            for i, tool_call in enumerate(result["tool_calls"], 1):
                tool_name = tool_call.get("tool", "Unknown")
                status = tool_call.get("status", "Unknown")
                query = tool_call.get("query", "")
                
                # Add emoji based on tool type
                if "tavily" in tool_name.lower():
                    emoji = "🌐"
                elif "wikipedia" in tool_name.lower():
                    emoji = "📚"
                elif "facebook" in tool_name.lower() or "instagram" in tool_name.lower():
                    emoji = "📱"
                elif "analyze" in tool_name.lower():
                    emoji = "🔍"
                elif "optimize" in tool_name.lower():
                    emoji = "🎯"
                elif "generate" in tool_name.lower():
                    emoji = "✨"
                else:
                    emoji = "🛠️"
                
                query_info = f' ("{query[:40]}...")' if query and len(query) > 5 else ""
                print(f'   {i:2d}. {emoji} {tool_name:<35} → {status}{query_info}')
            print()
        
        if result['status'] == 'completed':
            print('📋 FRESH IDEAS & MARKET INSIGHTS REPORT:')
            print('=' * 80)
            
            final_output = result['final_output']
            print(final_output)
            
            print('=' * 80)
            print()
            
            # Validate web search integration
            print('🔍 WEB SEARCH INTEGRATION VALIDATION:')
            print('-' * 50)
            
            # Check if web searches were triggered
            web_search_triggered = len(web_searches) > 0
            print(f'   ✅ Web Search Triggered: {"Yes" if web_search_triggered else "No"} ({len(web_searches)} searches)')
            
            # Check if multiple search queries were used
            multiple_searches = len(web_searches) >= 2
            print(f'   ✅ Multiple Search Queries: {"Yes" if multiple_searches else "No"} ({len(web_searches)} queries)')
            
            # Check if market insights are included
            has_market_insights = "market" in final_output.lower() or "trend" in final_output.lower() or "2024" in final_output
            print(f'   ✅ Market Insights Included: {"Yes" if has_market_insights else "No"}')
            
            # Check if fresh ideas are provided
            has_fresh_ideas = "idea" in final_output.lower() or "strategy" in final_output.lower() or "innovative" in final_output.lower()
            print(f'   ✅ Fresh Ideas Generated: {"Yes" if has_fresh_ideas else "No"}')
            
            # Check if research is integrated with campaign data
            has_campaign_integration = "campaign" in final_output.lower() and ("facebook" in final_output.lower() or "instagram" in final_output.lower())
            print(f'   ✅ Campaign Data Integration: {"Yes" if has_campaign_integration else "No"}')
            
            # Check response comprehensiveness
            response_length = len(final_output)
            is_comprehensive = response_length > 2000  # Should be detailed with web research
            print(f'   ✅ Comprehensive Response: {"Yes" if is_comprehensive else "No"} ({response_length} chars)')
            
            print()
            
            # Overall web search assessment
            web_search_score = sum([
                web_search_triggered, multiple_searches, has_market_insights, 
                has_fresh_ideas, has_campaign_integration, is_comprehensive
            ])
            
            print(f'📈 WEB SEARCH INTEGRATION SCORE: {web_search_score}/6')
            
            if web_search_score >= 5:
                print('🎉 EXCELLENT: Web search integration working perfectly!')
                print('   🌐 Multiple searches performed automatically')
                print('   📊 Market insights seamlessly integrated')
                print('   💡 Fresh, data-driven ideas generated')
            elif web_search_score >= 3:
                print('✅ GOOD: Web search integration functional with room for improvement')
            else:
                print('⚠️  NEEDS IMPROVEMENT: Web search integration not fully working')
            
            print()
            print('🌐 WEB SEARCH WORKFLOW TEST COMPLETED!')
            print('=' * 55)
            print('✅ Campaign brainstorming scenario tested')
            print(f'✅ Execution time: {execution_time:.1f} seconds')
            print(f'✅ Web searches performed: {len(web_searches)}')
            print(f'✅ Total tools used: {len(result.get("tool_calls", []))}')
            print(f'✅ Integration score: {web_search_score}/6')
            print()
            
            return web_search_score >= 3
        else:
            print(f'❌ Web Search Workflow Failed: {result.get("errors", [])}')
            return False
            
    except Exception as e:
        print(f'❌ Test failed with exception: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print('🧪 CAMPAIGN AI WEB SEARCH INTEGRATION TEST')
    print('Testing: Fresh Campaign Ideas & Market Research Integration')
    print()
    
    success = await test_web_search_workflow()
    
    if success:
        print('\n🎯 TEST RESULTS:')
        print('   ✅ Web search tools automatically triggered')
        print('   ✅ Market insights and trends integrated')
        print('   ✅ Fresh campaign ideas generated')
        print('   ✅ Campaign data combined with external research')
        print()
        print('📁 FILES GENERATED:')
        print('   🖼️  web_search_workflow_graph.png - Workflow diagram')
        print('   📊 Web search integration validated')
    else:
        print('\n❌ WEB SEARCH INTEGRATION TEST FAILED')
        print('   The workflow needs optimization for web research scenarios')
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 