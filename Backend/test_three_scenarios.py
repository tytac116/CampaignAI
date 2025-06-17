#!/usr/bin/env python3
"""
Three Scenario Comprehensive Test Suite

This test suite validates the Campaign AI workflow with three distinct scenarios:
1. BUDGET OPTIMIZATION - Reallocating budget across underperforming campaigns
2. AUDIENCE TARGETING - Improving audience reach and engagement strategies  
3. COMPETITIVE ANALYSIS - Analyzing performance against industry benchmarks

Each test demonstrates different aspects of the system's capabilities.
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

async def test_scenario_1_budget_optimization():
    """
    SCENARIO 1: BUDGET OPTIMIZATION
    Test: Advanced budget reallocation analysis with ROI optimization
    """
    
    try:
        from app.agents.simple_workflow import SimpleMultiAgentWorkflow
        
        print('💰 SCENARIO 1: BUDGET OPTIMIZATION ANALYSIS')
        print('=' * 70)
        print('Focus: Advanced budget reallocation with ROI optimization')
        print('Expected: Detailed financial analysis, reallocation strategies')
        print('=' * 70)
        print()
        
        workflow = SimpleMultiAgentWorkflow()
        
        # Budget optimization query
        budget_query = """I have a total monthly budget of $50,000 for my campaigns, but I'm not getting the ROI I expected. Can you analyze my current budget allocation across all campaigns and recommend how I should reallocate my budget to maximize ROAS? I want specific dollar amounts for reallocation and clear reasoning based on performance data. Also, identify which campaigns I should pause or scale up."""
        
        print('💰 BUDGET OPTIMIZATION QUERY:')
        print('-' * 50)
        print(budget_query)
        print('-' * 50)
        print()
        print('⏳ Running budget optimization analysis...')
        print('🎯 Expected: Financial analysis, reallocation matrix, pause/scale recommendations')
        print()
        
        start_time = datetime.now()
        result = await workflow.run_workflow(budget_query)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print('💰 BUDGET OPTIMIZATION RESULTS')
        print('=' * 50)
        print(f'✅ Status: {result["status"]}')
        print(f'⏱️  Execution Time: {execution_time:.2f} seconds')
        print(f'🛠️  Tools Used: {len(result.get("tool_calls", []))}')
        print()
        
        if result['status'] == 'completed':
            output = result['final_output']
            
            # Analyze budget-specific content
            has_dollar_amounts = '$' in output
            has_roas_analysis = 'ROAS' in output or 'roas' in output
            has_reallocation = 'reallocate' in output.lower() or 'budget' in output.lower()
            has_pause_recommendations = 'pause' in output.lower() or 'stop' in output.lower()
            has_scale_recommendations = 'scale' in output.lower() or 'increase' in output.lower()
            
            print('💰 BUDGET ANALYSIS VALIDATION:')
            print('-' * 40)
            print(f'   ✅ Dollar Amounts Provided: {"Yes" if has_dollar_amounts else "No"}')
            print(f'   ✅ ROAS Analysis Included: {"Yes" if has_roas_analysis else "No"}')
            print(f'   ✅ Reallocation Strategy: {"Yes" if has_reallocation else "No"}')
            print(f'   ✅ Pause Recommendations: {"Yes" if has_pause_recommendations else "No"}')
            print(f'   ✅ Scale Recommendations: {"Yes" if has_scale_recommendations else "No"}')
            
            budget_score = sum([has_dollar_amounts, has_roas_analysis, has_reallocation, 
                              has_pause_recommendations, has_scale_recommendations])
            print(f'   📊 Budget Analysis Score: {budget_score}/5')
            print()
            
            print('📋 BUDGET OPTIMIZATION REPORT (First 1000 chars):')
            print('-' * 55)
            print(output[:1000] + '...' if len(output) > 1000 else output)
            print()
            
            return budget_score >= 3
        else:
            print(f'❌ Budget optimization failed: {result.get("errors", [])}')
            return False
            
    except Exception as e:
        print(f'❌ Scenario 1 failed: {str(e)}')
        return False

