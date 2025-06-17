#!/usr/bin/env python3
"""
Comprehensive Workflow Testing Script

This script tests every component of the Campaign AI system to identify
why the workflow is getting stuck at the analyze intent step.
"""

import asyncio
import logging
import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, List

# Add Backend directory to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

# Set up comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('workflow_test.log')
    ]
)

logger = logging.getLogger(__name__)

class WorkflowTester:
    """Comprehensive workflow testing class."""
    
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "detailed_results": {},
            "errors": []
        }
    
    def log_test_result(self, test_name: str, success: bool, details: Dict[str, Any] = None, error: str = None):
        """Log test result."""
        self.test_results["tests_run"] += 1
        if success:
            self.test_results["tests_passed"] += 1
            logger.info(f"✅ {test_name}: PASSED")
        else:
            self.test_results["tests_failed"] += 1
            logger.error(f"❌ {test_name}: FAILED - {error}")
            self.test_results["errors"].append(f"{test_name}: {error}")
        
        self.test_results["detailed_results"][test_name] = {
            "success": success,
            "details": details or {},
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
    
    async def test_mcp_server_connection(self):
        """Test MCP server connection and tool availability."""
        logger.info("🔌 Testing MCP Server Connection...")
        
        try:
            from mcp.client.stdio import stdio_client, StdioServerParameters
            from mcp.client.session import ClientSession
            
            server_path = os.path.join(backend_dir, "mcp_server.py")
            
            if not os.path.exists(server_path):
                raise FileNotFoundError(f"MCP server not found at {server_path}")
            
            server_params = StdioServerParameters(
                command="python3",
                args=[server_path],
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # List available tools
                    tools = await session.list_tools()
                    tool_names = [tool.name for tool in tools.tools]
                    
                    logger.info(f"📋 Available MCP Tools ({len(tool_names)}):")
                    for tool_name in tool_names:
                        logger.info(f"   🛠️ {tool_name}")
                    
                    # Test a simple tool call
                    if "mcp_get_facebook_campaigns" in tool_names:
                        result = await session.call_tool("mcp_get_facebook_campaigns", {"limit": 1})
                        logger.info(f"✅ Test tool call successful: {len(result.content[0].text)} chars")
                    
                    self.log_test_result(
                        "mcp_server_connection",
                        True,
                        {"tools_available": len(tool_names), "tool_names": tool_names}
                    )
                    
                    return tool_names
                    
        except Exception as e:
            self.log_test_result("mcp_server_connection", False, error=str(e))
            return []
    
    async def test_individual_agents(self):
        """Test each agent individually."""
        logger.info("🤖 Testing Individual Agents...")
        
        # Test Campaign Agent
        try:
            from app.agents.campaign_agent import CampaignAgent
            
            agent = CampaignAgent()
            result = await agent.execute_campaign_workflow(
                "Show me current Facebook campaign performance",
                {"test": True}
            )
            
            self.log_test_result(
                "campaign_agent",
                result["status"] == "completed",
                {"tool_calls": len(result.get("tool_calls", [])), "workflow_id": result.get("workflow_id")}
            )
            
        except Exception as e:
            self.log_test_result("campaign_agent", False, error=str(e))
        
        # Test Campaign Action Agent
        try:
            from app.agents.campaign_action_agent import CampaignActionAgent
            
            action_agent = CampaignActionAgent()
            
            # Test intent analysis
            intent_result = await action_agent.analyze_user_intent(
                "Create a new Facebook campaign for lead generation with $1000 budget"
            )
            
            self.log_test_result(
                "campaign_action_agent_intent",
                "intent_type" in intent_result,
                {"intent_type": intent_result.get("intent_type"), "confidence": intent_result.get("confidence")}
            )
            
            # Test action workflow
            workflow_result = await action_agent.execute_action_workflow(
                "Analyze current campaign performance",
                intent_result
            )
            
            self.log_test_result(
                "campaign_action_agent_workflow",
                workflow_result.get("success", False),
                {"workflow_id": workflow_result.get("workflow_id")}
            )
            
        except Exception as e:
            self.log_test_result("campaign_action_agent", False, error=str(e))
        
        # Test Coordinator Agent
        try:
            from app.agents.coordinator import CoordinatorAgent
            
            coordinator = CoordinatorAgent()
            coord_result = await coordinator.coordinate_campaign_optimization(
                campaign_ids=[1, 2, 3],
                trigger_reason="test_evaluation"
            )
            
            self.log_test_result(
                "coordinator_agent",
                coord_result["status"] in ["completed", "failed"],
                {"status": coord_result["status"], "phases": len(coord_result.get("phases_completed", []))}
            )
            
        except Exception as e:
            self.log_test_result("coordinator_agent", False, error=str(e))
    
    async def test_workflow_nodes(self):
        """Test individual workflow nodes."""
        logger.info("🔧 Testing Workflow Nodes...")
        
        try:
            from app.agents.workflow_nodes import (
                CampaignMonitorNode,
                DataAnalysisNode,
                OptimizationNode,
                ReportingNode
            )
            from app.agents.state import create_initial_state
            
            # Create test state
            test_state = create_initial_state(
                workflow_id="test_workflow",
                campaign_ids=[1, 2],
                requested_analysis=["performance", "optimization"]
            )
            
            # Test Monitor Node
            try:
                monitor_node = CampaignMonitorNode()
                monitor_result = await monitor_node.execute(test_state)
                
                self.log_test_result(
                    "monitor_node",
                    len(monitor_result.get("errors", [])) == 0,
                    {"completed_agents": len(monitor_result.get("completed_agents", []))}
                )
            except Exception as e:
                self.log_test_result("monitor_node", False, error=str(e))
            
            # Test Analysis Node
            try:
                analysis_node = DataAnalysisNode()
                analysis_result = await analysis_node.execute(test_state)
                
                self.log_test_result(
                    "analysis_node",
                    len(analysis_result.get("errors", [])) == 0,
                    {"completed_agents": len(analysis_result.get("completed_agents", []))}
                )
            except Exception as e:
                self.log_test_result("analysis_node", False, error=str(e))
            
        except Exception as e:
            self.log_test_result("workflow_nodes", False, error=str(e))
    
    async def test_simple_workflow(self):
        """Test the simple workflow implementation."""
        logger.info("🌊 Testing Simple Workflow...")
        
        try:
            from app.agents.simple_workflow import SimpleMultiAgentWorkflow
            
            workflow = SimpleMultiAgentWorkflow()
            
            # Test with a simple instruction
            result = await workflow.run_workflow(
                "Analyze the performance of my Facebook campaigns and suggest optimizations"
            )
            
            self.log_test_result(
                "simple_workflow",
                result["status"] == "completed",
                {
                    "status": result["status"],
                    "tool_calls": len(result.get("tool_calls", [])),
                    "final_output_length": len(result.get("final_output", ""))
                }
            )
            
            # Log detailed workflow steps
            logger.info(f"📊 Workflow Steps Completed: {result.get('current_step', 'unknown')}")
            if result.get("tool_calls"):
                logger.info(f"🛠️ Tool Calls Made: {len(result['tool_calls'])}")
                for i, call in enumerate(result["tool_calls"][:5]):  # Show first 5
                    logger.info(f"   {i+1}. {call}")
            
            return result
            
        except Exception as e:
            self.log_test_result("simple_workflow", False, error=str(e))
            return None
    
    async def test_workflow_graph(self):
        """Test the LangGraph workflow implementation."""
        logger.info("📊 Testing LangGraph Workflow...")
        
        try:
            from app.agents.workflow_graph import CampaignOptimizationGraph
            
            graph = CampaignOptimizationGraph()
            
            # Test with a simple instruction
            result = await graph.run_workflow(
                "Show me the performance of my current marketing campaigns",
                {"test_mode": True}
            )
            
            self.log_test_result(
                "workflow_graph",
                result["status"] == "completed",
                {
                    "status": result["status"],
                    "current_step": result.get("current_step"),
                    "tool_calls": len(result.get("tool_calls", [])),
                    "errors": len(result.get("errors", []))
                }
            )
            
            # Log detailed steps
            logger.info(f"📋 Current Step: {result.get('current_step', 'unknown')}")
            logger.info(f"🔄 Iteration Count: {result.get('iteration_count', 0)}")
            logger.info(f"✅ Should Continue: {result.get('should_continue', False)}")
            
            if result.get("errors"):
                logger.error(f"❌ Workflow Errors: {result['errors']}")
            
            return result
            
        except Exception as e:
            self.log_test_result("workflow_graph", False, error=str(e))
            return None
    
    async def test_intent_analysis_specifically(self):
        """Deep dive into intent analysis issues."""
        logger.info("🧠 Deep Testing Intent Analysis...")
        
        test_instructions = [
            "Show me my Facebook campaign performance",
            "Create a new Instagram campaign for lead generation",
            "Optimize my current marketing campaigns",
            "Generate ad copy for my product launch",
            "Analyze which campaigns are performing best"
        ]
        
        for i, instruction in enumerate(test_instructions):
            logger.info(f"🧪 Testing instruction {i+1}: {instruction}")
            
            try:
                # Test with workflow graph
                from app.agents.workflow_graph import CampaignOptimizationGraph
                
                graph = CampaignOptimizationGraph()
                
                # Create initial state
                initial_state = {
                    "workflow_id": f"intent_test_{i+1}",
                    "current_step": "starting",
                    "user_instruction": instruction,
                    "campaign_context": {"test_mode": True},
                    "intent_analysis": {},
                    "campaign_data": {},
                    "performance_metrics": {},
                    "analysis_results": {},
                    "optimization_strategy": {},
                    "content_generated": {},
                    "action_results": {},
                    "validation_results": {},
                    "iteration_count": 0,
                    "should_continue": True,
                    "tool_calls": [],
                    "final_output": "",
                    "errors": [],
                    "started_at": datetime.now().isoformat(),
                    "completed_at": None,
                    "status": "running"
                }
                
                # Test just the intent analysis node
                intent_result = await graph._analyze_intent_node(initial_state)
                
                self.log_test_result(
                    f"intent_analysis_{i+1}",
                    "intent_analysis" in intent_result and len(intent_result["intent_analysis"]) > 0,
                    {
                        "instruction": instruction,
                        "intent_found": "intent_analysis" in intent_result,
                        "current_step": intent_result.get("current_step"),
                        "errors": intent_result.get("errors", [])
                    }
                )
                
                logger.info(f"   📋 Intent Analysis Result: {intent_result.get('intent_analysis', {})}")
                logger.info(f"   📊 Current Step: {intent_result.get('current_step')}")
                
                if intent_result.get("errors"):
                    logger.error(f"   ❌ Errors: {intent_result['errors']}")
                
            except Exception as e:
                self.log_test_result(f"intent_analysis_{i+1}", False, error=str(e))
                logger.error(f"   ❌ Exception: {str(e)}")
    
    async def run_comprehensive_test(self):
        """Run all tests comprehensively."""
        logger.info("🚀 Starting Comprehensive Workflow Testing...")
        logger.info("=" * 60)
        
        # Test 1: MCP Server Connection
        available_tools = await self.test_mcp_server_connection()
        
        # Test 2: Individual Agents
        await self.test_individual_agents()
        
        # Test 3: Workflow Nodes
        await self.test_workflow_nodes()
        
        # Test 4: Simple Workflow
        simple_result = await self.test_simple_workflow()
        
        # Test 5: LangGraph Workflow
        graph_result = await self.test_workflow_graph()
        
        # Test 6: Deep Intent Analysis
        await self.test_intent_analysis_specifically()
        
        # Generate final report
        logger.info("=" * 60)
        logger.info("📊 COMPREHENSIVE TEST RESULTS")
        logger.info("=" * 60)
        
        logger.info(f"✅ Tests Passed: {self.test_results['tests_passed']}")
        logger.info(f"❌ Tests Failed: {self.test_results['tests_failed']}")
        logger.info(f"📊 Total Tests: {self.test_results['tests_run']}")
        logger.info(f"📈 Success Rate: {(self.test_results['tests_passed'] / self.test_results['tests_run'] * 100):.1f}%")
        
        if self.test_results["errors"]:
            logger.error("❌ ERRORS FOUND:")
            for error in self.test_results["errors"]:
                logger.error(f"   • {error}")
        
        # Save detailed results
        with open("comprehensive_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info("💾 Detailed results saved to comprehensive_test_results.json")
        
        return self.test_results

async def main():
    """Main test function."""
    tester = WorkflowTester()
    results = await tester.run_comprehensive_test()
    
    # Return exit code based on results
    if results["tests_failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main()) 