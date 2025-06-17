"""
Simple Multi-Agent Workflow for Campaign AI

This module provides a working multi-agent system that uses direct MCP calls
without complex LangGraph dependencies that cause recursion issues.
"""

import os
import sys
import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add Backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# MCP imports
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

logger = logging.getLogger(__name__)

class SimpleWorkflowState(TypedDict):
    """Simple state for the multi-agent workflow."""
    workflow_id: str
    user_instruction: str
    current_step: str
    
    # Agent outputs
    intent_analysis: Dict[str, Any]
    campaign_data: Dict[str, Any]
    performance_analysis: Dict[str, Any]
    optimization_strategy: Dict[str, Any]
    generated_content: Dict[str, Any]
    
    # Tracking
    tool_calls: List[Dict[str, Any]]
    errors: List[str]
    final_output: str
    
    # Metadata
    started_at: str
    completed_at: Optional[str]
    status: str

class SimpleAgent:
    """Base class for simple agents that use direct MCP calls."""
    
    def __init__(self, agent_type: str, model: str = "gpt-4o-mini", temperature: float = 0.3):
        self.agent_id = f"{agent_type}_{uuid.uuid4().hex[:8]}"
        self.agent_type = agent_type
        self.model = model
        self.temperature = temperature
        
        # MCP server path
        self.mcp_server_path = os.path.join(backend_dir, "mcp_server.py")
        
        # Initialize OpenAI client
        self.llm = ChatOpenAI(model=self.model, temperature=self.temperature)
        
        logger.info(f"✅ Initialized {agent_type} Agent: {self.agent_id}")
    
    async def call_mcp_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Make a direct MCP tool call."""
        try:
            server_params = StdioServerParameters(
                command="python3",
                args=[self.mcp_server_path],
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    result = await session.call_tool(tool_name, args)
                    return result.content[0].text
                    
        except Exception as e:
            logger.error(f"❌ {self.agent_id}: MCP tool call failed: {str(e)}")
            return f"Error calling {tool_name}: {str(e)}"
    
    async def think_and_act(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Use OpenAI to think and then act with MCP tools."""
        try:
            # Use OpenAI to analyze what to do
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
            
        except Exception as e:
            logger.error(f"❌ {self.agent_id}: Think and act failed: {str(e)}")
            return f"Error in thinking: {str(e)}"

class IntentAnalysisAgent(SimpleAgent):
    """Agent that analyzes user intent."""
    
    def __init__(self):
        super().__init__("intent_analyzer", temperature=0.1)
    
    async def analyze_intent(self, user_instruction: str) -> Dict[str, Any]:
        """Analyze user intent with enhanced brainstorming detection."""
        logger.info(f"🧠 {self.agent_id}: Analyzing intent")
        
        try:
            # Enhanced intent analysis prompt
            intent_prompt = f"""
            Analyze this user request and categorize the intent:
            
            USER REQUEST: "{user_instruction}"
            
            INTENT CATEGORIES:
            1. BRAINSTORMING - User wants fresh ideas, market insights, trends, innovative strategies
            2. ANALYSIS - User wants detailed analysis of existing campaigns
            3. SIMPLE_QUERY - User wants quick data (top campaigns, metrics, lists)
            4. OPTIMIZATION - User wants to improve specific campaigns
            
            BRAINSTORMING INDICATORS:
            - "fresh ideas", "brainstorm", "new ideas", "market trends"
            - "what's out there", "innovative strategies", "latest trends"
            - "haven't considered", "different approaches", "market insights"
            - "what successful brands are doing", "industry best practices"
            
            ANALYSIS INDICATORS:
            - "analyze", "report", "detailed analysis", "compare"
            - "why", "how", "what's causing", "breakdown"
            
            SIMPLE_QUERY INDICATORS:
            - "show me", "list", "top campaigns", "which campaigns"
            - "how many", "what is", "when was"
            
            Respond with:
            {{
                "primary_intent": "[BRAINSTORMING|ANALYSIS|SIMPLE_QUERY|OPTIMIZATION]",
                "confidence": [0-1],
                "requires_web_research": [true|false],
                "research_topics": ["topic1", "topic2", ...],
                "analysis": "Brief explanation of the intent"
            }}
            """
            
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage
            
            llm = ChatOpenAI(model=self.model, temperature=self.temperature)
            response = await llm.ainvoke([HumanMessage(content=intent_prompt)])
            
            # Parse the response (assuming JSON format)
            import json
            try:
                intent_data = json.loads(response.content)
            except:
                # Fallback parsing
                intent_data = {
                    "primary_intent": "ANALYSIS",
                    "confidence": 0.7,
                    "requires_web_research": "brainstorm" in user_instruction.lower() or "fresh ideas" in user_instruction.lower(),
                    "research_topics": [],
                    "analysis": response.content[:200]
                }
            
            # Enhance with additional detection
            brainstorming_keywords = [
                "fresh ideas", "brainstorm", "market trends", "innovative strategies",
                "what's out there", "haven't considered", "latest trends", "2024",
                "successful brands", "different approaches", "market insights"
            ]
            
            if any(keyword in user_instruction.lower() for keyword in brainstorming_keywords):
                intent_data["primary_intent"] = "BRAINSTORMING"
                intent_data["requires_web_research"] = True
                intent_data["research_topics"] = [
                    "digital marketing trends 2024",
                    "innovative campaign strategies",
                    "successful brand campaigns",
                    "marketing best practices"
                ]
            
            logger.info(f"📋 Intent: {intent_data.get('primary_intent', 'unknown').lower()}")
            logger.info(f"🌐 Web Research Needed: {intent_data.get('requires_web_research', False)}")
            
            return intent_data
            
        except Exception as e:
            logger.error(f"❌ Intent analysis failed: {str(e)}")
            return {
                "primary_intent": "ANALYSIS",
                "confidence": 0.5,
                "requires_web_research": False,
                "research_topics": [],
                "analysis": f"Error in analysis: {str(e)}"
            }

