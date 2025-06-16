#!/usr/bin/env python3
"""
Campaign AI MCP Server

This server exposes Campaign AI tools via the Model Context Protocol (MCP)
for client applications to discover and use.
"""

import os
import sys
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the Backend directory to the Python path (go up 3 levels from app/mcp/server)
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(backend_dir)

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("CampaignAI")

# Import our Campaign AI tool functions
try:
    from app.tools.llm_tools import (
        analyze_campaign_performance,
        generate_campaign_content,
        optimize_campaign_strategy,
        general_marketing_assistant
    )
    from app.tools.vector_search_tools import (
        search_campaign_data,
        analyze_campaign_trends
    )
    from app.tools.facebook_campaign_api import (
        get_facebook_campaigns,
        get_facebook_campaign_details
    )
    from app.tools.instagram_campaign_api import (
        get_instagram_campaigns,
        get_instagram_campaign_details
    )
    from app.tools.search_tools import (
        tavily_search,
        wikipedia_search
    )
    from app.tools.campaign_action_tool import (
        create_campaign,
        update_campaign,
        bulk_campaign_operation,
        list_campaigns_by_criteria
    )
    
    logger.info("✅ Successfully imported Campaign AI tool functions")
    
except Exception as e:
    logger.error(f"❌ Failed to import tool functions: {str(e)}")
    sys.exit(1)

# Define MCP tools directly using FastMCP decorators

@mcp.tool()
def get_server_info() -> Dict[str, Any]:
    """Get information about the Campaign AI MCP server."""
    return {
        "server_name": "Campaign AI MCP Server",
        "version": "1.0.0",
        "description": "MCP server providing Campaign AI tools for marketing optimization",
        "categories": [
            "llm_tools",
            "vector_search", 
            "campaign_api",
            "campaign_actions",
            "search_tools"
        ],
        "total_tools": 18
    }

@mcp.tool()
def test_connection() -> str:
    """Test the connection to the Campaign AI MCP server."""
    return "✅ Connection successful! Campaign AI MCP Server is operational."

