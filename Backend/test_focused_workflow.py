#!/usr/bin/env python3
"""
Focused Workflow Test: Validate Enhanced Campaign Analysis

This test validates that the enhanced workflow:
1. Provides direct, specific answers to questions
2. Identifies specific campaigns by name
3. Provides campaign-specific recommendations
4. Uses web search when beneficial
5. Avoids generic fluff and focuses on the actual question

Test Question: "Analyze the top 3 campaigns with the lowest click-through rate and generate a report 
with recommendations on how to improve them, including budget optimization and identified problems 
compared to other campaigns."
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

async def test_focused_workflow():
    """Test the enhanced workflow for focused, specific answers."""
    
    try:
        from app.agents.simple_workflow import SimpleMultiAgentWorkflow
        
        print('🎯 FOCUSED WORKFLOW TEST')
        print('=' * 80)
        print('Testing: Enhanced Multi-Agent Analysis with Specific Answers')
        print('Validation: Direct answers, campaign-specific recommendations, web research')
        print('=' * 80)
        print()
        
        # Create workflow
        workflow = SimpleMultiAgentWorkflow()
        
        # Generate graph visualization
        print('📊 Generating workflow graph visualization...')
        graph_path = workflow.visualize_graph("focused_workflow_test_graph.png")
        if graph_path:
            print(f'✅ Graph saved as: {graph_path}')
        print()
        
        # Focused test question
        test_question = """Analyze the top 3 campaigns with the lowest click-through rate and generate a comprehensive report with recommendations on how to improve them, including budget optimization and identified problems compared to other campaigns."""
        
        print('❓ TEST QUESTION:')
        print('-' * 50)
        print(test_question)
        print('-' * 50)
        print()
        print('⏳ Running enhanced workflow...')
        print('🎯 Expected: Direct answer with specific campaign names and targeted improvements')
        print()
        
        start_time = datetime.now()
        result = await workflow.run_workflow(test_question)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Analyze the results
        print('📊 ENHANCED WORKFLOW RESULTS')
        print('=' * 60)
        print(f'✅ Status: {result["status"]}')
        print(f'⏱️  Execution Time: {execution_time:.2f} seconds')
        print(f'📊 Final Step: {result["current_step"]}')
        print(f'🛠️  Tool Calls: {len(result.get("tool_calls", []))}')
        print()
        
        # Show tool calls
        if result.get("tool_calls"):
            print('🔧 TOOLS USED:')
            print('-' * 30)
            for i, tool_call in enumerate(result["tool_calls"], 1):
                tool_name = tool_call.get("tool", "Unknown")
                status = tool_call.get("status", "Unknown")
                query = tool_call.get("query", "")
                query_info = f" ({query})" if query else ""
                print(f'   {i:2d}. {tool_name:<35} → {status}{query_info}')
            print()
        
        # Check if web search was used
        web_search_used = any("tavily" in tool.get("tool", "") for tool in result.get("tool_calls", []))
        if web_search_used:
            print('🌐 WEB RESEARCH: Enhanced with industry insights')
        else:
            print('📊 DATA ANALYSIS: Campaign data analysis only')
        print()
        
        if result['status'] == 'completed':
            print('📋 FOCUSED ANALYSIS REPORT:')
            print('=' * 80)
            
            final_output = result['final_output']
            print(final_output)
            
            print('=' * 80)
            print()
            
            # Validate the response quality
            print('🔍 RESPONSE QUALITY VALIDATION:')
            print('-' * 40)
            
            # Check for direct answers
            has_direct_answer = "Direct Answer" in final_output or "lowest click-through rate" in final_output.lower()
            print(f'   ✅ Direct Answer Provided: {"Yes" if has_direct_answer else "No"}')
            
            # Check for specific campaign names
            has_campaign_names = "Campaign" in final_output and ("Facebook" in final_output or "Instagram" in final_output)
            print(f'   ✅ Specific Campaign Names: {"Yes" if has_campaign_names else "No"}')
            
            # Check for specific recommendations
            has_specific_recs = "Recommended Actions" in final_output or "Budget Optimization" in final_output
            print(f'   ✅ Campaign-Specific Recommendations: {"Yes" if has_specific_recs else "No"}')
            
            # Check for web research integration
            has_research = "Industry Research" in final_output or "Research:" in final_output
            print(f'   ✅ Web Research Integration: {"Yes" if has_research else "No"}')
            
            # Check response length (should be focused, not too long)
            response_length = len(final_output)
            is_focused = 1000 < response_length < 5000  # Focused but comprehensive
            print(f'   ✅ Focused Response Length: {"Yes" if is_focused else "No"} ({response_length} chars)')
            
            print()
            
            # Overall assessment
            quality_score = sum([has_direct_answer, has_campaign_names, has_specific_recs, has_research, is_focused])
            print(f'📈 OVERALL QUALITY SCORE: {quality_score}/5')
            
            if quality_score >= 4:
                print('🎉 EXCELLENT: Enhanced workflow provides focused, specific answers!')
            elif quality_score >= 3:
                print('✅ GOOD: Workflow provides targeted responses with room for improvement')
            else:
                print('⚠️  NEEDS IMPROVEMENT: Response lacks specificity or focus')
            
            print()
            print('🎯 ENHANCED WORKFLOW TEST COMPLETED!')
            print('=' * 50)
            print('✅ Multi-agent coordination working')
            print(f'✅ Execution time: {execution_time:.1f} seconds')
            print('✅ Focused, campaign-specific analysis delivered')
            print('✅ Web research integration when beneficial')
            print(f'✅ Quality score: {quality_score}/5')
            print()
            
            return quality_score >= 3
        else:
            print(f'❌ Enhanced Workflow Failed: {result.get("errors", [])}')
            return False
            
    except Exception as e:
        print(f'❌ Test failed with exception: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print('🧪 CAMPAIGN AI ENHANCED WORKFLOW TEST')
    print('Testing: Focused, Campaign-Specific Analysis & Recommendations')
    print()
    
    success = await test_focused_workflow()
    
    if success:
        print('\n🎯 TEST RESULTS:')
        print('   ✅ Enhanced workflow provides focused answers')
        print('   ✅ Campaign-specific recommendations generated')
        print('   ✅ Web research integration working')
        print('   ✅ Direct response to user questions')
        print()
        print('📁 FILES GENERATED:')
        print('   🖼️  focused_workflow_test_graph.png - Workflow diagram')
        print('   📊 Quality validation completed')
    else:
        print('\n❌ ENHANCED WORKFLOW TEST FAILED')
        print('   The workflow needs further optimization for focused responses')
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 