#!/usr/bin/env python3
"""
Individual MCP Tool Testing - Test each tool with specific inputs and expected outputs
"""

import asyncio
import sys
import os
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

class MCPToolTester:
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []

    async def run_tool_test(self, session, tool_name, test_input, expected_criteria, description):
        """Run a single tool test and validate the output"""
        print(f'\n🧪 Testing: {tool_name}')
        print(f'   Description: {description}')
        print(f'   Input: {test_input}')
        
        try:
            result = await session.call_tool(tool_name, test_input)
            output = result.content[0].text
            
            # Check expected criteria
            passed = True
            for criterion in expected_criteria:
                if criterion not in output.lower():
                    passed = False
                    break
            
            if passed:
                print(f'   ✅ PASSED - Output contains expected criteria')
                print(f'   📊 Output length: {len(output)} characters')
                print(f'   📝 Preview: {output[:150]}...')
                self.passed_tests += 1
                self.test_results.append((tool_name, "PASSED", output[:200]))
            else:
                print(f'   ❌ FAILED - Missing expected criteria: {expected_criteria}')
                print(f'   📊 Output length: {len(output)} characters')
                print(f'   📝 Full output: {output}')
                self.failed_tests += 1
                self.test_results.append((tool_name, "FAILED", output))
                
        except Exception as e:
            print(f'   ❌ ERROR - {str(e)}')
            self.failed_tests += 1
            self.test_results.append((tool_name, "ERROR", str(e)))

    async def test_all_tools(self):
        """Test all MCP tools individually"""
        print('🔍 INDIVIDUAL MCP TOOL TESTING')
        print('=' * 60)
        
        server_params = StdioServerParameters(
            command='python3',
            args=['mcp_server.py'],
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print('✅ MCP Session initialized\n')
                
                # Test 1: Server Info Tool
                await self.run_tool_test(
                    session, 'get_server_info', {},
                    ['campaign ai', 'server', 'tools'],
                    'Get basic server information'
                )
                
                # Test 2: Connection Test Tool
                await self.run_tool_test(
                    session, 'test_connection', {},
                    ['connection successful', 'operational'],
                    'Test server connection'
                )
                
                # Test 3: List Campaigns by Criteria
                await self.run_tool_test(
                    session, 'mcp_list_campaigns_by_criteria', 
                    {'platform': 'facebook', 'limit': 3},
                    ['found', 'campaigns', 'facebook', 'budget', 'roas'],
                    'List Facebook campaigns with criteria'
                )
                
                # Test 4: Search Campaign Data
                await self.run_tool_test(
                    session, 'mcp_search_campaign_data',
                    {'query': 'AI', 'limit': 2},
                    ['found', 'campaigns', 'ai', 'budget'],
                    'Search for AI-related campaigns'
                )
                
                # Test 5: Get Facebook Campaigns
                await self.run_tool_test(
                    session, 'mcp_get_facebook_campaigns',
                    {'limit': 2},
                    ['facebook', 'campaigns', 'platform'],
                    'Get Facebook campaigns via API'
                )
                
                # Test 6: Get Instagram Campaigns
                await self.run_tool_test(
                    session, 'mcp_get_instagram_campaigns',
                    {'limit': 2},
                    ['instagram', 'campaigns', 'platform'],
                    'Get Instagram campaigns via API'
                )
                
                # Test 7: Analyze Campaign Performance (AI Tool)
                await self.run_tool_test(
                    session, 'mcp_analyze_campaign_performance',
                    {'campaign_data': 'Campaign: Test AI Campaign, Budget: R5000, Spend: R2500, ROAS: 3.2x, CTR: 4.5%, Platform: Facebook'},
                    ['analysis', 'campaign', 'performance', 'budget', 'roas'],
                    'AI analysis of campaign performance'
                )
                
                # Test 8: Generate Campaign Content (AI Tool) - Fixed parameters
                await self.run_tool_test(
                    session, 'mcp_generate_campaign_content',
                    {'campaign_type': 'ad_copy', 'target_audience': 'young professionals', 'platform': 'facebook', 'campaign_objective': 'conversions'},
                    ['campaign', 'content', 'young professionals', 'facebook'],
                    'AI generation of campaign content'
                )
                
                # Test 9: Optimize Campaign Strategy (AI Tool) - Fixed parameters and criteria
                await self.run_tool_test(
                    session, 'mcp_optimize_campaign_strategy',
                    {'campaign_data': 'Low performing campaign with 1.2x ROAS', 'goals': 'increase ROAS to 3x'},
                    ['strategy optimization', 'audience', 'creative', 'performance'],
                    'AI optimization of campaign strategy'
                )
                
                # Test 10: General Marketing Assistant (AI Tool)
                await self.run_tool_test(
                    session, 'mcp_general_marketing_assistant',
                    {'query': 'What are the best practices for Facebook ad targeting?'},
                    ['facebook', 'targeting', 'best practices', 'marketing'],
                    'General marketing advice'
                )
                
                # Test 11: Analyze Campaign Trends - Fixed expected criteria
                await self.run_tool_test(
                    session, 'mcp_analyze_campaign_trends',
                    {'time_period': '30_days'},
                    ['trend analysis', 'performance', 'insights', 'recommendations'],
                    'Analyze campaign trends over time'
                )
                
                # Test 12: Create Campaign
                await self.run_tool_test(
                    session, 'mcp_create_campaign',
                    {
                        'name': 'Test Campaign Creation',
                        'platform': 'facebook',
                        'objective': 'conversions',
                        'budget_amount': 1000.0,
                        'budget_type': 'daily'
                    },
                    ['campaign', 'created', 'test campaign creation'],
                    'Create a new campaign'
                )
                
                # Test 13: Tavily Search
                await self.run_tool_test(
                    session, 'mcp_tavily_search',
                    {'query': 'digital marketing trends 2024'},
                    ['marketing', 'trends', '2024'],
                    'Web search using Tavily'
                )
                
                # Test 14: Wikipedia Search
                await self.run_tool_test(
                    session, 'mcp_wikipedia_search',
                    {'query': 'digital marketing'},
                    ['digital marketing', 'wikipedia'],
                    'Wikipedia search for digital marketing'
                )
                
                # Print final summary
                self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print('\n' + '=' * 60)
        print('📊 FINAL TEST SUMMARY')
        print('=' * 60)
        
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f'Total Tests: {total_tests}')
        print(f'✅ Passed: {self.passed_tests}')
        print(f'❌ Failed: {self.failed_tests}')
        print(f'📈 Success Rate: {success_rate:.1f}%')
        
        if self.failed_tests > 0:
            print('\n❌ FAILED TESTS:')
            for tool_name, status, output in self.test_results:
                if status != "PASSED":
                    print(f'   - {tool_name}: {status}')
                    if len(output) < 200:
                        print(f'     Output: {output}')
        
        print('\n🎯 VERDICT:')
        if self.failed_tests == 0:
            print('🎉 ALL TOOLS WORKING PERFECTLY!')
        elif self.failed_tests <= 2:
            print('⚠️ MOSTLY WORKING - Few tools need attention')
        else:
            print('❌ MULTIPLE TOOLS FAILING - Needs investigation')

async def main():
    tester = MCPToolTester()
    await tester.test_all_tools()

if __name__ == "__main__":
    asyncio.run(main()) 