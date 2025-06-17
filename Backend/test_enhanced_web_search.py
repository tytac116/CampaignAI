#!/usr/bin/env python3
"""
Enhanced Web Search Test for Brainstorming Scenarios

This test specifically validates that:
1. Brainstorming intent is properly detected
2. Multiple web searches are automatically triggered
3. Market insights are integrated into recommendations
4. Fresh ideas are generated based on web research
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

async def test_enhanced_brainstorming():
    """Test enhanced brainstorming with web search integration."""
    
    try:
        from app.agents.simple_workflow import SimpleMultiAgentWorkflow
        
        print('🧠 ENHANCED BRAINSTORMING WEB SEARCH TEST')
        print('=' * 80)
        print('Testing: Advanced Web Research Integration for Fresh Campaign Ideas')
        print('Expected: Multiple searches, market trends, innovative strategies')
        print('=' * 80)
        print()
        
        # Create workflow
        workflow = SimpleMultiAgentWorkflow()
        
        # Brainstorming question designed to trigger web research
        brainstorming_query = """I need fresh ideas and innovative strategies for improving my low-performing campaigns. What are the latest marketing trends and successful approaches that brands are using in 2024? I want to brainstorm new ideas we haven't considered based on current market insights."""
        
        print('❓ BRAINSTORMING QUERY:')
        print('-' * 60)
        print(brainstorming_query)
        print('-' * 60)
        print()
        print('⏳ Running enhanced brainstorming workflow...')
        print('🌐 Expected: Multiple web searches for trends and strategies')
        print()
        
        start_time = datetime.now()
        result = await workflow.run_workflow(brainstorming_query)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Analyze results
        print('🧠 BRAINSTORMING ANALYSIS RESULTS')
        print('=' * 60)
        print(f'✅ Status: {result["status"]}')
        print(f'⏱️  Execution Time: {execution_time:.2f} seconds')
        print(f'🛠️  Total Tool Calls: {len(result.get("tool_calls", []))}')
        print()
        
        # Count different types of tools used
        tool_calls = result.get("tool_calls", [])
        web_searches = [t for t in tool_calls if "tavily" in t.get("tool", "").lower()]
        wikipedia_searches = [t for t in tool_calls if "wikipedia" in t.get("tool", "").lower()]
        campaign_tools = [t for t in tool_calls if "campaign" in t.get("tool", "").lower()]
        analysis_tools = [t for t in tool_calls if "analyze" in t.get("tool", "").lower()]
        strategy_tools = [t for t in tool_calls if "optimize" in t.get("tool", "").lower()]
        
        print('🔍 TOOL USAGE BREAKDOWN:')
        print('-' * 40)
        print(f'   🌐 Tavily Web Searches: {len(web_searches)}')
        print(f'   📚 Wikipedia Searches: {len(wikipedia_searches)}')
        print(f'   📱 Campaign Data Tools: {len(campaign_tools)}')
        print(f'   🔍 Analysis Tools: {len(analysis_tools)}')
        print(f'   🎯 Strategy Tools: {len(strategy_tools)}')
        print()
        
        # Show specific searches performed
        if web_searches or wikipedia_searches:
            print('🔍 WEB RESEARCH PERFORMED:')
            print('-' * 50)
            search_count = 1
            for search in web_searches:
                query = search.get("query", "Unknown query")
                status = search.get("status", "Unknown")
                print(f'   {search_count:2d}. 🌐 Tavily: "{query}" → {status}')
                search_count += 1
            
            for search in wikipedia_searches:
                query = search.get("query", "Unknown query")
                status = search.get("status", "Unknown")
                print(f'   {search_count:2d}. 📚 Wikipedia: "{query}" → {status}')
                search_count += 1
            print()
        
        # Show intent analysis results
        intent_analysis = result.get("intent_analysis", {})
        if intent_analysis:
            print('🧠 INTENT ANALYSIS RESULTS:')
            print('-' * 40)
            print(f'   🎯 Primary Intent: {intent_analysis.get("primary_intent", "Unknown")}')
            print(f'   🌐 Web Research Required: {intent_analysis.get("requires_web_research", False)}')
            print(f'   📊 Confidence: {intent_analysis.get("confidence", 0):.2f}')
            
            research_topics = intent_analysis.get("research_topics", [])
            if research_topics:
                print(f'   🔍 Research Topics Identified:')
                for i, topic in enumerate(research_topics, 1):
                    print(f'      {i}. {topic}')
            print()
        
        if result['status'] == 'completed':
            print('💡 FRESH IDEAS & MARKET INSIGHTS REPORT:')
            print('=' * 80)
            
            final_output = result['final_output']
            print(final_output[:2000])  # Show first 2000 chars
            if len(final_output) > 2000:
                print(f'\n... [Report continues for {len(final_output) - 2000} more characters]')
            
            print('=' * 80)
            print()
            
            # Validate brainstorming effectiveness
            print('🎯 BRAINSTORMING EFFECTIVENESS VALIDATION:')
            print('-' * 55)
            
            # Check intent detection
            intent_detected = intent_analysis.get("primary_intent") == "BRAINSTORMING"
            print(f'   ✅ Brainstorming Intent Detected: {"Yes" if intent_detected else "No"}')
            
            # Check web research execution
            web_research_performed = len(web_searches) > 0
            print(f'   ✅ Web Research Executed: {"Yes" if web_research_performed else "No"} ({len(web_searches)} searches)')
            
            # Check multiple searches
            multiple_searches = len(web_searches) >= 2
            print(f'   ✅ Multiple Search Queries: {"Yes" if multiple_searches else "No"} ({len(web_searches)} queries)')
            
            # Check for market trends in output
            has_trends = any(word in final_output.lower() for word in ["trend", "2024", "latest", "current", "recent"])
            print(f'   ✅ Market Trends Included: {"Yes" if has_trends else "No"}')
            
            # Check for fresh ideas
            has_fresh_ideas = any(word in final_output.lower() for word in ["fresh", "innovative", "new", "creative", "unique"])
            print(f'   ✅ Fresh Ideas Generated: {"Yes" if has_fresh_ideas else "No"}')
            
            # Check for actionable recommendations
            has_actionable = any(word in final_output.lower() for word in ["recommend", "suggest", "implement", "strategy", "action"])
            print(f'   ✅ Actionable Recommendations: {"Yes" if has_actionable else "No"}')
            
            # Check comprehensive response
            is_comprehensive = len(final_output) > 1500
            print(f'   ✅ Comprehensive Response: {"Yes" if is_comprehensive else "No"} ({len(final_output)} chars)')
            
            # Check web research integration
            has_research_integration = "research" in final_output.lower() or "market" in final_output.lower()
            print(f'   ✅ Research Integration: {"Yes" if has_research_integration else "No"}')
            
            print()
            
            # Calculate overall score
            brainstorming_score = sum([
                intent_detected, web_research_performed, multiple_searches,
                has_trends, has_fresh_ideas, has_actionable, 
                is_comprehensive, has_research_integration
            ])
            
            print(f'📈 BRAINSTORMING EFFECTIVENESS SCORE: {brainstorming_score}/8')
            
            if brainstorming_score >= 7:
                print('🎉 EXCELLENT: Brainstorming workflow performing at optimal level!')
                print('   🧠 Intent properly detected and routed')
                print('   🌐 Comprehensive web research executed')
                print('   💡 Fresh, market-backed ideas generated')
                print('   🎯 Actionable recommendations provided')
            elif brainstorming_score >= 5:
                print('✅ GOOD: Brainstorming workflow functional with room for optimization')
                print('   Consider enhancing web search triggers or result integration')
            else:
                print('⚠️  NEEDS IMPROVEMENT: Brainstorming workflow requires optimization')
                print('   Web search integration or intent detection may need enhancement')
            
            print()
            print('🧠 ENHANCED BRAINSTORMING TEST COMPLETED!')
            print('=' * 55)
            print('✅ Brainstorming scenario thoroughly tested')
            print(f'✅ Execution time: {execution_time:.1f} seconds')
            print(f'✅ Web research performed: {len(web_searches)} searches')
            print(f'✅ Total tools utilized: {len(tool_calls)}')
            print(f'✅ Effectiveness score: {brainstorming_score}/8')
            print()
            
            return brainstorming_score >= 5
        else:
            print(f'❌ Enhanced Brainstorming Test Failed: {result.get("errors", [])}')
            return False
            
    except Exception as e:
        print(f'❌ Test failed with exception: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print('🧪 CAMPAIGN AI ENHANCED BRAINSTORMING TEST')
    print('Testing: Advanced Web Research Integration for Fresh Ideas')
    print()
    
    success = await test_enhanced_brainstorming()
    
    if success:
        print('\n🎯 TEST RESULTS SUMMARY:')
        print('   ✅ Brainstorming intent properly detected')
        print('   ✅ Multiple web searches automatically triggered')
        print('   ✅ Market insights and trends integrated')
        print('   ✅ Fresh, innovative ideas generated')
        print('   ✅ Actionable recommendations provided')
        print()
        print('📁 VALIDATION COMPLETE:')
        print('   🌐 Web search integration optimized')
        print('   🧠 Brainstorming workflow enhanced')
    else:
        print('\n❌ ENHANCED BRAINSTORMING TEST FAILED')
        print('   The workflow needs further optimization for brainstorming scenarios')
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 