#!/usr/bin/env python3
"""
Simple MCP Client Test

This script tests the MCP server connection and basic functionality
before running the full LangGraph demo.
"""

import asyncio
import json
import logging
import subprocess
import time
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class MCPClientTest:
    """Simple MCP client for testing server connectivity."""
    
    def __init__(self):
        """Initialize the MCP client test."""
        self.server_process = None
        
    def start_mcp_server(self) -> bool:
        """Start the MCP server in the background."""
        try:
            logger.info("🚀 Starting MCP server...")
            
            # Start the server as a background process
            self.server_process = subprocess.Popen(
                [sys.executable, "mcp_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            # Give the server time to start
            time.sleep(3)
            
            # Check if the process is still running
            if self.server_process.poll() is None:
                logger.info("✅ MCP server started successfully")
                return True
            else:
                stdout, stderr = self.server_process.communicate()
                logger.error(f"❌ MCP server failed to start")
                logger.error(f"STDOUT: {stdout.decode()}")
                logger.error(f"STDERR: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start MCP server: {str(e)}")
            return False
    
    def stop_mcp_server(self):
        """Stop the MCP server."""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                logger.info("🛑 MCP server stopped")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                logger.info("🛑 MCP server killed (timeout)")
            except Exception as e:
                logger.error(f"❌ Error stopping MCP server: {str(e)}")
    
    def test_server_info(self) -> bool:
        """Test basic server info functionality."""
        try:
            logger.info("🔍 Testing server info...")
            
            # This would normally use MCP protocol, but for now we'll test the import
            from mcp_server import mcp
            
            # Test that the server has the expected tools
            tools = mcp.list_tools()
            logger.info(f"📊 Found {len(tools)} tools")
            
            # Check for key tools
            expected_tools = [
                "get_server_info",
                "test_connection", 
                "mcp_create_campaign",
                "mcp_analyze_campaign_performance",
                "mcp_search_campaign_data"
            ]
            
            tool_names = [tool.name for tool in tools]
            missing_tools = [tool for tool in expected_tools if tool not in tool_names]
            
            if missing_tools:
                logger.error(f"❌ Missing expected tools: {missing_tools}")
                return False
            
            logger.info("✅ All expected tools found")
            return True
            
        except Exception as e:
            logger.error(f"❌ Server info test failed: {str(e)}")
            return False
    
    def test_environment_variables(self) -> bool:
        """Test that all required environment variables are present."""
        logger.info("🔍 Testing environment variables...")
        
        required_vars = [
            "OPENAI_API_KEY",
            "SUPABASE_URL", 
            "SUPABASE_ANON_KEY",
            "LANGSMITH_API_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
            else:
                # Show partial key for verification (first 8 chars + ...)
                value = os.environ.get(var)
                masked_value = value[:8] + "..." if len(value) > 8 else value
                logger.info(f"✅ {var}: {masked_value}")
        
        if missing_vars:
            logger.error(f"❌ Missing environment variables: {missing_vars}")
            return False
        
        logger.info("✅ All required environment variables present")
        return True
    
    def test_imports(self) -> bool:
        """Test that all required modules can be imported."""
        logger.info("🔍 Testing imports...")
        
        try:
            # Test core imports
            from app.agents.workflow_graph import create_campaign_graph
            from app.tools.campaign_action_tool import create_campaign
            from app.agents.campaign_action_agent import CampaignActionAgent
            
            logger.info("✅ Core workflow imports successful")
            
            # Test LangChain imports
            from langchain_openai import ChatOpenAI
            from langgraph.graph import StateGraph
            
            logger.info("✅ LangChain imports successful")
            
            # Test database imports
            from supabase import create_client
            
            logger.info("✅ Database imports successful")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Import test failed: {str(e)}")
            return False
    
    def test_database_connection(self) -> bool:
        """Test database connectivity."""
        logger.info("🔍 Testing database connection...")
        
        try:
            from supabase import create_client
            
            supabase_url = os.environ.get("SUPABASE_URL")
            supabase_key = os.environ.get("SUPABASE_ANON_KEY")
            
            if not supabase_url or not supabase_key:
                logger.error("❌ Missing Supabase credentials")
                return False
            
            # Create client
            supabase = create_client(supabase_url, supabase_key)
            
            # Test connection with a simple query
            result = supabase.table("campaigns").select("id").limit(1).execute()
            
            logger.info(f"✅ Database connection successful")
            logger.info(f"📊 Test query returned {len(result.data)} rows")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {str(e)}")
            return False
    
    def test_openai_connection(self) -> bool:
        """Test OpenAI API connectivity."""
        logger.info("🔍 Testing OpenAI connection...")
        
        try:
            from langchain_openai import ChatOpenAI
            
            # Create a simple LLM instance
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.1,
                max_tokens=50
            )
            
            # Test with a simple message
            response = llm.invoke("Say 'OpenAI connection test successful'")
            
            logger.info(f"✅ OpenAI connection successful")
            logger.info(f"🤖 Response: {response.content}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ OpenAI connection test failed: {str(e)}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all MCP client tests."""
        logger.info(f"\n{'='*80}")
        logger.info(f"🧪 STARTING MCP CLIENT TESTS")
        logger.info(f"{'='*80}")
        
        tests = [
            ("Environment Variables", self.test_environment_variables),
            ("Module Imports", self.test_imports),
            ("Database Connection", self.test_database_connection),
            ("OpenAI Connection", self.test_openai_connection),
            # ("MCP Server Info", self.test_server_info)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            logger.info(f"\n🔬 Running test: {test_name}")
            try:
                result = test_func()
                results.append((test_name, result))
                
                if result:
                    logger.info(f"✅ {test_name}: PASSED")
                else:
                    logger.error(f"❌ {test_name}: FAILED")
                    
            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {str(e)}")
                results.append((test_name, False))
        
        # Summary
        passed_tests = len([r for r in results if r[1]])
        total_tests = len(results)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 TEST SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"✅ Passed: {passed_tests}/{total_tests}")
        logger.info(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
        logger.info(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"   {status}: {test_name}")
        
        all_passed = all(result for _, result in results)
        
        if all_passed:
            logger.info(f"\n🎉 ALL TESTS PASSED! Ready for LangGraph demo.")
        else:
            logger.error(f"\n❌ Some tests failed. Please fix issues before running demo.")
        
        return all_passed

async def main():
    """Main test execution function."""
    test_client = MCPClientTest()
    
    try:
        # Run all tests
        success = await test_client.run_all_tests()
        
        if success:
            logger.info(f"\n🚀 MCP system is ready!")
            logger.info(f"💡 You can now run: python3 demo_langgraph_client.py")
        else:
            logger.error(f"\n❌ MCP system has issues that need to be resolved.")
            
        return success
        
    except Exception as e:
        logger.error(f"❌ Test execution failed: {str(e)}")
        return False
    
    finally:
        # Clean up
        test_client.stop_mcp_server()

if __name__ == "__main__":
    # Ensure we have the required environment variables
    required_vars = ["OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY", "LANGSMITH_API_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    # Run the demo
    success = asyncio.run(main())
    sys.exit(0 if success else 1)