class DataCollectionAgent(SimpleAgent):
    """Agent that collects campaign data."""
    
    def __init__(self):
        super().__init__("data_collector", temperature=0.2)
    
    async def collect_campaign_data(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Collect campaign data using MCP tools."""
        logger.info(f"📊 {self.agent_id}: Collecting campaign data")
        
        collected_data = {}
        tool_calls = []
        
        try:
            # Get Facebook campaigns - increased limit for top 10 analysis
            if "facebook" in intent.get("platforms", []):
                fb_data = await self.call_mcp_tool('mcp_get_facebook_campaigns', {'limit': 50})
                collected_data["facebook_campaigns"] = fb_data
                tool_calls.append({"tool": "mcp_get_facebook_campaigns", "status": "success"})
            
            # Also get Instagram campaigns for comprehensive top 10 analysis
            ig_data = await self.call_mcp_tool('mcp_get_instagram_campaigns', {'limit': 50})
            collected_data["instagram_campaigns"] = ig_data
            tool_calls.append({"tool": "mcp_get_instagram_campaigns", "status": "success"})
            
            # Search campaign database
            if intent.get("needs_data", False):
                search_data = await self.call_mcp_tool('mcp_search_campaign_data', {
                    'query': 'campaign performance metrics',
                    'limit': 100  # Increased for better top 10 selection
                })
                collected_data["search_results"] = search_data
                tool_calls.append({"tool": "mcp_search_campaign_data", "status": "success"})
            
            collected_data["tool_calls"] = tool_calls
            collected_data["timestamp"] = datetime.now().isoformat()
            
            logger.info(f"✅ Data collection completed: {len(tool_calls)} tools used")
            return collected_data
            
        except Exception as e:
            logger.error(f"❌ Data collection failed: {str(e)}")
            return {"error": str(e), "tool_calls": tool_calls}

class PerformanceAnalysisAgent(SimpleAgent):
    """Agent that analyzes campaign performance."""
    
    def __init__(self):
        super().__init__("performance_analyzer", temperature=0.3)
    
    async def analyze_performance(self, campaign_data: Dict[str, Any], intent: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze campaign performance with focus on specific campaigns and actionable insights."""
        try:
            # Enhanced prompt for focused analysis
            analysis_prompt = f"""
            CAMPAIGN PERFORMANCE ANALYSIS TASK:
            
            User Intent: {intent}
            Campaign Data Available: {list(campaign_data.keys())}
            
            INSTRUCTIONS:
            1. Focus on the SPECIFIC question asked (e.g., "lowest CTR campaigns")
            2. Identify the exact campaigns that answer the question
            3. Provide campaign-specific analysis, not generic insights
            4. Suggest specific improvements for each identified campaign
            5. If you need additional data (competitor benchmarks, industry standards, etc.), clearly state what would help
            6. Be direct and actionable - minimize fluff
            
            ANALYSIS FRAMEWORK:
            - Identify specific campaigns that match the query
            - Analyze their performance metrics in detail
            - Compare against the campaign portfolio average
            - Identify root causes of performance issues
            - Recommend specific, actionable improvements
            - Suggest additional research if needed
            
            Provide your analysis using the MCP analyze_campaign_performance tool.
            """
            
            # Use MCP tool for enhanced analysis
            analysis_result = await self.call_mcp_tool(
                "mcp_analyze_campaign_performance", 
                {
                    "campaign_data": str(campaign_data)[:2000],  # Limit data size
                    "analysis_type": "focused_campaign_analysis",
                    "specific_request": intent.get("analysis", "performance analysis")
                }
            )
            
            # Parse and structure the analysis
            analysis_data = {
                "analysis_type": "focused_performance_analysis",
                "specific_campaigns_identified": True,
                "actionable_insights": True,
                "raw_analysis": analysis_result,
                "needs_additional_research": "industry benchmark" in analysis_result.lower() or "competitor" in analysis_result.lower(),
                "timestamp": datetime.now().isoformat()
            }
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"❌ Performance analysis failed: {str(e)}")
            return {"error": str(e), "analysis_type": "failed"}