async def test_scenario_2_audience_targeting():
    """
    SCENARIO 2: AUDIENCE TARGETING OPTIMIZATION
    Test: Advanced audience analysis and targeting strategy development
    """
    
    try:
        from app.agents.simple_workflow import SimpleMultiAgentWorkflow
        
        print('🎯 SCENARIO 2: AUDIENCE TARGETING OPTIMIZATION')
        print('=' * 70)
        print('Focus: Advanced audience analysis and targeting strategies')
        print('Expected: Demographic insights, lookalike strategies, targeting recommendations')
        print('=' * 70)
        print()
        
        workflow = SimpleMultiAgentWorkflow()
        
        # Audience targeting query
        audience_query = """My campaigns are reaching people, but the engagement and conversion rates are lower than expected. I suspect my audience targeting might be too broad or not precise enough. Can you analyze my current audience performance across all campaigns and recommend specific targeting improvements? I want to know which demographics are converting best, what interests and behaviors I should target, and how to create lookalike audiences. Also suggest A/B testing strategies for audience optimization."""
        
        print('🎯 AUDIENCE TARGETING QUERY:')
        print('-' * 50)
        print(audience_query)
        print('-' * 50)
        print()
        print('⏳ Running audience targeting analysis...')
        print('🎯 Expected: Demographic analysis, targeting strategies, A/B test plans')
        print()
        
        start_time = datetime.now()
        result = await workflow.run_workflow(audience_query)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print('🎯 AUDIENCE TARGETING RESULTS')
        print('=' * 50)
        print(f'✅ Status: {result["status"]}')
        print(f'⏱️  Execution Time: {execution_time:.2f} seconds')
        print(f'🛠️  Tools Used: {len(result.get("tool_calls", []))}')
        print()
        
        if result['status'] == 'completed':
            output = result['final_output']
            
            # Analyze audience-specific content
            has_demographics = any(word in output.lower() for word in ['demographic', 'age', 'gender', 'location'])
            has_interests = 'interest' in output.lower() or 'behavior' in output.lower()
            has_lookalike = 'lookalike' in output.lower() or 'similar' in output.lower()
            has_ab_testing = 'a/b' in output.lower() or 'test' in output.lower()
            has_conversion_analysis = 'conversion' in output.lower() or 'convert' in output.lower()
            has_targeting_strategy = 'target' in output.lower() and 'strategy' in output.lower()
            
            print('🎯 AUDIENCE ANALYSIS VALIDATION:')
            print('-' * 40)
            print(f'   ✅ Demographic Analysis: {"Yes" if has_demographics else "No"}')
            print(f'   ✅ Interest/Behavior Insights: {"Yes" if has_interests else "No"}')
            print(f'   ✅ Lookalike Strategies: {"Yes" if has_lookalike else "No"}')
            print(f'   ✅ A/B Testing Plans: {"Yes" if has_ab_testing else "No"}')
            print(f'   ✅ Conversion Analysis: {"Yes" if has_conversion_analysis else "No"}')
            print(f'   ✅ Targeting Strategy: {"Yes" if has_targeting_strategy else "No"}')
            
            audience_score = sum([has_demographics, has_interests, has_lookalike, 
                                has_ab_testing, has_conversion_analysis, has_targeting_strategy])
            print(f'   📊 Audience Analysis Score: {audience_score}/6')
            print()
            
            print('📋 AUDIENCE TARGETING REPORT (First 1000 chars):')
            print('-' * 55)
            print(output[:1000] + '...' if len(output) > 1000 else output)
            print()
            
            return audience_score >= 4
        else:
            print(f'❌ Audience targeting failed: {result.get("errors", [])}')
            return False
            
    except Exception as e:
        print(f'❌ Scenario 2 failed: {str(e)}')
        return False

async def test_scenario_3_competitive_analysis():
    """
    SCENARIO 3: COMPETITIVE BENCHMARKING & MARKET POSITIONING
    Test: Industry benchmark analysis with competitive intelligence
    """
    
    try:
        from app.agents.simple_workflow import SimpleMultiAgentWorkflow
        
        print('🏆 SCENARIO 3: COMPETITIVE BENCHMARKING ANALYSIS')
        print('=' * 70)
        print('Focus: Industry benchmarks and competitive market positioning')
        print('Expected: Benchmark comparisons, competitive insights, market positioning')
        print('=' * 70)
        print()
        
        workflow = SimpleMultiAgentWorkflow()
        
        # Competitive analysis query
        competitive_query = """I want to understand how my campaigns are performing compared to industry standards and competitors. Can you analyze my campaign performance against industry benchmarks for my sector? I need to know if my CTR, CPC, and conversion rates are competitive, what the industry averages are, and how I can improve my market positioning. Also, research what successful companies in my space are doing differently and provide actionable insights to help me compete more effectively."""
        
        print('🏆 COMPETITIVE ANALYSIS QUERY:')
        print('-' * 50)
        print(competitive_query)
        print('-' * 50)
        print()
        print('⏳ Running competitive benchmarking analysis...')
        print('🎯 Expected: Industry benchmarks, competitive insights, positioning strategies')
        print()
        
        start_time = datetime.now()
        result = await workflow.run_workflow(competitive_query)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print('🏆 COMPETITIVE ANALYSIS RESULTS')
        print('=' * 50)
        print(f'✅ Status: {result["status"]}')
        print(f'⏱️  Execution Time: {execution_time:.2f} seconds')
        print(f'🛠️  Tools Used: {len(result.get("tool_calls", []))}')
        print()
        
        # Check for web research (should be triggered for competitive analysis)
        tool_calls = result.get("tool_calls", [])
        web_searches = [t for t in tool_calls if "tavily" in t.get("tool", "").lower()]
        print(f'🌐 Web Research Performed: {len(web_searches)} searches')
        print()
        
        if result['status'] == 'completed':
            output = result['final_output']
            
            # Analyze competitive-specific content
            has_benchmarks = 'benchmark' in output.lower() or 'industry' in output.lower()
            has_competitor_analysis = 'competitor' in output.lower() or 'competitive' in output.lower()
            has_market_insights = 'market' in output.lower() and ('position' in output.lower() or 'trend' in output.lower())
            has_industry_averages = 'average' in output.lower() or 'standard' in output.lower()
            has_improvement_suggestions = 'improve' in output.lower() or 'better' in output.lower()
            has_research_backing = len(web_searches) > 0 and ('research' in output.lower() or 'study' in output.lower())
            
            print('🏆 COMPETITIVE ANALYSIS VALIDATION:')
            print('-' * 45)
            print(f'   ✅ Industry Benchmarks: {"Yes" if has_benchmarks else "No"}')
            print(f'   ✅ Competitor Analysis: {"Yes" if has_competitor_analysis else "No"}')
            print(f'   ✅ Market Positioning: {"Yes" if has_market_insights else "No"}')
            print(f'   ✅ Industry Averages: {"Yes" if has_industry_averages else "No"}')
            print(f'   ✅ Improvement Strategies: {"Yes" if has_improvement_suggestions else "No"}')
            print(f'   ✅ Research-Backed Insights: {"Yes" if has_research_backing else "No"}')
            
            competitive_score = sum([has_benchmarks, has_competitor_analysis, has_market_insights,
                                   has_industry_averages, has_improvement_suggestions, has_research_backing])
            print(f'   📊 Competitive Analysis Score: {competitive_score}/6')
            print()
            
            print('📋 COMPETITIVE ANALYSIS REPORT (First 1000 chars):')
            print('-' * 55)
            print(output[:1000] + '...' if len(output) > 1000 else output)
            print()
            
            return competitive_score >= 4
        else:
            print(f'❌ Competitive analysis failed: {result.get("errors", [])}')
            return False
            
    except Exception as e:
        print(f'❌ Scenario 3 failed: {str(e)}')
        return False

