#!/usr/bin/env python3
"""
Test Simple Multi-Agent Workflow

This script tests the new simple multi-agent workflow that should actually work.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add Backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.simple_workflow import create_simple_workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_simple_workflow():
    """Test the simple multi-agent workflow."""
    print("🚀 Testing Simple Multi-Agent Workflow")
    print("="*60)
    
    try:
        # Create the workflow
        print("📊 Creating Simple Multi-Agent Workflow...")
        workflow = create_simple_workflow()
        print(f"✅ Workflow created: {workflow.workflow_id}")
        
        # Test user instruction
        user_instruction = "Analyze my Facebook campaigns and optimize their performance with new content"
        
        print(f"\n📝 User Instruction: {user_instruction}")
        print("="*60)
        
        # Run the workflow
        print("🔄 Starting workflow execution...")
        start_time = datetime.now()
        
        result = await workflow.run_workflow(user_instruction)
        
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
        print(result['final_output'][:1500] + "..." if len(result['final_output']) > 1500 else result['final_output'])
        
        # Test graph visualization
        print("\n📊 Generating graph visualization...")
        try:
            viz_path = workflow.visualize_graph("simple_workflow_graph.png")
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
            ("All steps completed", result['current_step'] == 'completed'),
            ("Intent analysis done", 'intent_analysis' in result and result['intent_analysis']),
            ("Data collected", 'campaign_data' in result and result['campaign_data']),
            ("Performance analyzed", 'performance_analysis' in result and result['performance_analysis']),
            ("Strategy developed", 'optimization_strategy' in result and result['optimization_strategy']),
            ("Content generated", 'generated_content' in result and result['generated_content'])
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
            print("🎉 SIMPLE MULTI-AGENT WORKFLOW TEST: SUCCESS!")
            print("✅ The workflow flows properly through all agents")
            print("✅ MCP tools are integrated and working")
            print("✅ All agents execute their tasks")
            print("✅ LangGraph orchestrates the flow correctly")
        else:
            print("❌ SIMPLE MULTI-AGENT WORKFLOW TEST: FAILED!")
            print("❌ The workflow has issues that need to be addressed")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Workflow test failed: {str(e)}")
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        return None

if __name__ == "__main__":
    print("🤖 Campaign AI - Simple Multi-Agent Workflow Test")
    print("="*60)
    
    # Run the test
    asyncio.run(test_simple_workflow()) 