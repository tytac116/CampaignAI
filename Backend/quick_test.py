#!/usr/bin/env python3
"""Quick test for the top 10 campaigns question."""

import asyncio
import logging
import sys
import os

# Add Backend to path
sys.path.append(os.getcwd())

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_simple_question():
    """Test the simple workflow with the specific question."""
    
    try:
        from app.agents.simple_workflow import SimpleMultiAgentWorkflow
        
        print('🧪 Testing: "Show me the top 10 best performing campaigns"')
        print('=' * 60)
        
        workflow = SimpleMultiAgentWorkflow()
        result = await workflow.run_workflow('Show me the top 10 best performing campaigns')
        
        print(f'✅ Status: {result["status"]}')
        print(f'📊 Current Step: {result["current_step"]}')
        print(f'🛠️ Tool Calls: {len(result.get("tool_calls", []))}')
        print(f'❌ Errors: {len(result.get("errors", []))}')
        
        if result['status'] == 'completed':
            print('\n🤖 FINAL OUTPUT:')
            print('=' * 60)
            print(result['final_output'])
            print('=' * 60)
            return True
        else:
            print(f'❌ Failed: {result.get("errors", [])}')
            return False
            
    except Exception as e:
        print(f'❌ Test failed with exception: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print('🚀 Quick Test: Top 10 Best Performing Campaigns')
    
    result = await test_simple_question()
    
    print(f'\n📊 Test Result: {"✅ PASSED" if result else "❌ FAILED"}')
    
    if result:
        print('🎉 The workflow can handle simple questions!')
        print('✅ Ready for chatbot integration')
    else:
        print('🔧 The workflow needs more fixes')
    
    return result

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
