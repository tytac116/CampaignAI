# Facebook & Instagram API Tools for Agents

## 🎯 Overview

This system provides comprehensive Facebook and Instagram API simulation tools designed for LangChain/LangGraph agents. The tools are built using real campaign data from Supabase and simulate realistic API responses that agents can use for campaign optimization and analysis.

## 📊 Database Structure

**Available Tables:**
- **campaigns**: 500 records (250 Facebook, 250 Instagram) - Core campaign data
- **campaign_metrics**: 7,000 records - Daily performance metrics 
- **campaign_content**: 500 records - Content details (titles, descriptions, hashtags, etc.)
- **campaign_comments**: 2,500 records - User comments with sentiment analysis

## 🔧 Tool Categories

### 📘 Facebook Campaign Management (3 tools)
- `get_facebook_campaigns` - Retrieve Facebook campaigns with filtering
- `get_facebook_campaign_details` - Get detailed campaign information
- `update_facebook_campaign` - Update campaign settings (status, budget, name)

### 📷 Instagram Campaign Management (3 tools)
- `get_instagram_campaigns` - Retrieve Instagram campaigns with filtering
- `get_instagram_campaign_details` - Get detailed campaign information
- `update_instagram_campaign` - Update campaign settings (status, budget, name)

### 📈 Analytics & Reporting (3 tools)
- `get_campaign_analytics` - Detailed analytics with daily breakdowns
- `get_platform_performance_comparison` - Compare Facebook vs Instagram performance
- `get_top_performing_campaigns` - Rank campaigns by specific metrics

### 📝 Content Management (3 tools)
- `get_campaign_content` - Retrieve campaign content details
- `analyze_content_performance` - Analyze performance by content type
- `get_hashtag_analysis` - Analyze hashtag effectiveness

### 💬 Social Engagement (3 tools)
- `get_campaign_comments` - Get comments with sentiment filtering
- `analyze_sentiment_trends` - Analyze sentiment patterns across campaigns
- `get_engagement_insights` - Comprehensive engagement analysis

### 🔍 Web Search (2 tools)
- `wikipedia_search` - Search Wikipedia for information
- `tavily_search` - Search the web using Tavily API

## 🚀 Quick Start

```python
from app.tools import get_all_tools
from langgraph.prebuilt import ToolNode

# Get all tools
tools = get_all_tools()

# Create ToolNode for agents
tool_node = ToolNode(tools)

# Use in LangGraph workflow
from langgraph.graph import StateGraph
workflow = StateGraph(YourState)
workflow.add_node("tools", tool_node)
```

## 📋 Usage Examples

### Facebook Campaign Management
```python
# Get active Facebook campaigns
get_facebook_campaigns(limit=10, status='active', objective='conversions')

# Get detailed campaign info
get_facebook_campaign_details(campaign_id='fa_camp_0001')

# Update campaign status
update_facebook_campaign(campaign_id='fa_camp_0001', status='paused')
```

### Analytics & Reporting
```python
# Get campaign analytics
get_campaign_analytics(campaign_id='fa_camp_0001', date_range='last_30_days')

# Compare platforms
get_platform_performance_comparison(date_range='last_90_days', limit=20)

# Get top performers
get_top_performing_campaigns(platform='facebook', metric='roas', limit=10)
```

### Content Analysis
```python
# Get campaign content
get_campaign_content(campaign_id='fa_camp_0001')

# Analyze content performance
analyze_content_performance(platform='instagram', content_type='reel')

# Analyze hashtags
get_hashtag_analysis(platform='instagram', limit=50)
```

### Social Engagement
```python
# Get comments
get_campaign_comments(campaign_id='fa_camp_0001', sentiment_filter='positive')

# Analyze sentiment trends
analyze_sentiment_trends(platform='all', date_range='last_30_days')

# Get engagement insights
get_engagement_insights(campaign_id='fa_camp_0001')
```

## 🎯 Agent Integration Patterns

### Campaign Optimization Agent
```python
def create_optimizer_agent():
    tools = get_all_tools()
    tool_node = ToolNode(tools)
    
    # Agent can use tools to:
    # 1. Analyze current performance
    # 2. Identify optimization opportunities
    # 3. Update campaign settings
    # 4. Monitor results
```

### Content Strategy Agent
```python
def create_content_agent():
    tools = get_analysis_tools()  # Analytics + Content + Engagement
    tool_node = ToolNode(tools)
    
    # Agent can:
    # 1. Analyze content performance
    # 2. Identify best-performing hashtags
    # 3. Analyze sentiment trends
    # 4. Recommend content strategies
```

### Performance Monitoring Agent
```python
def create_monitor_agent():
    tools = get_campaign_management_tools()  # FB + IG management
    tool_node = ToolNode(tools)
    
    # Agent can:
    # 1. Monitor campaign performance
    # 2. Detect performance issues
    # 3. Automatically adjust budgets
    # 4. Pause underperforming campaigns
```

## 📊 Data Structure Examples

### Campaign Data
```json
{
  "campaign_id": "fa_camp_0001",
  "name": "Smart Marketing Solutions",
  "platform": "facebook",
  "status": "active",
  "performance": {
    "impressions": 37391,
    "clicks": 966,
    "conversions": 127,
    "revenue": 15303.81,
    "roas": 3.44
  },
  "engagement": {
    "likes": 4427,
    "shares": 264,
    "comments": 5,
    "engagement_rate": 12.91
  }
}
```

### Analytics Data
```json
{
  "campaign_id": "fa_camp_0001",
  "analysis_period": {
    "date_range": "last_7_days",
    "total_days": 7
  },
  "summary_metrics": {
    "performance": {
      "total_impressions": 15000,
      "total_clicks": 450,
      "click_through_rate": 3.0
    },
    "financial": {
      "total_spend": 1200.50,
      "total_revenue": 4500.75,
      "return_on_ad_spend": 3.75
    }
  },
  "daily_breakdown": [...]
}
```

## ✅ Verification

All tools have been tested and verified:
- ✅ 17 tools total
- ✅ 100% test success rate
- ✅ ToolNode compatibility confirmed
- ✅ Real data integration working
- ✅ Error handling implemented
- ✅ Comprehensive documentation

## 🔒 Security & Performance

- **Rate Limiting**: Built-in limits (max 50-100 records per query)
- **Error Handling**: Graceful error responses for missing data
- **Data Validation**: Input validation for all parameters
- **Performance**: Optimized queries with proper indexing
- **Logging**: Comprehensive logging for debugging

## 🚀 Ready for Production

The API tools are production-ready and can be immediately integrated into agent workflows. They provide a realistic simulation of Facebook and Instagram APIs while using actual campaign data for meaningful analysis and optimization.

**Next Steps:**
1. Import tools: `from app.tools import get_all_tools`
2. Create ToolNode: `tool_node = ToolNode(get_all_tools())`
3. Integrate with your agent workflows
4. Start optimizing campaigns! 