# LLM Tools
@mcp.tool()
def mcp_analyze_campaign_performance(campaign_data: str) -> str:
    """Analyze campaign performance using AI."""
    try:
        # Call the actual tool function
        result = analyze_campaign_performance.invoke({"campaign_data": campaign_data})
        logger.info(f"🧠 analyze_campaign_performance called with input length: {len(campaign_data)}")
        logger.info(f"🧠 analyze_campaign_performance output length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"❌ analyze_campaign_performance failed: {str(e)}")
        return f"Error analyzing campaign: {str(e)}"

@mcp.tool()
def mcp_generate_campaign_content(campaign_type: str, target_audience: str, platform: str) -> str:
    """Generate campaign content using AI."""
    try:
        result = generate_campaign_content.invoke({
            "campaign_type": campaign_type,
            "target_audience": target_audience,
            "platform": platform
        })
        logger.info(f"🧠 generate_campaign_content called: {campaign_type}, {target_audience}, {platform}")
        logger.info(f"🧠 generate_campaign_content output length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"❌ generate_campaign_content failed: {str(e)}")
        return f"Error generating content: {str(e)}"

@mcp.tool()
def mcp_optimize_campaign_strategy(campaign_data: str, goals: str) -> str:
    """Optimize campaign strategy using AI."""
    try:
        result = optimize_campaign_strategy.invoke({
            "campaign_data": campaign_data,
            "goals": goals
        })
        logger.info(f"🧠 optimize_campaign_strategy called with data length: {len(campaign_data)}")
        logger.info(f"🧠 optimize_campaign_strategy output length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"❌ optimize_campaign_strategy failed: {str(e)}")
        return f"Error optimizing strategy: {str(e)}"

@mcp.tool()
def mcp_general_marketing_assistant(query: str) -> str:
    """General marketing assistant using AI."""
    try:
        result = general_marketing_assistant.invoke({"query": query})
        logger.info(f"🧠 general_marketing_assistant called with query length: {len(query)}")
        logger.info(f"🧠 general_marketing_assistant output length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"❌ general_marketing_assistant failed: {str(e)}")
        return f"Error with marketing assistant: {str(e)}"

# Vector Search Tools
@mcp.tool()
def mcp_search_campaign_data(query: str, limit: int = 5) -> str:
    """Search campaign database using vector similarity."""
    try:
        result = search_campaign_data.invoke({
            "query": query,
            "limit": limit
        })
        logger.info(f"🔍 search_campaign_data called: {query[:50]}... (limit: {limit})")
        logger.info(f"🔍 search_campaign_data output length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"❌ search_campaign_data failed: {str(e)}")
        return f"Error searching campaigns: {str(e)}"

@mcp.tool()
def mcp_analyze_campaign_trends(time_period: str = "30_days") -> str:
    """Analyze campaign trends over time."""
    try:
        result = analyze_campaign_trends.invoke({"time_period": time_period})
        logger.info(f"🔍 analyze_campaign_trends called for period: {time_period}")
        logger.info(f"🔍 analyze_campaign_trends output length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"❌ analyze_campaign_trends failed: {str(e)}")
        return f"Error analyzing trends: {str(e)}"

# Campaign API Tools
@mcp.tool()
def mcp_get_facebook_campaigns(limit: int = 10) -> str:
    """Get Facebook campaigns from API."""
    try:
        result = get_facebook_campaigns.invoke({"limit": limit})
        logger.info(f"📱 get_facebook_campaigns called (limit: {limit})")
        logger.info(f"📱 get_facebook_campaigns output length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"❌ get_facebook_campaigns failed: {str(e)}")
        return f"Error getting Facebook campaigns: {str(e)}"

@mcp.tool()
def mcp_get_facebook_campaign_details(campaign_id: str) -> str:
    """Get detailed Facebook campaign information."""
    try:
        result = get_facebook_campaign_details.invoke({"campaign_id": campaign_id})
        logger.info(f"📱 get_facebook_campaign_details called for ID: {campaign_id}")
        logger.info(f"📱 get_facebook_campaign_details output length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"❌ get_facebook_campaign_details failed: {str(e)}")
        return f"Error getting Facebook campaign details: {str(e)}"

@mcp.tool()
def mcp_get_instagram_campaigns(limit: int = 10) -> str:
    """Get Instagram campaigns from API."""
    try:
        result = get_instagram_campaigns.invoke({"limit": limit})
        logger.info(f"📱 get_instagram_campaigns called (limit: {limit})")
        logger.info(f"📱 get_instagram_campaigns output length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"❌ get_instagram_campaigns failed: {str(e)}")
        return f"Error getting Instagram campaigns: {str(e)}"

@mcp.tool()
def mcp_get_instagram_campaign_details(campaign_id: str) -> str:
    """Get detailed Instagram campaign information."""
    try:
        result = get_instagram_campaign_details.invoke({"campaign_id": campaign_id})
        logger.info(f"📱 get_instagram_campaign_details called for ID: {campaign_id}")
        logger.info(f"📱 get_instagram_campaign_details output length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"❌ get_instagram_campaign_details failed: {str(e)}")
        return f"Error getting Instagram campaign details: {str(e)}"

# Campaign Action Tools (NEW!)
@mcp.tool()
def mcp_create_campaign(
    name: str,
    platform: str,
    objective: str,
    budget_amount: float,
    budget_type: str = "daily",
    target_audience: str = None,
    ad_creative: str = None,
    start_date: str = None,
    end_date: str = None,
    campaign_settings: str = None
) -> str:
    """Create a new campaign in the database."""
    try:
        result = create_campaign.invoke({
            "name": name,
            "platform": platform,
            "objective": objective,
            "budget_amount": budget_amount,
            "budget_type": budget_type,
            "target_audience": target_audience,
            "ad_creative": ad_creative,
            "start_date": start_date,
            "end_date": end_date,
            "campaign_settings": campaign_settings
        })
        logger.info(f"🎯 create_campaign called: {name} on {platform}")
        logger.info(f"🎯 create_campaign output length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"❌ create_campaign failed: {str(e)}")
        return f"Error creating campaign: {str(e)}"

@mcp.tool()
def mcp_update_campaign(
    campaign_id: str,
    name: str = None,
    status: str = None,
    budget_amount: float = None,
    budget_type: str = None,
    target_audience: str = None,
    ad_creative: str = None,
    end_date: str = None,
    campaign_settings: str = None
) -> str:
    """Update an existing campaign in the database."""
    try:
        result = update_campaign.invoke({
            "campaign_id": campaign_id,
            "name": name,
            "status": status,
            "budget_amount": budget_amount,
            "budget_type": budget_type,
            "target_audience": target_audience,
            "ad_creative": ad_creative,
            "end_date": end_date,
            "campaign_settings": campaign_settings
        })
        logger.info(f"🎯 update_campaign called for ID: {campaign_id}")
        logger.info(f"🎯 update_campaign output length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"❌ update_campaign failed: {str(e)}")
        return f"Error updating campaign: {str(e)}"

@mcp.tool()
def mcp_bulk_campaign_operation(
    operation: str,
    filters: str,
    updates: str = None
) -> str:
    """Perform bulk operations on multiple campaigns."""
    try:
        result = bulk_campaign_operation.invoke({
            "operation": operation,
            "filters": filters,
            "updates": updates
        })
        logger.info(f"🎯 bulk_campaign_operation called: {operation}")
        logger.info(f"🎯 bulk_campaign_operation output length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"❌ bulk_campaign_operation failed: {str(e)}")
        return f"Error with bulk operation: {str(e)}"

@mcp.tool()
def mcp_list_campaigns_by_criteria(
    platform: str = None,
    status: str = None,
    min_budget: float = None,
    max_budget: float = None,
    min_ctr: float = None,
    max_ctr: float = None,
    min_roas: float = None,
    max_roas: float = None,
    limit: int = 50
) -> str:
    """List campaigns that match specific criteria."""
    try:
        result = list_campaigns_by_criteria.invoke({
            "platform": platform,
            "status": status,
            "min_budget": min_budget,
            "max_budget": max_budget,
            "min_ctr": min_ctr,
            "max_ctr": max_ctr,
            "min_roas": min_roas,
            "max_roas": max_roas,
            "limit": limit
        })
        logger.info(f"🎯 list_campaigns_by_criteria called with filters")
        logger.info(f"🎯 list_campaigns_by_criteria output length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"❌ list_campaigns_by_criteria failed: {str(e)}")
        return f"Error listing campaigns: {str(e)}"

# Search Tools
@mcp.tool()
def mcp_tavily_search(query: str) -> str:
    """Search the web using Tavily API."""
    try:
        result = tavily_search.invoke({"query": query})
        logger.info(f"🔍 tavily_search called: {query[:50]}...")
        logger.info(f"🔍 tavily_search output length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"❌ tavily_search failed: {str(e)}")
        return f"Error with Tavily search: {str(e)}"

@mcp.tool()
def mcp_wikipedia_search(query: str) -> str:
    """Search Wikipedia for information."""
    try:
        result = wikipedia_search.invoke({"query": query})
        logger.info(f"🔍 wikipedia_search called: {query[:50]}...")
        logger.info(f"🔍 wikipedia_search output length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"❌ wikipedia_search failed: {str(e)}")
        return f"Error with Wikipedia search: {str(e)}"

if __name__ == "__main__":
    logger.info("🌐 Starting Campaign AI MCP Server (Enhanced Version)...")
    logger.info("📊 Available MCP tools:")
    logger.info("   🔧 Server Tools:")
    logger.info("     - get_server_info: Get server information")
    logger.info("     - test_connection: Test server connection")
    logger.info("   🧠 LLM Tools:")
    logger.info("     - mcp_analyze_campaign_performance: Analyze campaign performance")
    logger.info("     - mcp_generate_campaign_content: Generate campaign content")
    logger.info("     - mcp_optimize_campaign_strategy: Optimize campaign strategy")
    logger.info("     - mcp_general_marketing_assistant: General marketing assistant")
    logger.info("   🔍 Vector Search Tools:")
    logger.info("     - mcp_search_campaign_data: Search campaign database")
    logger.info("     - mcp_analyze_campaign_trends: Analyze campaign trends")
    logger.info("   📱 Campaign API Tools:")
    logger.info("     - mcp_get_facebook_campaigns: Get Facebook campaigns")
    logger.info("     - mcp_get_facebook_campaign_details: Get Facebook campaign details")
    logger.info("     - mcp_get_instagram_campaigns: Get Instagram campaigns")
    logger.info("     - mcp_get_instagram_campaign_details: Get Instagram campaign details")
    logger.info("   🎯 Campaign Action Tools (NEW!):")
    logger.info("     - mcp_create_campaign: Create new campaigns")
    logger.info("     - mcp_update_campaign: Update existing campaigns")
    logger.info("     - mcp_bulk_campaign_operation: Bulk campaign operations")
    logger.info("     - mcp_list_campaigns_by_criteria: List campaigns by criteria")
    logger.info("   🌐 Search Tools:")
    logger.info("     - mcp_tavily_search: Search web with Tavily")
    logger.info("     - mcp_wikipedia_search: Search Wikipedia")
    
    logger.info("🚀 Server ready for client connections!")
    
    # Run the server with stdio transport for client connections
    mcp.run(transport="stdio") 