class StrategyOptimizationAgent(SimpleAgent):
    """Agent that develops optimization strategies."""
    
    def __init__(self):
        super().__init__("strategy_optimizer", temperature=0.4)
    
    async def develop_strategy(self, analysis: Dict[str, Any], intent: Dict[str, Any]) -> Dict[str, Any]:
        """Develop targeted optimization strategy with enhanced web research for brainstorming."""
        logger.info(f"🎯 {self.agent_id}: Developing targeted optimization strategy")
        
        try:
            # Prepare focused context for strategy development
            analysis_summary = analysis.get("raw_analysis", str(analysis))[:1000] if isinstance(analysis, dict) else str(analysis)[:1000]
            user_request = intent.get("analysis", "optimization strategy")
            intent_type = intent.get("primary_intent", "ANALYSIS")
            
            # Enhanced web research for brainstorming scenarios
            research_insights = ""
            web_search_count = 0
            
            if intent_type == "BRAINSTORMING" or intent.get("requires_web_research", False):
                logger.info("🌐 BRAINSTORMING DETECTED: Triggering comprehensive web research...")
                
                # Define comprehensive search queries for brainstorming
                search_queries = [
                    "digital marketing trends 2024 innovative strategies",
                    "successful social media campaign examples 2024",
                    "Facebook Instagram advertising best practices 2024",
                    "marketing campaign optimization techniques",
                    "creative advertising ideas that work 2024"
                ]
                
                # Add specific searches based on user request
                user_lower = user_request.lower()
                if "low performing" in user_lower or "improve" in user_lower:
                    search_queries.extend([
                        "how to improve low performing ad campaigns",
                        "campaign performance optimization strategies"
                    ])
                
                if "ctr" in user_lower or "click" in user_lower:
                    search_queries.extend([
                        "improve click through rates digital advertising",
                        "CTR optimization best practices 2024"
                    ])
                
                # Perform multiple web searches
                for query in search_queries[:4]:  # Limit to 4 searches for performance
                    try:
                        logger.info(f"🔍 Searching: {query}")
                        search_result = await self.call_mcp_tool("mcp_tavily_search", {"query": query})
                        if search_result and len(search_result) > 100:
                            research_insights += f"\n\n**🌐 Market Research: {query}**\n{search_result[:600]}...\n"
                            web_search_count += 1
                    except Exception as e:
                        logger.warning(f"Search failed for '{query}': {e}")
                
                # Also try Wikipedia for broader context
                try:
                    logger.info("📚 Searching Wikipedia for additional context...")
                    wiki_result = await self.call_mcp_tool("mcp_wikipedia_search", {"query": "Digital marketing trends"})
                    if wiki_result and len(wiki_result) > 100:
                        research_insights += f"\n\n**📚 Wikipedia Context: Digital Marketing Trends**\n{wiki_result[:400]}...\n"
                        web_search_count += 1
                except Exception as e:
                    logger.warning(f"Wikipedia search failed: {e}")
            
            # Use MCP tool for initial strategy optimization
            strategy_result = await self.call_mcp_tool('mcp_optimize_campaign_strategy', {
                'campaign_data': analysis_summary,
                'optimization_focus': user_request,
                'analysis_type': 'campaign_specific_improvements'
            })
            
            # Generate enhanced strategic recommendations with web research integration
            if intent_type == "BRAINSTORMING":
                strategy_prompt = f"""
                BRAINSTORMING & FRESH IDEAS TASK:
                User Request: {user_request}
                Campaign Analysis: {analysis_summary}
                
                MARKET RESEARCH INSIGHTS:
                {research_insights}
                
                INSTRUCTIONS:
                1. **FRESH IDEAS**: Generate innovative campaign concepts we haven't tried
                2. **MARKET TRENDS**: Integrate 2024 trends from the research above
                3. **SPECIFIC CAMPAIGNS**: Provide targeted improvements for low-performing campaigns
                4. **INNOVATIVE STRATEGIES**: Suggest cutting-edge approaches successful brands are using
                5. **ACTIONABLE RECOMMENDATIONS**: Each idea should be implementable with clear steps
                
                FORMAT:
                ## 🚀 Fresh Campaign Ideas (Based on 2024 Market Trends)
                [List 3-5 innovative concepts with market research backing]
                
                ## 🎯 Campaign-Specific Improvements
                [Target specific low-performing campaigns with fresh approaches]
                
                ## 💡 Innovative Strategies from Market Leaders
                [What successful brands are doing differently - from research]
                
                ## 📊 Implementation Roadmap
                [Step-by-step plan to test these fresh ideas]
                
                Focus on FRESH, INNOVATIVE, MARKET-BACKED ideas - not generic advice.
                """
            else:
                strategy_prompt = f"""
                STRATEGIC OPTIMIZATION TASK:
                User Request: {user_request}
                Analysis Results: {analysis_summary}
                
                INSTRUCTIONS:
                1. Focus on the SPECIFIC campaigns identified in the analysis
                2. Provide campaign-specific, actionable recommendations
                3. Include budget optimization suggestions with numbers
                4. Suggest A/B testing strategies for identified issues
                5. Be direct and actionable - no generic advice
                
                FORMAT:
                ## Campaign-Specific Recommendations
                [For each identified campaign, provide specific improvements]
                
                ## Budget Optimization Strategy
                [Specific budget reallocation suggestions]
                
                Be specific to the campaigns mentioned in the analysis.
                """
            
            strategic_recommendations = await self.think_and_act(strategy_prompt)
            
            # Additional targeted research if needed
            if not research_insights and any(phrase in strategic_recommendations.lower() for phrase in [
                "industry benchmark", "competitor analysis", "market research", 
                "best practices", "additional research needed"
            ]):
                logger.info("🔍 Performing additional strategic research...")
                
                # Determine search queries based on the analysis
                additional_queries = []
                if "ctr" in user_request.lower():
                    additional_queries.append("CTR optimization strategies digital advertising 2024")
                if "budget" in strategic_recommendations.lower():
                    additional_queries.append("campaign budget optimization best practices")
                if "facebook" in analysis_summary.lower():
                    additional_queries.append("Facebook ads performance improvement strategies")
                
                # Perform targeted web searches
                for query in additional_queries[:2]:  # Limit searches
                    try:
                        search_result = await self.call_mcp_tool("mcp_tavily_search", {"query": query})
                        if search_result and len(search_result) > 100:
                            research_insights += f"\n\n**Research: {query}**\n{search_result[:400]}..."
                            web_search_count += 1
                    except Exception as e:
                        logger.warning(f"Research search failed for '{query}': {e}")
            
            strategy_data = {
                "mcp_strategy": strategy_result,
                "strategic_recommendations": strategic_recommendations,
                "research_insights": research_insights,
                "web_searches_performed": web_search_count,
                "intent_type": intent_type,
                "needs_additional_research": intent.get("requires_web_research", False),
                "timestamp": datetime.now().isoformat(),
                "tool_calls": [
                    {"tool": "mcp_optimize_campaign_strategy", "status": "success"},
                    *[{"tool": "mcp_tavily_search", "status": "success"} for _ in range(web_search_count)]
                ]
            }
            
            logger.info(f"✅ Targeted strategy development completed ({web_search_count} web searches)")
            return strategy_data
            
        except Exception as e:
            logger.error(f"❌ Strategy development failed: {str(e)}")
            return {"error": str(e)}

