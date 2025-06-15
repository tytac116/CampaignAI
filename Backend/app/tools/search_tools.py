"""
Search tools for LangChain/LangGraph agents.

This module provides Wikipedia and Tavily search tools that can be used by agents
to gather information from external sources.
"""

import os
import logging
from typing import Dict, Any, Optional
from langchain_core.tools import tool
import wikipedia
import requests

logger = logging.getLogger(__name__)


@tool
def wikipedia_search(query: str) -> str:
    """
    Search Wikipedia for factual information.
    
    Use this tool when you need reliable, encyclopedic information about
    topics, people, places, concepts, or historical facts.
    
    Args:
        query: The search query string
        
    Returns:
        Wikipedia search results as a string
    """
    try:
        logger.info(f"Searching Wikipedia for: {query}")
        
        # Set Wikipedia language and user agent
        wikipedia.set_lang("en")
        
        # Search for pages
        search_results = wikipedia.search(query, results=3)
        
        if not search_results:
            return f"No Wikipedia results found for: {query}"
        
        # Get summary of the first result
        try:
            page_title = search_results[0]
            summary = wikipedia.summary(page_title, sentences=10)
            
            # Get the page URL
            page = wikipedia.page(page_title)
            url = page.url
            
            result = f"Wikipedia Search Results for: {query}\n\n"
            result += f"Title: {page_title}\n"
            result += f"URL: {url}\n\n"
            result += f"Summary:\n{summary}\n\n"
            
            # Add other search results
            if len(search_results) > 1:
                result += "Other related pages:\n"
                for title in search_results[1:]:
                    try:
                        page = wikipedia.page(title)
                        result += f"- {title}: {page.url}\n"
                    except:
                        result += f"- {title}\n"
            
            logger.info(f"Wikipedia search completed for: {query}")
            return result
            
        except wikipedia.exceptions.DisambiguationError as e:
            # Handle disambiguation pages
            options = e.options[:5]  # Get first 5 options
            result = f"Wikipedia Search Results for: {query}\n\n"
            result += f"Multiple pages found. Here are some options:\n"
            for option in options:
                result += f"- {option}\n"
            return result
            
        except wikipedia.exceptions.PageError:
            return f"Wikipedia page not found for: {query}"
            
    except Exception as e:
        error_msg = f"Wikipedia search failed for query '{query}': {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@tool
def tavily_search(query: str) -> str:
    """
    Search the web for current, real-time information using Tavily.
    
    Use this tool when you need up-to-date information, news, current events,
    recent developments, or information not available in Wikipedia.
    
    Args:
        query: The search query string
        
    Returns:
        Tavily search results as a formatted string
    """
    try:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return "Error: Tavily search tool not available. Please check TAVILY_API_KEY environment variable."
        
        logger.info(f"Searching Tavily for: {query}")
        
        # Tavily API endpoint
        url = "https://api.tavily.com/search"
        
        payload = {
            "api_key": api_key,
            "query": query,
            "search_depth": "basic",
            "include_answer": False,
            "include_raw_content": False,
            "max_results": 5
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Format the results
        result = f"Tavily Search Results for: {query}\n\n"
        
        if "answer" in data and data["answer"]:
            result += f"Answer: {data['answer']}\n\n"
        
        if "results" in data and data["results"]:
            result += "Search Results:\n"
            for i, item in enumerate(data["results"], 1):
                title = item.get("title", "No title")
                url = item.get("url", "No URL")
                content = item.get("content", "No content")
                
                # Truncate content if too long
                if len(content) > 300:
                    content = content[:300] + "..."
                
                result += f"\n{i}. {title}\n"
                result += f"   URL: {url}\n"
                result += f"   Content: {content}\n"
        else:
            result += "No search results found."
        
        logger.info(f"Tavily search completed for: {query}")
        return result
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Tavily API request failed: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Tavily search failed for query '{query}': {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


def get_search_tools():
    """Get the search tools for use with ToolNode."""
    return [wikipedia_search, tavily_search]


def test_search_tools():
    """Test the search tools."""
    print("Testing Wikipedia tool...")
    result = wikipedia_search("Python programming language")
    print(f"Wikipedia result length: {len(result)}")
    print(f"Preview: {result[:200]}...")
    
    print("\nTesting Tavily tool...")
    result = tavily_search("latest AI news")
    print(f"Tavily result length: {len(result)}")
    print(f"Preview: {result[:200]}...")


if __name__ == "__main__":
    test_search_tools() 