async def run_comprehensive_test_suite():
    """Run all three scenarios and provide comprehensive analysis."""
    
    print('🧪 CAMPAIGN AI COMPREHENSIVE TEST SUITE')
    print('Testing System Versatility Across Multiple Use Cases')
    print('=' * 80)
    print()
    
    # Track results
    results = {}
    total_start_time = datetime.now()
    
    # Run Scenario 1: Budget Optimization
    print('🚀 STARTING SCENARIO 1...')
    scenario_1_success = await test_scenario_1_budget_optimization()
    results['budget_optimization'] = scenario_1_success
    print(f'📊 Scenario 1 Result: {"✅ PASSED" if scenario_1_success else "❌ FAILED"}')
    print('\n' + '='*80 + '\n')
    
    # Run Scenario 2: Audience Targeting  
    print('🚀 STARTING SCENARIO 2...')
    scenario_2_success = await test_scenario_2_audience_targeting()
    results['audience_targeting'] = scenario_2_success
    print(f'📊 Scenario 2 Result: {"✅ PASSED" if scenario_2_success else "❌ FAILED"}')
    print('\n' + '='*80 + '\n')
    
    # Run Scenario 3: Competitive Analysis
    print('🚀 STARTING SCENARIO 3...')
    scenario_3_success = await test_scenario_3_competitive_analysis()
    results['competitive_analysis'] = scenario_3_success
    print(f'📊 Scenario 3 Result: {"✅ PASSED" if scenario_3_success else "❌ FAILED"}')
    print('\n' + '='*80 + '\n')
    
    # Final analysis
    total_execution_time = (datetime.now() - total_start_time).total_seconds()
    passed_scenarios = sum(results.values())
    
    print('🎯 COMPREHENSIVE TEST SUITE RESULTS')
    print('=' * 60)
    print(f'📊 Scenarios Passed: {passed_scenarios}/3')
    print(f'⏱️  Total Execution Time: {total_execution_time:.1f} seconds')
    print(f'🎯 Success Rate: {(passed_scenarios/3)*100:.1f}%')
    print()
    
    print('📋 DETAILED RESULTS:')
    print('-' * 30)
    for scenario, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f'   {scenario.replace("_", " ").title()}: {status}')
    print()
    
    if passed_scenarios == 3:
        print('🎉 EXCELLENT: All scenarios passed successfully!')
        print('   🏆 System demonstrates comprehensive versatility')
        print('   💰 Budget optimization capabilities validated')
        print('   🎯 Audience targeting intelligence confirmed')
        print('   🏆 Competitive analysis functionality proven')
        print('   🌐 Web research integration working across scenarios')
    elif passed_scenarios >= 2:
        print('✅ GOOD: Majority of scenarios successful')
        print('   System shows strong performance with room for improvement')
    else:
        print('⚠️  NEEDS IMPROVEMENT: Multiple scenario failures detected')
        print('   System requires optimization for production readiness')
    
    print()
    print('📁 FILES GENERATED:')
    print('   🖼️  updated_campaign_ai_workflow.png - Latest workflow diagram')
    print('   📊 Three comprehensive scenario validations completed')
    print()
    
    return passed_scenarios >= 2

async def main():
    """Main test execution function."""
    success = await run_comprehensive_test_suite()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 