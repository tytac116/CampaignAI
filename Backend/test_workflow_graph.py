#!/usr/bin/env python3
"""
Test LangGraph Workflow and Generate Visualization

This script tests the Campaign Optimization LangGraph workflow and generates
a PNG visualization of the graph structure.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add Backend directory to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_workflow_graph():
    """Test the LangGraph workflow and generate visualization."""
    print('🧪 Testing Campaign Optimization LangGraph Workflow')
    print('=' * 60)
    
    try:
        # Import the workflow graph
        from app.agents.workflow_graph import create_campaign_graph
        
        print('📊 Creating Campaign Optimization Graph...')
        workflow_graph = create_campaign_graph()
        
        # Generate visualization
        print('🎨 Generating graph visualization...')
        output_path = "campaign_workflow_graph.png"
        viz_path = workflow_graph.visualize_graph(output_path)
        
        if viz_path:
            print(f'✅ Graph visualization saved to: {viz_path}')
        else:
            print('❌ Failed to generate graph visualization')
        
        # Test workflow execution
        print('🚀 Testing workflow execution...')
        
        test_instruction = """
        Analyze and optimize our Facebook and Instagram campaigns.
        Focus on improving CTR and reducing CPC for campaigns with IDs 1, 2, and 3.
        Provide specific recommendations for budget allocation and targeting.
        """
        
        test_context = {
            "campaign_ids": [1, 2, 3],
            "focus_metrics": ["CTR", "CPC"],
            "platforms": ["facebook", "instagram"]
        }
        
        start_time = datetime.now()
        
        # Run the workflow
        result = await workflow_graph.run_workflow(
            user_instruction=test_instruction,
            campaign_context=test_context
        )
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Display results
        print('\n📋 WORKFLOW EXECUTION RESULTS')
        print('=' * 40)
        print(f'Workflow ID: {result["workflow_id"]}')
        print(f'Status: {result["status"]}')
        print(f'Current Step: {result["current_step"]}')
        print(f'Execution Time: {execution_time:.2f} seconds')
        print(f'Total Tool Calls: {len(result["tool_calls"])}')
        print(f'Iteration Count: {result["iteration_count"]}')
        print(f'Errors: {len(result["errors"])}')
        
        if result["errors"]:
            print('\n❌ ERRORS:')
            for error in result["errors"]:
                print(f'  - {error}')
        
        print(f'\n📊 WORKFLOW PHASES:')
        phases = [
            ('Monitoring', result.get("monitoring_results", {})),
            ('Analysis', result.get("analysis_results", {})),
            ('Optimization', result.get("optimization_results", {})),
            ('Reporting', result.get("reporting_results", {}))
        ]
        
        for phase_name, phase_result in phases:
            status = phase_result.get("status", "not_executed")
            tool_calls = len(phase_result.get("tool_calls", []))
            print(f'  {phase_name}: {status} ({tool_calls} tool calls)')
        
        print(f'\n📝 FINAL OUTPUT:')
        print('-' * 40)
        final_output = result.get("final_output", "No output generated")
        print(final_output[:500] + "..." if len(final_output) > 500 else final_output)
        
        print(f'\n🔧 TOOL CALLS SUMMARY:')
        print('-' * 40)
        tool_summary = {}
        for tool_call in result["tool_calls"]:
            tool_name = tool_call.get("name", "unknown")
            tool_summary[tool_name] = tool_summary.get(tool_name, 0) + 1
        
        for tool_name, count in tool_summary.items():
            print(f'  {tool_name}: {count} calls')
        
        print(f'\n✅ WORKFLOW TEST COMPLETED SUCCESSFULLY!')
        print(f'📊 Graph visualization: {viz_path}')
        print(f'⏱️  Total execution time: {execution_time:.2f} seconds')
        
        return True
        
    except Exception as e:
        print(f'❌ Workflow test failed: {str(e)}')
        logger.error(f"Workflow test error: {str(e)}", exc_info=True)
        return False

async def main():
    """Main test function."""
    print('🎯 Campaign AI LangGraph Workflow Test')
    print('=' * 60)
    
    # Check environment variables
    required_vars = ['OPENAI_API_KEY', 'TAVILY_API_KEY', 'PINECONE_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f'❌ Missing environment variables: {", ".join(missing_vars)}')
        return False
    
    print('✅ Environment variables loaded')
    
    # Run workflow test
    success = await test_workflow_graph()
    
    if success:
        print('\n🎉 ALL TESTS PASSED!')
        print('📊 Check the generated PNG file for the workflow visualization')
    else:
        print('\n❌ TESTS FAILED!')
    
    return success

if __name__ == "__main__":
    asyncio.run(main()) 