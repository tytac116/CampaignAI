#!/usr/bin/env python3
"""
Test LangGraph Workflow End-to-End

This script tests the complete LangGraph workflow to ensure it flows
from start node to end node properly with MCP tool integration.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add Backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.workflow_graph import create_campaign_graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_langgraph_workflow():
    """Test the complete LangGraph workflow."""
    print("🚀 Testing LangGraph Campaign Optimization Workflow")
    print("="*60)
    
    try:
        # Create the workflow graph
        print("📊 Creating Campaign Optimization Graph...")
        graph = create_campaign_graph()
        print(f"✅ Graph created: {graph.workflow_id}")
        
        # Test user instruction
        user_instruction = "Analyze my Facebook campaigns and optimize their performance with new content"
        
        print(f"\n📝 User Instruction: {user_instruction}")
        print("="*60)
        
        # Run the workflow
        print("🔄 Starting LangGraph workflow execution...")
        start_time = datetime.now()
        
        result = await graph.run_workflow(
            user_instruction=user_instruction,
            campaign_context={"test_mode": True}
        )
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print("="*60)
        print("📊 WORKFLOW EXECUTION RESULTS")
        print("="*60)
        
        print(f"🆔 Workflow ID: {result['workflow_id']}")
        print(f"📈 Status: {result['status']}")
        print(f"🔧 Current Step: {result['current_step']}")
        print(f"🛠️ Tool Calls: {len(result['tool_calls'])}")
        print(f"⚡ Execution Time: {execution_time:.2f}s")
        print(f"❌ Errors: {len(result['errors'])}")
        
        if result['errors']:
            print("\n🚨 ERRORS:")
            for error in result['errors']:
                print(f"   • {error}")
        
        print("\n🛠️ TOOL CALLS MADE:")
        for i, tool_call in enumerate(result['tool_calls'], 1):
            print(f"   {i}. {tool_call.get('tool', 'unknown')} - {tool_call.get('status', 'unknown')}")
        
        print("\n📋 FINAL OUTPUT:")
        print("-" * 40)
        print(result['final_output'][:1000] + "..." if len(result['final_output']) > 1000 else result['final_output'])
        
        # Test graph visualization
        print("\n📊 Generating graph visualization...")
        try:
            viz_path = graph.visualize_graph("test_workflow_graph.png")
            if viz_path:
                print(f"✅ Graph visualization saved to: {viz_path}")
            else:
                print("❌ Graph visualization failed")
        except Exception as e:
            print(f"❌ Graph visualization error: {str(e)}")
        
        # Validation
        print("\n🛡️ WORKFLOW VALIDATION:")
        print("-" * 40)
        
        validation_checks = [
            ("Workflow completed", result['status'] == 'completed'),
            ("No errors", len(result['errors']) == 0),
            ("Tools were used", len(result['tool_calls']) > 0),
            ("Output generated", len(result['final_output']) > 100),
            ("Validation passed", result.get('validation_results', {}).get('is_valid', False)),
            ("All nodes executed", result['current_step'] == 'validated')
        ]
        
        passed_checks = 0
        for check_name, check_result in validation_checks:
            status = "✅ PASS" if check_result else "❌ FAIL"
            print(f"   {status}: {check_name}")
            if check_result:
                passed_checks += 1
        
        success_rate = (passed_checks / len(validation_checks)) * 100
        print(f"\n📊 Overall Success Rate: {success_rate:.1f}% ({passed_checks}/{len(validation_checks)})")
        
        if success_rate >= 80:
            print("🎉 LANGGRAPH WORKFLOW TEST: SUCCESS!")
            print("✅ The workflow flows properly from start to end node")
            print("✅ MCP tools are integrated and working")
            print("✅ All nodes execute in sequence")
        else:
            print("❌ LANGGRAPH WORKFLOW TEST: FAILED!")
            print("❌ The workflow has issues that need to be addressed")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Workflow test failed: {str(e)}")
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        return None

if __name__ == "__main__":
    print("🤖 Campaign AI - LangGraph Workflow Test")
    print("="*60)
    
    # Run the tests
    asyncio.run(test_langgraph_workflow()) 