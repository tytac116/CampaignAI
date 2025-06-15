"""
OpenAI LLM Tools for Campaign Analysis and Content Generation

This module provides access to OpenAI's language models as tools that agents
can use for advanced reasoning, content generation, and analysis tasks.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class CampaignLLMAssistant:
    """Handles OpenAI LLM interactions for campaign-related tasks."""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=2000
        )
        logger.info(f"✅ Initialized LLM Assistant with model: {model}")
    
    def generate_response(self, prompt: str, system_message: Optional[str] = None) -> str:
        """Generate a response using the LLM."""
        try:
            messages = []
            
            if system_message:
                messages.append(SystemMessage(content=system_message))
            
            messages.append(HumanMessage(content=prompt))
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"❌ LLM generation error: {str(e)}")
            return f"❌ Error generating response: {str(e)}"

# Initialize the LLM assistant
_llm_assistant = None

def get_llm_assistant():
    """Get or create the LLM assistant instance."""
    global _llm_assistant
    if _llm_assistant is None:
        _llm_assistant = CampaignLLMAssistant()
    return _llm_assistant

@tool
def analyze_campaign_performance(
    campaign_data: str,
    analysis_type: str = "comprehensive",
    focus_areas: Optional[str] = None
) -> str:
    """
    Analyze campaign performance data using advanced LLM reasoning.
    
    This tool provides deep analysis of campaign performance metrics, identifying
    patterns, insights, and actionable recommendations using AI reasoning.
    
    Args:
        campaign_data: Campaign performance data (metrics, trends, comparisons)
        analysis_type: Type of analysis to perform:
            - "comprehensive": Full analysis with insights and recommendations
            - "performance": Focus on performance metrics and optimization
            - "competitive": Competitive analysis and benchmarking
            - "troubleshooting": Identify issues and solutions
            - "forecasting": Predict future performance trends
        focus_areas: Specific areas to focus on (e.g., "ROAS, CTR, engagement")
    
    Returns:
        Detailed analysis with insights, patterns, and actionable recommendations
    
    Examples:
        - Analyze overall campaign performance and identify optimization opportunities
        - Compare campaign performance against benchmarks and competitors
        - Troubleshoot underperforming campaigns and suggest fixes
        - Forecast future performance based on current trends
    """
    try:
        llm_assistant = get_llm_assistant()
        
        # Build system message based on analysis type
        system_messages = {
            "comprehensive": """You are an expert digital marketing analyst specializing in campaign performance analysis. 
            Provide comprehensive insights covering performance metrics, trends, optimization opportunities, and strategic recommendations. 
            Focus on actionable insights that can drive measurable improvements.""",
            
            "performance": """You are a performance marketing specialist focused on metrics optimization. 
            Analyze the data for performance patterns, identify key drivers of success/failure, and provide specific 
            optimization recommendations for ROAS, CTR, conversion rates, and other key metrics.""",
            
            "competitive": """You are a competitive intelligence analyst for digital marketing campaigns. 
            Compare the provided data against industry benchmarks, identify competitive advantages/disadvantages, 
            and suggest strategies to outperform competitors.""",
            
            "troubleshooting": """You are a campaign troubleshooting expert. Identify specific issues, problems, 
            or underperformance patterns in the data. Provide clear diagnostic insights and step-by-step solutions 
            to fix identified problems.""",
            
            "forecasting": """You are a marketing data scientist specializing in performance forecasting. 
            Analyze trends and patterns to predict future campaign performance. Provide forecasts with confidence 
            intervals and recommendations for proactive optimization."""
        }
        
        system_message = system_messages.get(analysis_type, system_messages["comprehensive"])
        
        # Build the analysis prompt
        prompt_parts = [
            f"Please analyze the following campaign performance data:\n\n{campaign_data}\n"
        ]
        
        if focus_areas:
            prompt_parts.append(f"Focus specifically on these areas: {focus_areas}\n")
        
        prompt_parts.extend([
            f"Analysis Type: {analysis_type.title()}\n",
            "Please provide:",
            "1. Key insights and patterns identified",
            "2. Performance assessment and benchmarking",
            "3. Specific issues or opportunities",
            "4. Actionable recommendations with priority levels",
            "5. Expected impact of recommended actions",
            "",
            "Format your response with clear sections and bullet points for easy readability."
        ])
        
        prompt = "\n".join(prompt_parts)
        
        response = llm_assistant.generate_response(prompt, system_message)
        
        # Add metadata header
        result = f"🤖 **AI Campaign Analysis ({analysis_type.title()})**\n"
        result += f"📊 **Model**: {llm_assistant.model}\n"
        if focus_areas:
            result += f"🎯 **Focus Areas**: {focus_areas}\n"
        result += "=" * 60 + "\n\n"
        result += response
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Campaign analysis error: {str(e)}")
        return f"❌ Error analyzing campaign performance: {str(e)}"

@tool
def generate_campaign_content(
    content_type: str,
    campaign_objective: str,
    target_audience: str,
    platform: str = "facebook",
    tone: str = "professional",
    additional_context: Optional[str] = None
) -> str:
    """
    Generate campaign content using AI creativity and marketing expertise.
    
    This tool creates various types of marketing content optimized for specific
    platforms, audiences, and campaign objectives.
    
    Args:
        content_type: Type of content to generate:
            - "ad_copy": Advertisement copy and headlines
            - "social_post": Social media post content
            - "email_subject": Email subject lines
            - "landing_page": Landing page copy
            - "video_script": Video advertisement script
            - "campaign_strategy": Campaign strategy document
        campaign_objective: Campaign goal (e.g., "increase brand awareness", "drive conversions")
        target_audience: Description of target audience (e.g., "small business owners aged 25-45")
        platform: Target platform ("facebook", "instagram", "linkedin", "google", "email")
        tone: Content tone ("professional", "casual", "urgent", "friendly", "authoritative")
        additional_context: Extra context or requirements
    
    Returns:
        Generated content optimized for the specified parameters
    
    Examples:
        - Generate Facebook ad copy for lead generation campaigns
        - Create Instagram post content for brand awareness
        - Write email subject lines for product launches
        - Develop video scripts for engagement campaigns
    """
    try:
        llm_assistant = get_llm_assistant()
        
        # Build system message for content generation
        system_message = f"""You are an expert copywriter and digital marketing content creator with extensive experience 
        in creating high-converting content for {platform.title()}. You understand platform-specific best practices, 
        audience psychology, and conversion optimization techniques. Create compelling, engaging content that drives action 
        while maintaining the specified tone and meeting the campaign objectives."""
        
        # Build the content generation prompt
        prompt_parts = [
            f"Create {content_type.replace('_', ' ')} for a {platform.title()} campaign with the following specifications:",
            "",
            f"📋 **Campaign Objective**: {campaign_objective}",
            f"👥 **Target Audience**: {target_audience}",
            f"📱 **Platform**: {platform.title()}",
            f"🎭 **Tone**: {tone.title()}",
        ]
        
        if additional_context:
            prompt_parts.append(f"📝 **Additional Context**: {additional_context}")
        
        prompt_parts.extend([
            "",
            "Requirements:",
            f"- Optimize for {platform} best practices and character limits",
            f"- Appeal to the specified target audience",
            f"- Maintain a {tone} tone throughout",
            f"- Focus on achieving the campaign objective: {campaign_objective}",
            "- Include compelling calls-to-action where appropriate",
            "- Use persuasive copywriting techniques",
            "",
            "Please provide multiple variations (3-5) if applicable, and explain the strategy behind your content choices."
        ])
        
        prompt = "\n".join(prompt_parts)
        
        response = llm_assistant.generate_response(prompt, system_message)
        
        # Add metadata header
        result = f"✨ **AI Content Generation ({content_type.replace('_', ' ').title()})**\n"
        result += f"🎯 **Objective**: {campaign_objective}\n"
        result += f"👥 **Audience**: {target_audience}\n"
        result += f"📱 **Platform**: {platform.title()}\n"
        result += f"🎭 **Tone**: {tone.title()}\n"
        result += "=" * 60 + "\n\n"
        result += response
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Content generation error: {str(e)}")
        return f"❌ Error generating campaign content: {str(e)}"

@tool
def optimize_campaign_strategy(
    current_strategy: str,
    performance_data: str,
    optimization_goals: str,
    constraints: Optional[str] = None
) -> str:
    """
    Optimize campaign strategy using AI-powered strategic thinking.
    
    This tool analyzes current campaign strategies and performance data to provide
    strategic optimization recommendations and improved campaign approaches.
    
    Args:
        current_strategy: Description of current campaign strategy and approach
        performance_data: Current performance metrics and trends
        optimization_goals: Specific goals for optimization (e.g., "increase ROAS by 25%")
        constraints: Any constraints or limitations (budget, timeline, resources)
    
    Returns:
        Optimized strategy with specific recommendations and implementation plan
    
    Examples:
        - Optimize underperforming campaigns for better ROAS
        - Improve engagement rates for social media campaigns
        - Scale successful campaigns while maintaining efficiency
        - Pivot strategy based on performance insights
    """
    try:
        llm_assistant = get_llm_assistant()
        
        system_message = """You are a senior digital marketing strategist with expertise in campaign optimization 
        and performance marketing. You excel at analyzing campaign data, identifying optimization opportunities, 
        and developing strategic recommendations that drive measurable improvements. Provide actionable, 
        data-driven strategies with clear implementation steps."""
        
        # Build the optimization prompt
        prompt_parts = [
            "Please analyze and optimize the following campaign strategy:",
            "",
            f"📋 **Current Strategy**:\n{current_strategy}",
            "",
            f"📊 **Performance Data**:\n{performance_data}",
            "",
            f"🎯 **Optimization Goals**: {optimization_goals}",
        ]
        
        if constraints:
            prompt_parts.append(f"⚠️ **Constraints**: {constraints}")
        
        prompt_parts.extend([
            "",
            "Please provide:",
            "1. **Strategy Analysis**: Strengths and weaknesses of current approach",
            "2. **Performance Assessment**: Key insights from the data",
            "3. **Optimization Opportunities**: Specific areas for improvement",
            "4. **Recommended Strategy**: Detailed optimization plan",
            "5. **Implementation Roadmap**: Step-by-step action plan with priorities",
            "6. **Success Metrics**: KPIs to track optimization success",
            "7. **Risk Assessment**: Potential risks and mitigation strategies",
            "",
            "Focus on actionable recommendations that can realistically achieve the optimization goals."
        ])
        
        prompt = "\n".join(prompt_parts)
        
        response = llm_assistant.generate_response(prompt, system_message)
        
        # Add metadata header
        result = f"🚀 **AI Strategy Optimization**\n"
        result += f"🎯 **Goals**: {optimization_goals}\n"
        if constraints:
            result += f"⚠️ **Constraints**: {constraints}\n"
        result += "=" * 60 + "\n\n"
        result += response
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Strategy optimization error: {str(e)}")
        return f"❌ Error optimizing campaign strategy: {str(e)}"

@tool
def general_marketing_assistant(
    query: str,
    context: Optional[str] = None,
    expertise_area: str = "general"
) -> str:
    """
    General-purpose marketing AI assistant for various marketing questions and tasks.
    
    This tool provides expert marketing advice, answers questions, and helps with
    various marketing-related tasks using advanced AI reasoning.
    
    Args:
        query: Your marketing question or task description
        context: Additional context or background information
        expertise_area: Specific area of expertise to focus on:
            - "general": General marketing advice
            - "digital_advertising": Digital ads and PPC
            - "social_media": Social media marketing
            - "content_marketing": Content strategy and creation
            - "analytics": Marketing analytics and measurement
            - "conversion_optimization": CRO and funnel optimization
            - "brand_strategy": Brand positioning and strategy
    
    Returns:
        Expert marketing advice and recommendations
    
    Examples:
        - "How can I improve my Facebook ad targeting?"
        - "What's the best way to measure campaign ROI?"
        - "Help me create a content calendar for Instagram"
        - "How do I optimize my landing page conversion rate?"
    """
    try:
        llm_assistant = get_llm_assistant()
        
        # Build system message based on expertise area
        expertise_messages = {
            "general": "You are an expert marketing consultant with broad experience across all marketing disciplines.",
            "digital_advertising": "You are a digital advertising specialist with expertise in PPC, social ads, and programmatic advertising.",
            "social_media": "You are a social media marketing expert with deep knowledge of platform strategies and community building.",
            "content_marketing": "You are a content marketing strategist specializing in content creation, distribution, and performance optimization.",
            "analytics": "You are a marketing analytics expert specializing in measurement, attribution, and data-driven insights.",
            "conversion_optimization": "You are a conversion rate optimization specialist focused on funnel optimization and user experience.",
            "brand_strategy": "You are a brand strategist with expertise in positioning, messaging, and brand development."
        }
        
        system_message = expertise_messages.get(expertise_area, expertise_messages["general"])
        system_message += " Provide practical, actionable advice based on current best practices and proven strategies."
        
        # Build the query prompt
        prompt_parts = [f"**Question/Task**: {query}"]
        
        if context:
            prompt_parts.append(f"**Context**: {context}")
        
        prompt_parts.extend([
            "",
            "Please provide:",
            "- Clear, actionable advice",
            "- Specific recommendations with rationale",
            "- Best practices and proven strategies",
            "- Implementation steps where applicable",
            "- Potential challenges and solutions",
            "",
            "Make your response practical and immediately useful."
        ])
        
        prompt = "\n".join(prompt_parts)
        
        response = llm_assistant.generate_response(prompt, system_message)
        
        # Add metadata header
        result = f"🤖 **Marketing AI Assistant ({expertise_area.replace('_', ' ').title()})**\n"
        result += f"❓ **Query**: {query}\n"
        result += "=" * 60 + "\n\n"
        result += response
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Marketing assistant error: {str(e)}")
        return f"❌ Error processing marketing query: {str(e)}"

# Export functions for tool registry
def get_llm_tools():
    """Get all LLM tools."""
    return [
        analyze_campaign_performance,
        generate_campaign_content,
        optimize_campaign_strategy,
        general_marketing_assistant
    ] 