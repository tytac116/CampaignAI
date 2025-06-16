#!/usr/bin/env python3
"""
Campaign Action Agent

This agent is responsible for:
1. Analyzing user intent (analysis vs action requests)
2. Coordinating with other agents for research and content generation
3. Making database changes to campaigns (create, update, pause, activate)
4. Routing requests appropriately within the multi-agent workflow

This agent demonstrates multi-agent coordination and intelligent decision making.
"""

import logging
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from ..core.config import get_settings
from .validation import get_hallucination_grader, get_enforcer_agent

logger = logging.getLogger(__name__)
settings = get_settings()

class CampaignActionAgent:
    """
    Campaign Action Agent for intelligent campaign management.
    
    This agent can:
    - Analyze user intent (analysis vs action)
    - Coordinate with other agents for research
    - Create and modify campaigns
    - Make intelligent decisions about workflow routing
    """
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.2):
        self.agent_id = f"action_agent_{uuid.uuid4().hex[:8]}"
        self.model = model
        self.temperature = temperature
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=2000,
            timeout=60
        )
        
        # MCP connection details
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.server_path = os.path.join(backend_dir, "mcp_server.py")
        self.mcp_tools = None
        self.mcp_agent = None
        
        # Validation tools
        self.hallucination_grader = get_hallucination_grader()
        self.enforcer_agent = get_enforcer_agent()
        
        logger.info(f"✅ Initialized Campaign Action Agent: {self.agent_id}")
        logger.info(f"🔧 Model: {model}, Temperature: {temperature}")
    
    async def initialize_mcp_connection(self) -> bool:
        """Initialize MCP connection and load tools."""
        try:
            if self.mcp_agent:
                return True  # Already initialized
                
            logger.info(f"🔗 {self.agent_id}: Connecting to MCP server...")
            
            # Create server parameters
            server_params = StdioServerParameters(
                command="python3",
                args=[self.server_path],
            )
            
            # Connect to MCP server and load tools
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Load MCP tools
                    self.mcp_tools = await load_mcp_tools(session)
                    logger.info(f"✅ {self.agent_id}: Loaded {len(self.mcp_tools)} MCP tools")
                    
                    # Log available tools
                    for tool in self.mcp_tools:
                        logger.info(f"   🛠️ {tool.name}: {tool.description[:50]}...")
                    
                    # Create LangGraph ReAct agent with MCP tools
                    self.mcp_agent = create_react_agent(self.llm, self.mcp_tools)
                    logger.info(f"✅ {self.agent_id}: MCP-integrated agent created")
                    
                    return True
                    
        except Exception as e:
            logger.error(f"❌ {self.agent_id}: MCP connection failed: {str(e)}")
            return False
    
    async def analyze_user_intent(self, user_instruction: str) -> Dict[str, Any]:
        """
        Analyze user instruction to determine intent and required actions.
        
        Args:
            user_instruction: Natural language instruction from user
            
        Returns:
            Intent analysis with action plan
        """
        try:
            logger.info(f"🧠 {self.agent_id}: Analyzing user intent...")
            
            intent_prompt = f"""
            You are an expert Campaign AI Intent Analyzer. Analyze the user's instruction and determine:
            
            1. INTENT TYPE:
               - "analysis": User wants information, reports, or insights (read-only)
               - "action": User wants to create, modify, or manage campaigns (write operations)
               - "hybrid": User wants both analysis and actions
            
            2. REQUIRED ACTIONS:
               - List specific actions needed
               - Identify which agents should be involved
               - Determine if campaign database changes are needed
            
            3. COORDINATION PLAN:
               - Which agents to call first
               - What information to gather
               - How to sequence the workflow
            
            User Instruction: "{user_instruction}"
            
            Respond with a JSON object containing:
            {{
                "intent_type": "analysis|action|hybrid",
                "confidence": 0.0-1.0,
                "requires_database_changes": true/false,
                "required_actions": ["action1", "action2", ...],
                "agents_needed": ["agent1", "agent2", ...],
                "coordination_plan": {{
                    "sequence": ["step1", "step2", ...],
                    "parallel_tasks": ["task1", "task2", ...],
                    "dependencies": {{"task": "depends_on"}}
                }},
                "reasoning": "explanation of the analysis"
            }}
            """
            
            response = await self.llm.ainvoke([HumanMessage(content=intent_prompt)])
            
            # Parse the JSON response
            try:
                intent_analysis = json.loads(response.content)
                logger.info(f"✅ Intent analysis: {intent_analysis['intent_type']} (confidence: {intent_analysis['confidence']})")
                return intent_analysis
            except json.JSONDecodeError:
                # Fallback analysis
                logger.warning("Failed to parse intent analysis JSON, using fallback")
                return self._fallback_intent_analysis(user_instruction)
                
        except Exception as e:
            logger.error(f"❌ Intent analysis failed: {str(e)}")
            return self._fallback_intent_analysis(user_instruction)
    
    def _fallback_intent_analysis(self, user_instruction: str) -> Dict[str, Any]:
        """Fallback intent analysis using keyword matching."""
        instruction_lower = user_instruction.lower()
        
        # Action keywords
        action_keywords = [
            'create', 'make', 'build', 'generate', 'add', 'new',
            'update', 'modify', 'change', 'edit', 'set',
            'pause', 'stop', 'activate', 'start', 'resume',
            'increase', 'decrease', 'allocate', 'budget'
        ]
        
        # Analysis keywords
        analysis_keywords = [
            'show', 'tell', 'what', 'how', 'analyze', 'report',
            'best', 'worst', 'performance', 'metrics', 'compare'
        ]
        
        action_score = sum(1 for keyword in action_keywords if keyword in instruction_lower)
        analysis_score = sum(1 for keyword in analysis_keywords if keyword in instruction_lower)
        
        if action_score > analysis_score:
            intent_type = "action"
        elif analysis_score > action_score:
            intent_type = "analysis"
        else:
            intent_type = "hybrid"
        
        return {
            "intent_type": intent_type,
            "confidence": 0.7,
            "requires_database_changes": action_score > 0,
            "required_actions": ["analyze_request", "execute_action"] if action_score > 0 else ["analyze_data"],
            "agents_needed": ["campaign_action_agent", "data_analysis_agent"],
            "coordination_plan": {
                "sequence": ["analyze", "execute"],
                "parallel_tasks": [],
                "dependencies": {}
            },
            "reasoning": f"Keyword analysis: {action_score} action keywords, {analysis_score} analysis keywords"
        }
    
    async def execute_action_workflow(self, 
                                    user_instruction: str,
                                    intent_analysis: Dict[str, Any],
                                    context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the action workflow based on intent analysis.
        
        Args:
            user_instruction: Original user instruction
            intent_analysis: Result from analyze_user_intent
            context: Additional context information
            
        Returns:
            Workflow execution results
        """
        workflow_id = f"action_workflow_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now()
        
        logger.info(f"🚀 {self.agent_id}: Starting action workflow: {workflow_id}")
        logger.info(f"📝 Intent: {intent_analysis['intent_type']}")
        
        try:
            # Ensure MCP connection
            if not await self.initialize_mcp_connection():
                raise Exception("Failed to establish MCP connection")
            
            # Check enforcer limits
            enforcer_result = self.enforcer_agent.should_continue(
                workflow_id,
                operation="action_workflow"
            )
            
            if not enforcer_result["should_continue"]:
                return {
                    "success": False,
                    "error": f"Enforcer blocked execution: {enforcer_result['reason']}",
                    "workflow_id": workflow_id
                }
            
            # Build comprehensive action prompt
            action_prompt = self._build_action_prompt(
                user_instruction, 
                intent_analysis, 
                context
            )
            
            # Execute via MCP agent
            messages = [HumanMessage(content=action_prompt)]
            response = await self.mcp_agent.ainvoke({"messages": messages})
            
            # Extract results
            final_message = response["messages"][-1]
            output = final_message.content if hasattr(final_message, 'content') else str(final_message)
            
            # Extract tool calls
            tool_calls = self._extract_tool_calls(response["messages"])
            
            # Validate output
            validation_result = self.hallucination_grader.grade_output(
                output,
                context=user_instruction,
                source_data=json.dumps(context or {})
            )
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "success": True,
                "workflow_id": workflow_id,
                "intent_type": intent_analysis["intent_type"],
                "output": output,
                "tool_calls": tool_calls,
                "execution_time_seconds": execution_time,
                "validation": {
                    "is_valid": not validation_result["is_hallucination"],
                    "confidence": validation_result["confidence"],
                    "reasoning": validation_result.get("reasoning", "")
                },
                "database_changes_made": len([tc for tc in tool_calls if self._is_database_tool(tc["name"])]) > 0
            }
            
            logger.info(f"✅ Action workflow completed: {workflow_id}")
            logger.info(f"📊 Tool calls: {len(tool_calls)}, DB changes: {result['database_changes_made']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Action workflow failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id,
                "execution_time_seconds": (datetime.now() - start_time).total_seconds()
            }
    
    def _build_action_prompt(self, 
                           user_instruction: str,
                           intent_analysis: Dict[str, Any],
                           context: Optional[Dict[str, Any]] = None) -> str:
        """Build comprehensive action prompt for MCP execution."""
        
        prompt = f"""You are a Campaign AI Action Agent with access to comprehensive campaign management tools.

**USER REQUEST:** {user_instruction}

**INTENT ANALYSIS:**
- Type: {intent_analysis['intent_type']}
- Requires DB Changes: {intent_analysis['requires_database_changes']}
- Required Actions: {', '.join(intent_analysis['required_actions'])}

**YOUR CAPABILITIES:**
1. **Campaign Creation**: Create new campaigns with research-backed content
2. **Campaign Management**: Update status, budget, targeting, creative
3. **Bulk Operations**: Pause/activate multiple campaigns based on criteria
4. **Data Analysis**: Analyze campaign performance and trends
5. **Content Generation**: Generate campaign content and targeting
6. **Web Research**: Search for trends, keywords, and market insights

**AVAILABLE MCP TOOLS:**
- create_campaign: Create new campaigns
- update_campaign: Modify existing campaigns
- bulk_campaign_operation: Bulk campaign operations
- list_campaigns_by_criteria: Find campaigns by filters
- mcp_analyze_campaign_performance: AI-powered performance analysis
- mcp_generate_campaign_content: AI content generation
- mcp_optimize_campaign_strategy: AI strategy optimization
- mcp_general_marketing_assistant: General marketing AI
- mcp_search_campaign_data: Vector search in campaign data
- mcp_analyze_campaign_trends: Trend analysis
- mcp_get_facebook_campaigns: Facebook campaign data
- mcp_get_instagram_campaigns: Instagram campaign data
- mcp_tavily_search: Web search for trends and insights
- mcp_wikipedia_search: Wikipedia research

**INSTRUCTIONS:**
1. **For Analysis Requests**: Use analysis tools to provide insights
2. **For Action Requests**: 
   - First gather necessary information (research, analysis)
   - Then execute the requested actions
   - Confirm changes made to campaigns
3. **For Campaign Creation**:
   - Research trends and best practices first
   - Generate appropriate content and targeting
   - Create campaign with optimized settings
4. **For Bulk Operations**:
   - Analyze criteria carefully
   - Show what campaigns will be affected
   - Execute the bulk operation
   - Report results clearly

**MULTI-AGENT COORDINATION:**
- Use web search for market research
- Use content generation for campaign materials
- Use performance analysis for optimization decisions
- Coordinate multiple tools for comprehensive solutions

**CONTEXT:** {json.dumps(context or {}, indent=2)}

Execute the user's request intelligently, using multiple tools as needed to provide a comprehensive solution."""

        return prompt
    
    def _extract_tool_calls(self, messages: List) -> List[Dict[str, Any]]:
        """Extract tool call information from messages."""
        tool_calls = []
        sequence = 1
        
        for message in messages:
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tool_call in message.tool_calls:
                    call_info = {
                        "sequence": sequence,
                        "name": tool_call["name"],
                        "args": tool_call.get("args", {}),
                        "timestamp": datetime.utcnow().isoformat(),
                        "is_database_tool": self._is_database_tool(tool_call["name"])
                    }
                    tool_calls.append(call_info)
                    logger.info(f"🔧 {self.agent_id} Tool Call #{sequence}: {tool_call['name']}")
                    sequence += 1
        
        return tool_calls
    
    def _is_database_tool(self, tool_name: str) -> bool:
        """Check if a tool makes database changes."""
        database_tools = [
            "create_campaign",
            "update_campaign", 
            "bulk_campaign_operation"
        ]
        return tool_name in database_tools
    
    async def create_intelligent_campaign(self,
                                        campaign_brief: str,
                                        platform: str = "facebook",
                                        budget: float = 1000.0) -> Dict[str, Any]:
        """
        Create an intelligent campaign with research and content generation.
        
        This method demonstrates multi-agent coordination by:
        1. Researching trends and best practices
        2. Generating optimized content and targeting
        3. Creating the campaign with intelligent defaults
        
        Args:
            campaign_brief: High-level campaign description
            platform: Target platform (facebook/instagram)
            budget: Campaign budget
            
        Returns:
            Campaign creation results
        """
        try:
            logger.info(f"🎯 Creating intelligent campaign: {campaign_brief}")
            
            # Ensure MCP connection
            if not await self.initialize_mcp_connection():
                raise Exception("Failed to establish MCP connection")
            
            # Step 1: Research trends and best practices
            research_prompt = f"""
            Research current marketing trends and best practices for: {campaign_brief}
            
            Use web search to find:
            1. Current trends related to this campaign type
            2. Best practices for {platform} campaigns
            3. Effective targeting strategies
            4. Optimal budget allocation approaches
            
            Provide actionable insights for campaign creation.
            """
            
            research_messages = [HumanMessage(content=research_prompt)]
            research_response = await self.mcp_agent.ainvoke({"messages": research_messages})
            research_output = research_response["messages"][-1].content
            
            # Step 2: Generate campaign content and targeting
            content_prompt = f"""
            Based on this research: {research_output}
            
            Generate optimized campaign content for: {campaign_brief}
            
            Create:
            1. Campaign name (engaging and descriptive)
            2. Campaign objective (conversions, traffic, awareness, etc.)
            3. Target audience (demographics, interests, behaviors)
            4. Ad creative content (headlines, descriptions, call-to-action)
            5. Campaign settings (placement, schedule, optimization)
            
            Format as JSON for campaign creation.
            """
            
            content_messages = [HumanMessage(content=content_prompt)]
            content_response = await self.mcp_agent.ainvoke({"messages": content_messages})
            content_output = content_response["messages"][-1].content
            
            # Step 3: Create the campaign
            creation_prompt = f"""
            Create a new campaign using this generated content: {content_output}
            
            Campaign Brief: {campaign_brief}
            Platform: {platform}
            Budget: {budget}
            
            Use the create_campaign tool with the optimized parameters.
            """
            
            creation_messages = [HumanMessage(content=creation_prompt)]
            creation_response = await self.mcp_agent.ainvoke({"messages": creation_messages})
            
            # Extract all tool calls
            all_tool_calls = []
            for response in [research_response, content_response, creation_response]:
                all_tool_calls.extend(self._extract_tool_calls(response["messages"]))
            
            final_output = creation_response["messages"][-1].content
            
            return {
                "success": True,
                "campaign_brief": campaign_brief,
                "research_insights": research_output,
                "generated_content": content_output,
                "creation_result": final_output,
                "tool_calls": all_tool_calls,
                "multi_agent_coordination": True
            }
            
        except Exception as e:
            logger.error(f"❌ Intelligent campaign creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "campaign_brief": campaign_brief
            }

# Factory function
def create_campaign_action_agent(model: str = "gpt-4o-mini", temperature: float = 0.2) -> CampaignActionAgent:
    """Create a new Campaign Action Agent."""
    return CampaignActionAgent(model=model, temperature=temperature) 