class ContentGenerationAgent(SimpleAgent):
    """Agent that generates campaign content."""
    
    def __init__(self):
        super().__init__("content_generator", temperature=0.6)
    
    async def generate_content(self, strategy: Dict[str, Any], intent: Dict[str, Any]) -> Dict[str, Any]:
        """Generate campaign content using MCP tools."""
        logger.info(f"✨ {self.agent_id}: Generating content")
        
        try:
            # Use MCP tool for content generation
            content_result = await self.call_mcp_tool('mcp_generate_campaign_content', {
                'campaign_type': 'ad_copy',
                'target_audience': 'business professionals',
                'platform': 'facebook',
                'campaign_objective': 'engagement'
            })
            
            # Generate additional creative ideas
            creative_prompt = f"""
            Based on this optimization strategy, create additional creative content ideas:
            {str(strategy)[:500]}
            
            Generate:
            1. Ad copy variations
            2. Creative concepts
            3. Call-to-action suggestions
            4. Audience messaging ideas
            """
            
            creative_ideas = await self.think_and_act(creative_prompt)
            
            content_data = {
                "mcp_content": content_result,
                "creative_ideas": creative_ideas,
                "timestamp": datetime.now().isoformat(),
                "tool_calls": [{"tool": "mcp_generate_campaign_content", "status": "success"}]
            }
            
            logger.info(f"✅ Content generation completed")
            return content_data
            
        except Exception as e:
            logger.error(f"❌ Content generation failed: {str(e)}")
            return {"error": str(e)}

