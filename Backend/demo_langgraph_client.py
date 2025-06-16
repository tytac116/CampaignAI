#!/usr/bin/env python3
"""
Campaign AI LangGraph Demo Client

This client demonstrates the enhanced multi-agent Campaign AI system by:
1. Connecting to the MCP server
2. Running different workflow scenarios
3. Generating LangSmith traces
4. Creating workflow graph visualizations
5. Testing various use cases (analysis, actions, hybrid)
"""

import asyncio
import json
import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the Backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Import our enhanced workflow graph
from app.agents.workflow_graph import create_campaign_graph

class CampaignAIDemoClient:
    """Demo client for testing the enhanced Campaign AI multi-agent system."""
    
    def __init__(self):
        """Initialize the demo client."""
        self.workflow_graph = create_campaign_graph(
            model="gpt-4o-mini",
            temperature=0.3
        )
        self.demo_results = []
        
        # Ensure LangSmith tracing is enabled
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "CampaignAI-MultiAgent-Demo"
        
        logger.info("🚀 Campaign AI Demo Client initialized")
        logger.info(f"📊 LangSmith Project: {os.environ.get('LANGCHAIN_PROJECT')}")
        logger.info(f"🔍 LangSmith Tracing: {os.environ.get('LANGCHAIN_TRACING_V2')}")
    
    def get_test_scenarios(self) -> List[Dict[str, Any]]:
        """Define comprehensive test scenarios for different use cases."""
        return [
            {
                "name": "Analysis Use Case - Performance Review",
                "type": "analysis",
                "instruction": "Analyze the performance of all Facebook campaigns from the last 30 days. Focus on CTR, ROAS, and conversion rates. Identify top performers and underperformers.",
                "expected_intent": "analysis",
                "description": "Pure analysis workflow - should route through monitor → analyze → optimize → report"
            },
            {
                "name": "Action Use Case - Campaign Creation",
                "type": "action", 
                "instruction": "Create a new Facebook campaign for promoting eco-friendly water bottles to millennials aged 25-35. Budget should be $50 daily, objective is conversions, and run for 2 weeks starting tomorrow.",
                "expected_intent": "action",
                "description": "Pure action workflow - should route through intent → execute actions → report"
            },
            {
                "name": "Hybrid Use Case - Optimization with Actions",
                "type": "hybrid",
                "instruction": "Find all Instagram campaigns with CTR below 1.5% and ROAS below 2.0, then pause the worst performers and increase budget by 20% for campaigns with good engagement but low reach.",
                "expected_intent": "hybrid",
                "description": "Hybrid workflow - should use full workflow with both analysis and actions"
            },
            {
                "name": "Bulk Operations Use Case",
                "type": "action",
                "instruction": "Pause all campaigns across all platforms that have been running for more than 60 days with a ROAS below 1.5. Also update their status to include a note about performance review.",
                "expected_intent": "action", 
                "description": "Complex bulk action workflow - tests bulk operations and multi-platform handling"
            },
            {
                "name": "Research and Create Use Case",
                "type": "hybrid",
                "instruction": "Research current trends in sustainable fashion marketing, then create 3 new Instagram campaigns targeting different demographics (Gen Z, Millennials, Gen X) with budgets optimized based on historical performance data.",
                "expected_intent": "hybrid",
                "description": "Multi-agent coordination - research + analysis + campaign creation"
            }
        ]
    
    async def run_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test scenario and capture results."""
        logger.info(f"\n{'='*80}")
        logger.info(f"🎯 RUNNING SCENARIO: {scenario['name']}")
        logger.info(f"📝 Type: {scenario['type']}")
        logger.info(f"💭 Instruction: {scenario['instruction']}")
        logger.info(f"🎪 Expected Intent: {scenario['expected_intent']}")
        logger.info(f"📋 Description: {scenario['description']}")
        logger.info(f"{'='*80}")
        
        start_time = datetime.now()
        
        try:
            # Run the workflow
            result = await self.workflow_graph.run_workflow(
                user_instruction=scenario['instruction'],
                campaign_context={
                    "demo_scenario": scenario['name'],
                    "expected_intent": scenario['expected_intent']
                }
            )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Analyze results
            scenario_result = {
                "scenario": scenario,
                "workflow_id": result["workflow_id"],
                "execution_time": execution_time,
                "status": result["status"],
                "intent_detected": result.get("intent_analysis", {}).get("intent_type", "unknown"),
                "intent_confidence": result.get("intent_analysis", {}).get("confidence", 0),
                "intent_match": result.get("intent_analysis", {}).get("intent_type") == scenario["expected_intent"],
                "steps_completed": result["current_step"],
                "tool_calls_count": len(result["tool_calls"]),
                "database_changes": result.get("action_results", {}).get("database_changes_made", False),
                "errors": result["errors"],
                "final_output_length": len(result["final_output"]),
                "validation_passed": result.get("validation_results", {}).get("is_valid", False),
                "langsmith_trace_url": f"https://smith.langchain.com/projects/{os.environ.get('LANGCHAIN_PROJECT', 'default')}"
            }
            
            # Log detailed results
            logger.info(f"✅ SCENARIO COMPLETED: {scenario['name']}")
            logger.info(f"⏱️  Execution Time: {execution_time:.2f}s")
            logger.info(f"🎯 Intent Detected: {scenario_result['intent_detected']} (confidence: {scenario_result['intent_confidence']:.2f})")
            logger.info(f"✅ Intent Match: {scenario_result['intent_match']}")
            logger.info(f"🔧 Tool Calls: {scenario_result['tool_calls_count']}")
            logger.info(f"💾 DB Changes: {scenario_result['database_changes']}")
            logger.info(f"🛡️ Validation: {scenario_result['validation_passed']}")
            logger.info(f"📊 Output Length: {scenario_result['final_output_length']} chars")
            
            if result["errors"]:
                logger.warning(f"⚠️  Errors: {len(result['errors'])}")
                for error in result["errors"]:
                    logger.warning(f"   - {error}")
            
            return scenario_result
            
        except Exception as e:
            logger.error(f"❌ SCENARIO FAILED: {scenario['name']} - {str(e)}")
            return {
                "scenario": scenario,
                "workflow_id": "failed",
                "execution_time": (datetime.now() - start_time).total_seconds(),
                "status": "failed",
                "error": str(e),
                "intent_detected": "unknown",
                "intent_match": False
            }
    
    async def run_all_scenarios(self) -> List[Dict[str, Any]]:
        """Run all test scenarios sequentially."""
        scenarios = self.get_test_scenarios()
        results = []
        
        logger.info(f"\n🚀 STARTING CAMPAIGN AI MULTI-AGENT DEMO")
        logger.info(f"📊 Total Scenarios: {len(scenarios)}")
        logger.info(f"🔍 LangSmith Project: {os.environ.get('LANGCHAIN_PROJECT')}")
        logger.info(f"⏰ Start Time: {datetime.now().isoformat()}")
        
        for i, scenario in enumerate(scenarios, 1):
            logger.info(f"\n📍 SCENARIO {i}/{len(scenarios)}")
            
            # Add delay between scenarios to ensure clean traces
            if i > 1:
                logger.info("⏳ Waiting 3 seconds between scenarios...")
                await asyncio.sleep(3)
            
            result = await self.run_scenario(scenario)
            results.append(result)
            
            # Save intermediate results
            self.save_results(results, f"demo_results_partial_{i}.json")
        
        logger.info(f"\n🎉 ALL SCENARIOS COMPLETED!")
        logger.info(f"⏰ Total Time: {sum(r.get('execution_time', 0) for r in results):.2f}s")
        
        return results
    
    def generate_workflow_graph(self) -> str:
        """Generate and save the workflow graph visualization."""
        logger.info("📊 Generating workflow graph visualization...")
        
        try:
            graph_path = "campaign_ai_workflow_graph.png"
            result_path = self.workflow_graph.visualize_graph(graph_path)
            
            if result_path:
                logger.info(f"✅ Workflow graph saved to: {result_path}")
                return result_path
            else:
                logger.error("❌ Failed to generate workflow graph")
                return None
                
        except Exception as e:
            logger.error(f"❌ Graph generation failed: {str(e)}")
            return None
    
    def save_results(self, results: List[Dict[str, Any]], filename: str = None):
        """Save demo results to JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"campaign_ai_demo_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump({
                    "demo_metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "total_scenarios": len(results),
                        "langsmith_project": os.environ.get('LANGCHAIN_PROJECT'),
                        "langsmith_tracing": os.environ.get('LANGCHAIN_TRACING_V2')
                    },
                    "results": results
                }, f, indent=2, default=str)
            
            logger.info(f"💾 Results saved to: {filename}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save results: {str(e)}")
    
    def print_summary(self, results: List[Dict[str, Any]]):
        """Print a comprehensive summary of all demo results."""
        logger.info(f"\n{'='*100}")
        logger.info(f"📊 CAMPAIGN AI MULTI-AGENT DEMO SUMMARY")
        logger.info(f"{'='*100}")
        
        total_scenarios = len(results)
        successful_scenarios = len([r for r in results if r.get('status') == 'completed'])
        failed_scenarios = total_scenarios - successful_scenarios
        total_time = sum(r.get('execution_time', 0) for r in results)
        total_tool_calls = sum(r.get('tool_calls_count', 0) for r in results)
        intent_matches = len([r for r in results if r.get('intent_match', False)])
        db_changes = len([r for r in results if r.get('database_changes', False)])
        
        logger.info(f"📈 Overall Statistics:")
        logger.info(f"   • Total Scenarios: {total_scenarios}")
        logger.info(f"   • Successful: {successful_scenarios}")
        logger.info(f"   • Failed: {failed_scenarios}")
        logger.info(f"   • Success Rate: {(successful_scenarios/total_scenarios)*100:.1f}%")
        logger.info(f"   • Total Execution Time: {total_time:.2f}s")
        logger.info(f"   • Average Time per Scenario: {total_time/total_scenarios:.2f}s")
        logger.info(f"   • Total Tool Calls: {total_tool_calls}")
        logger.info(f"   • Intent Detection Accuracy: {(intent_matches/total_scenarios)*100:.1f}%")
        logger.info(f"   • Scenarios with DB Changes: {db_changes}")
        
        logger.info(f"\n🎯 Scenario Details:")
        for i, result in enumerate(results, 1):
            status_emoji = "✅" if result.get('status') == 'completed' else "❌"
            intent_emoji = "🎯" if result.get('intent_match', False) else "❓"
            db_emoji = "💾" if result.get('database_changes', False) else "📖"
            
            logger.info(f"   {i}. {status_emoji} {result['scenario']['name']}")
            logger.info(f"      {intent_emoji} Intent: {result.get('intent_detected', 'unknown')} (expected: {result['scenario']['expected_intent']})")
            logger.info(f"      ⏱️  Time: {result.get('execution_time', 0):.2f}s")
            logger.info(f"      🔧 Tools: {result.get('tool_calls_count', 0)}")
            logger.info(f"      {db_emoji} Type: {result['scenario']['type']}")
            
            if result.get('errors'):
                logger.info(f"      ⚠️  Errors: {len(result['errors'])}")
        
        logger.info(f"\n🔍 LangSmith Traces:")
        logger.info(f"   • Project: {os.environ.get('LANGCHAIN_PROJECT')}")
        logger.info(f"   • URL: https://smith.langchain.com/projects/{os.environ.get('LANGCHAIN_PROJECT', 'default')}")
        logger.info(f"   • Each scenario should appear as a separate trace")
        logger.info(f"   • Look for multi-agent coordination and tool usage patterns")
        
        logger.info(f"\n📊 Graph Visualization:")
        logger.info(f"   • Check for 'campaign_ai_workflow_graph.png' in current directory")
        logger.info(f"   • Shows the complete multi-agent workflow structure")
        logger.info(f"   • Includes conditional routing and parallel processing paths")
        
        logger.info(f"{'='*100}")

async def main():
    """Main demo execution function."""
    try:
        # Initialize demo client
        demo_client = CampaignAIDemoClient()
        
        # Generate workflow graph first
        graph_path = demo_client.generate_workflow_graph()
        
        # Run all scenarios
        results = await demo_client.run_all_scenarios()
        
        # Save final results
        demo_client.save_results(results)
        
        # Print comprehensive summary
        demo_client.print_summary(results)
        
        logger.info(f"\n🎉 DEMO COMPLETED SUCCESSFULLY!")
        logger.info(f"📊 Check LangSmith for detailed traces: https://smith.langchain.com/projects/{os.environ.get('LANGCHAIN_PROJECT', 'default')}")
        if graph_path:
            logger.info(f"🖼️  Workflow graph: {graph_path}")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {str(e)}")
        raise

if __name__ == "__main__":
    # Ensure we have the required environment variables
    required_vars = ["OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY", "LANGSMITH_API_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    # Run the demo
    asyncio.run(main())