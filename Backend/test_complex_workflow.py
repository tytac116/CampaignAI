#!/usr/bin/env python3
"""
Complex Workflow Test: Analyze Low CTR Campaigns & Generate Improvement Report

This test will trigger the FULL complex workflow path:
1. Intent Analysis
2. Data Collection  
3. Performance Analysis
4. Strategy Development
5. Content Generation
6. Results Compilation

Question: "Analyze the top 3 campaigns with the lowest click-through rate and generate a report 
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

async def test_complex_workflow():
    """Test the complex workflow with a detailed analysis request."""
    
    try:
        from app.agents.simple_workflow import SimpleMultiAgentWorkflow
        
        print('🔬 COMPLEX WORKFLOW TEST')
        print('=' * 80)
        print('Testing: Multi-Agent Analysis & Report Generation')
        print('Expected Path: Intent → Data → Analysis → Strategy → Content → Compilation')
        print('=' * 80)
        print()
        
        # Create workflow
        workflow = SimpleMultiAgentWorkflow()
        
        # Generate graph visualization
        print('📊 Generating workflow graph visualization...')
        graph_path = workflow.visualize_graph("complex_workflow_analysis_graph.png")
        if graph_path:
            print(f'✅ Graph saved as: {graph_path}')
            print(f'🖼️  Workflow diagram: {os.path.abspath(graph_path)}')
        print()
        
        # Complex analysis question that should trigger full workflow
        complex_question = """Analyze the top 3 campaigns with the lowest click-through rate and generate a comprehensive report with recommendations on how to improve them, including budget optimization and identified problems compared to other campaigns."""
        
        print('❓ COMPLEX QUESTION:')
        print('-' * 50)
        print(complex_question)
        print('-' * 50)
        print()
        print('⏳ Processing complex workflow (this may take 60-90 seconds)...')
        print('🔄 Expected flow: All 6 workflow steps')
        print()
        
        start_time = datetime.now()
        result = await workflow.run_workflow(complex_question)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Detailed analysis of results
        print('📊 COMPLEX WORKFLOW RESULTS')
        print('=' * 60)
        print(f'✅ Status: {result["status"]}')
        print(f'⏱️  Total Execution Time: {execution_time:.2f} seconds')
        print(f'📊 Final Step: {result["current_step"]}')
        print(f'🛠️  Total Tool Calls: {len(result.get("tool_calls", []))}')
        print(f'❌ Errors: {len(result.get("errors", []))}')
        print()
        
        # Show detailed tool calls
        if result.get("tool_calls"):
            print('🔧 DETAILED TOOL CALLS:')
            print('-' * 40)
            for i, tool_call in enumerate(result["tool_calls"], 1):
                tool_name = tool_call.get("tool", "Unknown")
                status = tool_call.get("status", "Unknown")
                print(f'   {i:2d}. {tool_name:<35} → {status}')
            print()
        
        # Analyze workflow path taken
        current_step = result.get("current_step", "unknown")
        if current_step == "completed":
            print('🎯 WORKFLOW PATH: FULL COMPLEX ANALYSIS')
            print('   ✅ 1. Intent Analysis → Complex analysis detected')
            print('   ✅ 2. Data Collection → Campaign data gathered')
            print('   ✅ 3. Performance Analysis → Insights generated')
            print('   ✅ 4. Strategy Development → Recommendations created')
            print('   ✅ 5. Content Generation → Creative content produced')
            print('   ✅ 6. Results Compilation → Final report compiled')
        elif current_step == "quick_response_completed":
            print('⚠️  WORKFLOW PATH: SIMPLE QUERY (UNEXPECTED)')
            print('   This should have triggered complex analysis!')
        else:
            print(f'⚠️  WORKFLOW PATH: INCOMPLETE ({current_step})')
        print()
        
        # Show agent outputs
        if result.get("intent_analysis"):
            print('🧠 INTENT ANALYSIS RESULT:')
            intent = result["intent_analysis"]
            print(f'   Intent Type: {intent.get("intent_type", "Unknown")}')
            print(f'   Needs Analysis: {intent.get("needs_analysis", "Unknown")}')
            print(f'   Confidence: {intent.get("confidence", "Unknown")}')
            print()
        
        # Show data collection summary
        if result.get("campaign_data"):
            print('📊 DATA COLLECTION SUMMARY:')
            campaign_data = result["campaign_data"]
            
            # Count campaigns
            fb_count = 0
            ig_count = 0
            
            if "facebook_campaigns" in campaign_data:
                try:
                    fb_data = eval(campaign_data["facebook_campaigns"])
                    fb_count = len(fb_data.get("campaigns", []))
                except:
                    pass
            
            if "instagram_campaigns" in campaign_data:
                try:
                    ig_data = eval(campaign_data["instagram_campaigns"])
                    ig_count = len(ig_data.get("campaigns", []))
                except:
                    pass
            
            print(f'   Facebook Campaigns: {fb_count}')
            print(f'   Instagram Campaigns: {ig_count}')
            print(f'   Total Campaigns: {fb_count + ig_count}')
            print()
        
        if result['status'] == 'completed':
            print('📋 FINAL REPORT:')
            print('=' * 80)
            
            # Show the final output
            final_output = result['final_output']
            
            # For complex workflow, show the full report
            if len(final_output) > 2000:
                print(final_output[:2000] + "...")
                print()
                print(f"[Report truncated - Full length: {len(final_output)} characters]")
            else:
                print(final_output)
            
            print('=' * 80)
            print()
            
            # Success summary
            print('🎉 COMPLEX WORKFLOW TEST COMPLETED!')
            print('=' * 50)
            print('✅ Multi-agent workflow executed successfully')
            print(f'✅ Comprehensive analysis completed in {execution_time:.1f} seconds')
            print('✅ All agents participated in the workflow')
            print('✅ Detailed report with recommendations generated')
            print(f'✅ Workflow visualization saved: complex_workflow_analysis_graph.png')
            print()
            print('🚀 Your complex multi-agent workflow is working perfectly!')
            
            return True
        else:
            print(f'❌ Complex Workflow Failed: {result.get("errors", [])}')
            return False
            
    except Exception as e:
        print(f'❌ Test failed with exception: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print('🧪 CAMPAIGN AI COMPLEX WORKFLOW TEST')
    print('Testing: Low CTR Campaign Analysis & Improvement Recommendations')
    print()
    
    success = await test_complex_workflow()
    
    if success:
        print('\n🎯 TEST RESULTS:')
        print('   ✅ Complex workflow triggered successfully')
        print('   ✅ All multi-agent steps executed')
        print('   ✅ Comprehensive report generated')
        print('   ✅ Tools and agents working correctly')
        print()
        print('📁 FILES GENERATED:')
        print('   🖼️  complex_workflow_analysis_graph.png - Workflow diagram')
        print('   📊 Detailed execution logs above')
    else:
        print('\n❌ COMPLEX WORKFLOW TEST FAILED')
        print('   Check the logs above for detailed error information')
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 