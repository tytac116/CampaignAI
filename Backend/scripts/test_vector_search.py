#!/usr/bin/env python3
"""
Test script for vector search tools.

This script tests the vector search functionality with various queries
to ensure the tools work correctly with the ingested campaign data.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the parent directory to the path to import from app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.tools.vector_search_tools import (
    search_campaign_data,
    search_similar_campaigns,
    analyze_campaign_trends
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic_search():
    """Test basic campaign data search."""
    print("🔍 Testing Basic Campaign Search...")
    print("=" * 60)
    
    # Test query for high-performing campaigns
    result = search_campaign_data.invoke({
        "query": "high performing Facebook campaigns with positive sentiment",
        "top_k": 3
    })
    print(result)
    print("\n" + "=" * 60 + "\n")

def test_filtered_search():
    """Test search with filters."""
    print("🎯 Testing Filtered Search...")
    print("=" * 60)
    
    # Test with platform filter
    result = search_campaign_data.invoke({
        "query": "engagement rate optimization strategies",
        "filters": '{"platform": "instagram"}',
        "top_k": 3,
        "doc_types": "campaign,content"
    })
    print(result)
    print("\n" + "=" * 60 + "\n")

def test_similar_campaigns():
    """Test similar campaign search."""
    print("🔗 Testing Similar Campaign Search...")
    print("=" * 60)
    
    # First, let's find a campaign ID to use
    search_result = search_campaign_data.invoke({
        "query": "campaign",
        "top_k": 1
    })
    
    # Extract campaign ID from the result (this is a simple approach)
    if "Campaign:" in search_result:
        lines = search_result.split('\n')
        campaign_line = next((line for line in lines if "Campaign:" in line), None)
        if campaign_line:
            # Extract campaign ID (assuming format "Campaign: campaign_id")
            campaign_id = campaign_line.split("Campaign: ")[1].split()[0]
            print(f"Using campaign ID: {campaign_id}")
            
            result = search_similar_campaigns.invoke({
                "campaign_id": campaign_id,
                "similarity_type": "performance",
                "top_k": 3
            })
            print(result)
        else:
            print("❌ Could not extract campaign ID from search result")
    else:
        print("❌ No campaign found in search result")
    
    print("\n" + "=" * 60 + "\n")

def test_trend_analysis():
    """Test campaign trend analysis."""
    print("📈 Testing Trend Analysis...")
    print("=" * 60)
    
    # Test performance trends
    result = analyze_campaign_trends.invoke({
        "metric": "performance",
        "platform": "facebook",
        "top_k": 5
    })
    print(result)
    print("\n" + "=" * 60 + "\n")

def test_sentiment_analysis():
    """Test sentiment-based search."""
    print("😊 Testing Sentiment Analysis...")
    print("=" * 60)
    
    # Test sentiment trends
    result = analyze_campaign_trends.invoke({
        "metric": "sentiment",
        "top_k": 5
    })
    print(result)
    print("\n" + "=" * 60 + "\n")

def test_content_search():
    """Test content-specific search."""
    print("🎨 Testing Content Search...")
    print("=" * 60)
    
    # Test content analysis
    result = search_campaign_data.invoke({
        "query": "video content performance creative strategies",
        "doc_types": "content",
        "top_k": 3
    })
    print(result)
    print("\n" + "=" * 60 + "\n")

def main():
    """Run all tests."""
    print("🚀 Starting Vector Search Tool Tests")
    print("=" * 80)
    
    try:
        # Run all test functions
        test_basic_search()
        test_filtered_search()
        test_similar_campaigns()
        test_trend_analysis()
        test_sentiment_analysis()
        test_content_search()
        
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        print(f"❌ Test failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 