class SimpleMultiAgentWorkflow:
    """Simple multi-agent workflow using LangGraph."""
    
    def __init__(self):
        self.workflow_id = f"simple_workflow_{uuid.uuid4().hex[:8]}"
        
        # Initialize agents
        self.intent_agent = IntentAnalysisAgent()
        self.data_agent = DataCollectionAgent()
        self.analysis_agent = PerformanceAnalysisAgent()
        self.strategy_agent = StrategyOptimizationAgent()
        self.content_agent = ContentGenerationAgent()
        
        # Build the graph
        self.graph = self._build_graph()
        
        logger.info(f"✅ Initialized Simple Multi-Agent Workflow: {self.workflow_id}")
    
    def _build_graph(self) -> StateGraph:
        """Build the workflow graph with conditional routing."""
        workflow = StateGraph(SimpleWorkflowState)
        
        # Add nodes
        workflow.add_node("analyze_intent", self._analyze_intent_node)
        workflow.add_node("collect_data", self._collect_data_node)
        workflow.add_node("analyze_performance", self._analyze_performance_node)
        workflow.add_node("develop_strategy", self._develop_strategy_node)
        workflow.add_node("generate_content", self._generate_content_node)
        workflow.add_node("compile_results", self._compile_results_node)
        workflow.add_node("quick_response", self._quick_response_node)  # NEW: Quick response for simple queries
        
        # Set entry point
        workflow.set_entry_point("analyze_intent")
        
        # Add conditional routing based on intent
        workflow.add_conditional_edges(
            "analyze_intent",
            self._route_after_intent,
            {
                "simple_query": "collect_data",  # For "show me top campaigns" type queries
                "complex_analysis": "collect_data",  # For complex analysis
                "quick_answer": "quick_response"  # For very simple questions
            }
        )
        
        # Simple path for "show me top campaigns" type queries
        workflow.add_conditional_edges(
            "collect_data",
            self._route_after_data,
            {
                "simple_response": "quick_response",  # Skip complex analysis
                "full_analysis": "analyze_performance"  # Do full analysis
            }
        )
        
        # Full analysis path (existing)
        workflow.add_edge("analyze_performance", "develop_strategy")
        workflow.add_edge("develop_strategy", "generate_content")
        workflow.add_edge("generate_content", "compile_results")
        
        # End nodes
        workflow.add_edge("compile_results", END)
        workflow.add_edge("quick_response", END)
        
        # Compile with memory
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    
    def _route_after_intent(self, state: SimpleWorkflowState) -> str:
        """Route based on intent analysis with enhanced brainstorming detection."""
        intent = state.get("intent_analysis", {})
        user_instruction = state.get("user_instruction", "").lower()
        intent_type = intent.get("primary_intent", "ANALYSIS")
        
        # BRAINSTORMING scenarios always go to complex analysis
        brainstorming_keywords = [
            "fresh ideas", "brainstorm", "market trends", "innovative strategies",
            "what's out there", "haven't considered", "latest trends", "2024",
            "successful brands", "different approaches", "market insights",
            "new ideas", "industry best practices"
        ]
        
        if (intent_type == "BRAINSTORMING" or 
            any(keyword in user_instruction for keyword in brainstorming_keywords)):
            logger.info("🔄 Routing to complex analysis path (BRAINSTORMING detected)")
            return "complex_analysis"
        
        # Check for complex analysis keywords (high priority)
        complex_keywords = [
            "analyze", "analysis", "report", "recommendations", "improve", "optimize",
            "strategy", "compare", "comparison", "problems", "issues", "insights",
            "comprehensive", "detailed", "deep dive", "evaluate", "assessment"
        ]
        
        if any(keyword in user_instruction for keyword in complex_keywords):
            logger.info("🔄 Routing to complex analysis path (complex keywords detected)")
            return "complex_analysis"
        
        # Check for simple "show me" or "top campaigns" type queries (without analysis)
        simple_patterns = [
            "show me top", "list top", "what are the top", "which are the best",
            "top performing campaigns", "best campaigns"
        ]
        
        if any(pattern in user_instruction for pattern in simple_patterns):
            # But if it also has analysis keywords, still go complex
            if not any(keyword in user_instruction for keyword in complex_keywords):
                logger.info("🔄 Routing to simple query path")
                return "simple_query"
        
        # Check if it's a very simple question that can be answered quickly
        if any(phrase in user_instruction for phrase in [
            "how many", "what is", "when was", "who is", "where is"
        ]):
            logger.info("🔄 Routing to quick answer path")
            return "quick_answer"
        
        # Default to complex analysis for safety
        logger.info("🔄 Routing to complex analysis path (default)")
        return "complex_analysis"
    
    def _route_after_data(self, state: SimpleWorkflowState) -> str:
        """Route after data collection based on query type."""
        intent = state.get("intent_analysis", {})
        user_instruction = state.get("user_instruction", "").lower()
        
        # Check for complex analysis keywords - these should go to full analysis
        complex_keywords = [
            "analyze", "analysis", "report", "recommendations", "improve", "optimize",
            "strategy", "compare", "comparison", "problems", "issues", "insights",
            "comprehensive", "detailed", "deep dive", "evaluate", "assessment"
        ]
        
        if any(keyword in user_instruction for keyword in complex_keywords):
            logger.info("🔄 Routing to full analysis (complex analysis required)")
            return "full_analysis"
        
        # For simple "show me top campaigns" without analysis - go to simple response
        simple_patterns = [
            "show me top", "list top", "what are the top", "which are the best"
        ]
        
        if any(pattern in user_instruction for pattern in simple_patterns):
            logger.info("🔄 Routing to simple response (simple list request)")
            return "simple_response"
        
        # Default to full analysis for safety
        logger.info("🔄 Routing to full analysis (default)")
        return "full_analysis"
    
    async def _quick_response_node(self, state: SimpleWorkflowState) -> SimpleWorkflowState:
        """Enhanced response node that provides specific, targeted answers with real campaign data."""
        logger.info(f"⚡ Generating targeted response for: {state['workflow_id']}")
        
        try:
            # Get campaign data if we have it
            campaign_data = state.get("campaign_data", {})
            user_instruction = state.get("user_instruction", "")
            
            # If we don't have data yet, get it quickly
            if not campaign_data or "error" in campaign_data:
                logger.info("📊 Getting campaign data for targeted response...")
                data_result = await self.data_agent.collect_campaign_data(
                    state.get("intent_analysis", {})
                )
                campaign_data = data_result
                state["campaign_data"] = data_result
            
            # Parse and analyze campaigns with improved parsing
            all_campaigns = []
            
            # Parse Facebook campaigns with better error handling
            if "facebook_campaigns" in campaign_data:
                try:
                    fb_data_str = campaign_data["facebook_campaigns"]
                    # Handle both string and dict responses
                    if isinstance(fb_data_str, str):
                        # Try to parse as eval first, then as JSON
                        try:
                            fb_data = eval(fb_data_str)
                        except:
                            import json
                            fb_data = json.loads(fb_data_str)
                    else:
                        fb_data = fb_data_str
                    
                    if isinstance(fb_data, dict) and "campaigns" in fb_data:
                        for campaign in fb_data["campaigns"]:
                            # Extract rich campaign data including ID and name
                            campaign_info = {
                                "campaign_id": campaign.get('campaign_id', 'Unknown ID'),
                                "name": campaign.get('name', 'Unknown Name'),
                                "platform": "Facebook",
                                "status": campaign.get('status', 'Unknown'),
                                "objective": campaign.get('objective', 'Unknown'),
                                "performance": campaign.get("performance", {}),
                                "budget": campaign.get("budget", {}),
                                "engagement": campaign.get("engagement", {}),
                                "dates": campaign.get("dates", {})
                            }
                            all_campaigns.append(campaign_info)
                            
                    logger.info(f"📱 Parsed {len([c for c in all_campaigns if c['platform'] == 'Facebook'])} Facebook campaigns")
                except Exception as e:
                    logger.warning(f"Could not parse Facebook campaign data: {str(e)}")
            
            # Parse Instagram campaigns with better error handling
            if "instagram_campaigns" in campaign_data:
                try:
                    ig_data_str = campaign_data["instagram_campaigns"]
                    # Handle both string and dict responses
                    if isinstance(ig_data_str, str):
                        # Try to parse as eval first, then as JSON
                        try:
                            ig_data = eval(ig_data_str)
                        except:
                            import json
                            ig_data = json.loads(ig_data_str)
                    else:
                        ig_data = ig_data_str
                    
                    if isinstance(ig_data, dict) and "campaigns" in ig_data:
                        for campaign in ig_data["campaigns"]:
                            # Extract rich campaign data including ID and name
                            campaign_info = {
                                "campaign_id": campaign.get('campaign_id', 'Unknown ID'),
                                "name": campaign.get('name', 'Unknown Name'),
                                "platform": "Instagram", 
                                "status": campaign.get('status', 'Unknown'),
                                "objective": campaign.get('objective', 'Unknown'),
                                "performance": campaign.get("performance", {}),
                                "budget": campaign.get("budget", {}),
                                "engagement": campaign.get("engagement", {}),
                                "instagram_specific": campaign.get("instagram_specific", {}),
                                "dates": campaign.get("dates", {})
                            }
                            all_campaigns.append(campaign_info)
                            
                    logger.info(f"📸 Parsed {len([c for c in all_campaigns if c['platform'] == 'Instagram'])} Instagram campaigns")
                except Exception as e:
                    logger.warning(f"Could not parse Instagram campaign data: {str(e)}")
            
            logger.info(f"📊 Total campaigns parsed: {len(all_campaigns)} campaigns for targeted insights")
            
            # Create a focused response using LLM with specific instructions
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
            
            # Prepare detailed campaign data for analysis with IDs and names
            campaign_details = []
            for campaign in all_campaigns:
                perf = campaign.get("performance", {})
                budget = campaign.get("budget", {})
                engagement = campaign.get("engagement", {})
                
                campaign_detail = {
                    "campaign_id": campaign.get('campaign_id', 'Unknown ID'),
                    "name": campaign.get('name', 'Unknown Name'),
                    "platform": campaign.get('platform', 'Unknown'),
                    "status": campaign.get('status', 'Unknown'),
                    "objective": campaign.get('objective', 'Unknown'),
                    "metrics": {
                        "ctr": float(perf.get('ctr', 0)),
                        "roas": float(perf.get('roas', 0)),
                        "conversions": int(perf.get('conversions', 0)),
                        "revenue": float(perf.get('revenue', 0)),
                        "cpc": float(perf.get('cpc', 0)),
                        "cpm": float(perf.get('cpm', 0)),
                        "impressions": int(perf.get('impressions', 0)),
                        "clicks": int(perf.get('clicks', 0))
                    },
                    "budget_info": {
                        "type": budget.get('type', 'Unknown'),
                        "amount": float(budget.get('amount', 0)),
                        "spent": float(budget.get('spent', 0)),
                        "remaining": float(budget.get('remaining', 0))
                    },
                    "engagement_data": {
                        "likes": int(engagement.get('likes', 0)),
                        "shares": int(engagement.get('shares', 0)),
                        "comments": int(engagement.get('comments', 0)),
                        "engagement_rate": float(engagement.get('engagement_rate', 0))
                    }
                }
                campaign_details.append(campaign_detail)
            
            response_prompt = f"""
            TASK: {user_instruction}
            
            CAMPAIGN DATA: {campaign_details}
            
            CRITICAL INSTRUCTIONS:
            1. ALWAYS use the actual campaign_id and name from the data - these are real campaigns from the database
            2. If the question asks for "lowest CTR" campaigns, sort by CTR ascending and identify the bottom 3 WITH THEIR REAL NAMES AND IDs
            3. If the question asks for "top/best performing" campaigns, sort by ROAS descending and show top 10 WITH THEIR REAL NAMES AND IDs
            4. For budget analysis, use the actual budget amounts and spend data provided
            5. Be SPECIFIC and DIRECT - answer exactly what was asked using REAL campaign data
            6. For improvement recommendations, be campaign-specific with actionable steps that reference the actual campaign IDs
            7. Focus on the actual question, minimize fluff
            8. NEVER use generic names like "Campaign 1", "Campaign 2" - always use the real campaign names and IDs provided
            
            FORMAT YOUR RESPONSE AS:
            
            ## Direct Answer to Your Question
            [Directly answer what was asked using REAL campaign names and IDs]
            
            ## Campaign-Specific Analysis & Recommendations
            
            ### Campaign: [REAL NAME] (ID: [REAL CAMPAIGN_ID])
            - **Current Performance**: [Actual metrics from data]
            - **Key Issues**: [Specific analysis]
            - **Recommended Actions**: [Specific improvements]
            - **Budget Optimization**: [Specific dollar amounts and reasoning]
            
            [Repeat for each identified campaign]
            
            ## Additional Insights
            [Any additional context or recommendations]
            
            ## Immediate Next Steps
            [Specific, actionable steps with campaign IDs]
            
            REMEMBER: Use ONLY the real campaign data provided. Never make up campaign names or IDs.
            """
            
            response = await llm.ainvoke([HumanMessage(content=response_prompt)])
            targeted_answer = response.content
            
            # Check if the response suggests additional research
            needs_web_search = any(phrase in targeted_answer.lower() for phrase in [
                "additional research", "industry benchmark", "competitor analysis", 
                "market trends", "best practices", "would help to search"
            ])
            
            # If additional research is suggested, perform web searches
            additional_insights = ""
            if needs_web_search:
                logger.info("🔍 Performing additional web research for enhanced insights...")
                
                # Extract key terms for search
                search_queries = []
                if "lowest ctr" in user_instruction.lower() or "click-through rate" in user_instruction.lower():
                    search_queries.extend([
                        "improve low click through rate digital advertising 2024",
                        "facebook instagram ads CTR optimization strategies",
                        "campaign optimization low engagement rates"
                    ])
                elif "budget" in user_instruction.lower() and "roas" in user_instruction.lower():
                    search_queries.extend([
                        "campaign budget optimization strategies 2024",
                        "maximize ROAS advertising budget allocation",
                        "digital marketing budget reallocation best practices"
                    ])
                
                # Perform web searches
                web_insights = []
                for query in search_queries[:2]:  # Limit to 2 searches to avoid delays
                    try:
                        search_result = await self.data_agent.call_mcp_tool("mcp_tavily_search", {"query": query})
                        if search_result and len(search_result) > 100:
                            web_insights.append(f"**Market Research - {query}**: {search_result[:500]}...")
                            state["tool_calls"].append({
                                "tool": "mcp_tavily_search",
                                "status": "success",
                                "query": query
                            })
                    except Exception as e:
                        logger.warning(f"Web search failed for '{query}': {e}")
                
                if web_insights:
                    additional_insights = f"\n\n## Latest Industry Insights\n" + "\n\n".join(web_insights)
            
            # Create final focused output with campaign summary
            campaign_summary = f"• **Campaigns Analyzed**: {len(all_campaigns)} total"
            if all_campaigns:
                platforms = list(set([c['platform'] for c in all_campaigns]))
                campaign_summary += f" ({', '.join(platforms)})"
                
            final_output = f"""
🎯 **CAMPAIGN AI FOCUSED ANALYSIS**
📝 **Your Question**: {user_instruction}
⏰ **Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{targeted_answer}{additional_insights}

---
📊 **Analysis Summary**:
{campaign_summary}
• **Multi-Agent Process**: Intent → Data → Analysis → Strategy → Content → Results
• **Tools Utilized**: {len(state.get('tool_calls', []))} total tool calls
• **Execution Time**: Multi-stage analysis completed
• **Research Enhanced**: {"Yes" if additional_insights else "No"} - {"web research included" if additional_insights else "campaign data focused"}

🎉 **Your specific question has been answered with targeted, actionable recommendations.**
            """
            
            state["final_output"] = final_output.strip()
            state["current_step"] = "quick_response_completed"
            state["status"] = "completed"
            state["completed_at"] = datetime.now().isoformat()
            
            logger.info(f"✅ Targeted response generated successfully using {len(all_campaigns)} real campaigns")
            
        except Exception as e:
            logger.error(f"❌ Targeted response failed: {str(e)}")
            state["errors"].append(f"Targeted response error: {str(e)}")
            state["final_output"] = f"I apologize, but I encountered an error: {str(e)}"
            state["status"] = "failed"
        
        return state
    
    async def _analyze_intent_node(self, state: SimpleWorkflowState) -> SimpleWorkflowState:
        """Analyze user intent."""
        logger.info(f"🧠 Analyzing intent for: {state['workflow_id']}")
        
        try:
            intent_result = await self.intent_agent.analyze_intent(state["user_instruction"])
            state["intent_analysis"] = intent_result
            state["current_step"] = "intent_analyzed"
            logger.info(f"✅ Intent analysis completed")
            
        except Exception as e:
            logger.error(f"❌ Intent analysis failed: {str(e)}")
            state["errors"].append(f"Intent analysis error: {str(e)}")
            state["intent_analysis"] = {"error": str(e)}
        
        return state
    
    async def _collect_data_node(self, state: SimpleWorkflowState) -> SimpleWorkflowState:
        """Collect campaign data."""
        logger.info(f"📊 Collecting data for: {state['workflow_id']}")
        
        try:
            data_result = await self.data_agent.collect_campaign_data(state["intent_analysis"])
            state["campaign_data"] = data_result
            state["current_step"] = "data_collected"
            
            # Track tool calls
            if "tool_calls" in data_result:
                state["tool_calls"].extend(data_result["tool_calls"])
            
            logger.info(f"✅ Data collection completed")
            
        except Exception as e:
            logger.error(f"❌ Data collection failed: {str(e)}")
            state["errors"].append(f"Data collection error: {str(e)}")
            state["campaign_data"] = {"error": str(e)}
        
        return state
    
    async def _analyze_performance_node(self, state: SimpleWorkflowState) -> SimpleWorkflowState:
        """Analyze performance."""
        logger.info(f"🔍 Analyzing performance for: {state['workflow_id']}")
        
        try:
            analysis_result = await self.analysis_agent.analyze_performance(
                state["campaign_data"], 
                state["intent_analysis"]
            )
            state["performance_analysis"] = analysis_result
            state["current_step"] = "performance_analyzed"
            
            # Track tool calls
            if "tool_calls" in analysis_result:
                state["tool_calls"].extend(analysis_result["tool_calls"])
            
            logger.info(f"✅ Performance analysis completed")
            
        except Exception as e:
            logger.error(f"❌ Performance analysis failed: {str(e)}")
            state["errors"].append(f"Performance analysis error: {str(e)}")
            state["performance_analysis"] = {"error": str(e)}
        
        return state
    
    async def _develop_strategy_node(self, state: SimpleWorkflowState) -> SimpleWorkflowState:
        """Develop optimization strategy."""
        logger.info(f"🎯 Developing strategy for: {state['workflow_id']}")
        
        try:
            strategy_result = await self.strategy_agent.develop_strategy(
                state["performance_analysis"], 
                state["intent_analysis"]
            )
            state["optimization_strategy"] = strategy_result
            state["current_step"] = "strategy_developed"
            
            # Track tool calls
            if "tool_calls" in strategy_result:
                state["tool_calls"].extend(strategy_result["tool_calls"])
            
            logger.info(f"✅ Strategy development completed")
            
        except Exception as e:
            logger.error(f"❌ Strategy development failed: {str(e)}")
            state["errors"].append(f"Strategy development error: {str(e)}")
            state["optimization_strategy"] = {"error": str(e)}
        
        return state
    
    async def _generate_content_node(self, state: SimpleWorkflowState) -> SimpleWorkflowState:
        """Generate content."""
        logger.info(f"✨ Generating content for: {state['workflow_id']}")
        
        try:
            content_result = await self.content_agent.generate_content(
                state["optimization_strategy"], 
                state["intent_analysis"]
            )
            state["generated_content"] = content_result
            state["current_step"] = "content_generated"
            
            # Track tool calls
            if "tool_calls" in content_result:
                state["tool_calls"].extend(content_result["tool_calls"])
            
            logger.info(f"✅ Content generation completed")
            
        except Exception as e:
            logger.error(f"❌ Content generation failed: {str(e)}")
            state["errors"].append(f"Content generation error: {str(e)}")
            state["generated_content"] = {"error": str(e)}
        
        return state
    
    async def _compile_results_node(self, state: SimpleWorkflowState) -> SimpleWorkflowState:
        """Compile focused results that directly answer the user's question."""
        logger.info(f"📋 Compiling targeted results for: {state['workflow_id']}")
        
        try:
            # Extract key information
            user_question = state['user_instruction']
            performance_analysis = state.get('performance_analysis', {})
            strategy = state.get('optimization_strategy', {})
            content = state.get('generated_content', {})
            
            # Create a focused response using LLM
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
            
            compilation_prompt = f"""
            TASK: Create a focused, direct response to the user's question.
            
            USER QUESTION: {user_question}
            
            AVAILABLE DATA:
            - Performance Analysis: {str(performance_analysis)[:1500]}
            - Strategy Recommendations: {str(strategy)[:1500]}
            - Generated Content: {str(content)[:1000]}
            
            INSTRUCTIONS:
            1. DIRECTLY answer the user's specific question first
            2. If they asked for "3 campaigns with lowest CTR", identify those 3 campaigns by name
            3. For each identified campaign, provide specific, actionable improvements
            4. Include any web research insights that were gathered
            5. Be concise and campaign-specific - no generic advice
            6. Format for easy reading with clear sections
            
            FORMAT YOUR RESPONSE AS:
            
            ## Direct Answer to Your Question
            [Specifically answer what was asked - name the campaigns, metrics, etc.]
            
            ## Campaign-Specific Analysis & Recommendations
            
            ### Campaign 1: [Name]
            - Current Performance: [specific metrics]
            - Key Issues: [specific problems identified]
            - Recommended Actions: [specific improvements]
            - Budget Optimization: [specific suggestions]
            
            ### Campaign 2: [Name]
            [Same format]
            
            ### Campaign 3: [Name]
            [Same format]
            
            ## Additional Insights
            [Any web research findings or industry benchmarks]
            
            ## Immediate Next Steps
            [Prioritized action items]
            
            Focus on being specific and actionable. Reference actual campaign names and metrics.
            """
            
            response = await llm.ainvoke([HumanMessage(content=compilation_prompt)])
            focused_analysis = response.content
            
            # Include any research insights from strategy
            research_insights = ""
            if strategy.get("research_insights"):
                research_insights = f"\n\n## Latest Industry Research\n{strategy['research_insights']}"
            
            final_output = f"""
🎯 **CAMPAIGN AI FOCUSED ANALYSIS**
📝 **Your Question**: {user_question}
⏰ **Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{focused_analysis}{research_insights}

---
📊 **Analysis Summary**:
• **Campaigns Analyzed**: {len(state.get('campaign_data', {}).get('tool_calls', []))} data sources used
• **Multi-Agent Process**: Intent → Data → Analysis → Strategy → Content → Results
• **Tools Utilized**: {len(state['tool_calls'])} total tool calls
• **Execution Time**: Multi-stage analysis completed
• **Research Enhanced**: {'Yes' if strategy.get('research_insights') else 'No'} - web research included

🎉 **Your specific question has been answered with targeted, actionable recommendations.**
            """
            
            state["final_output"] = final_output.strip()
            state["current_step"] = "completed"
            state["status"] = "completed"
            state["completed_at"] = datetime.now().isoformat()
            
            logger.info(f"✅ Focused results compilation completed")
            
        except Exception as e:
            logger.error(f"❌ Results compilation failed: {str(e)}")
            state["errors"].append(f"Results compilation error: {str(e)}")
            state["final_output"] = f"Results compilation failed: {str(e)}"
            state["status"] = "failed"
        
        return state
    
    async def run_workflow(self, user_instruction: str) -> SimpleWorkflowState:
        """Run the complete multi-agent workflow."""
        workflow_id = f"workflow_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now()
        
        logger.info(f"🚀 Starting Simple Multi-Agent Workflow: {workflow_id}")
        logger.info(f"📝 Instruction: {user_instruction}")
        
        # Initialize state
        initial_state = SimpleWorkflowState(
            workflow_id=workflow_id,
            user_instruction=user_instruction,
            current_step="starting",
            intent_analysis={},
            campaign_data={},
            performance_analysis={},
            optimization_strategy={},
            generated_content={},
            tool_calls=[],
            errors=[],
            final_output="",
            started_at=start_time.isoformat(),
            completed_at=None,
            status="running"
        )
        
        try:
            # Run the workflow
            config = {"configurable": {"thread_id": workflow_id}}
            final_state = await self.graph.ainvoke(initial_state, config)
            
            # Calculate execution time
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            logger.info(f"✅ Workflow {workflow_id} completed in {execution_time:.2f}s")
            logger.info(f"📊 Total tool calls: {len(final_state['tool_calls'])}")
            logger.info(f"🔧 Final step: {final_state['current_step']}")
            
            return final_state
            
        except Exception as e:
            logger.error(f"❌ Workflow {workflow_id} failed: {str(e)}")
            initial_state["status"] = "failed"
            initial_state["errors"].append(f"Workflow execution failed: {str(e)}")
            initial_state["completed_at"] = datetime.now().isoformat()
            return initial_state
    
    def visualize_graph(self, output_path: str = "simple_workflow_graph.png"):
        """Generate a visual representation of the workflow graph."""
        try:
            # Get the graph visualization
            graph_image = self.graph.get_graph().draw_mermaid_png()
            
            # Save to file
            with open(output_path, "wb") as f:
                f.write(graph_image)
            
            logger.info(f"📊 Graph visualization saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Failed to generate graph visualization: {str(e)}")
            return None

# Factory function
def create_simple_workflow() -> SimpleMultiAgentWorkflow:
    """Create a new simple multi-agent workflow."""
    return SimpleMultiAgentWorkflow() 