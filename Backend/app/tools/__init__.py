"""
Tools module for LangChain/LangGraph agents.

This module provides search tools that can be used by agents in the campaign optimization platform.
"""

# Import search tools
from .search_tools import wikipedia_search, tavily_search, get_search_tools

# Import vector search tools
from .vector_search_tools import (
    search_campaign_data, 
    search_similar_campaigns, 
    analyze_campaign_trends,
    get_vector_search_tools
)

# Import Facebook and Instagram API tools
from .facebook_campaign_api import get_facebook_campaign_tools
from .instagram_campaign_api import get_instagram_campaign_tools
from .analytics_api import get_analytics_tools
from .content_management_api import get_content_management_tools
from .social_engagement_api import get_social_engagement_tools

def get_all_tools():
    """Get all available tools for agents."""
    tools = []
    
    # Add search tools
    tools.extend(get_search_tools())
    
    # Add vector search tools
    tools.extend(get_vector_search_tools())
    
    # Add Facebook campaign tools
    tools.extend(get_facebook_campaign_tools())
    
    # Add Instagram campaign tools
    tools.extend(get_instagram_campaign_tools())
    
    # Add analytics tools
    tools.extend(get_analytics_tools())
    
    # Add content management tools
    tools.extend(get_content_management_tools())
    
    # Add social engagement tools
    tools.extend(get_social_engagement_tools())
    
    return tools

def get_campaign_management_tools():
    """Get campaign management tools only."""
    tools = []
    tools.extend(get_facebook_campaign_tools())
    tools.extend(get_instagram_campaign_tools())
    return tools

def get_analysis_tools():
    """Get analysis and reporting tools only."""
    tools = []
    
    # Add vector search tools for semantic analysis
    tools.extend(get_vector_search_tools())
    
    # Add traditional analytics tools
    tools.extend(get_analytics_tools())
    tools.extend(get_content_management_tools())
    tools.extend(get_social_engagement_tools())
    return tools

# Export individual tool functions for direct use
__all__ = [
    'wikipedia_search',
    'tavily_search',
    'get_search_tools',
    'search_campaign_data',
    'search_similar_campaigns', 
    'analyze_campaign_trends',
    'get_vector_search_tools',
    'get_facebook_campaign_tools',
    'get_instagram_campaign_tools',
    'get_analytics_tools',
    'get_content_management_tools',
    'get_social_engagement_tools',
    'get_all_tools',
    'get_campaign_management_tools',
    'get_analysis_tools'
] 