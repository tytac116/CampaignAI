# Vector Search Tools for Campaign AI

## Overview

This document describes the vector search tools implementation that provides powerful semantic search capabilities over campaign data using Pinecone vector database with BM25 reranking for enhanced relevance.

## Architecture

### Components

1. **Vector Database**: Pinecone index `campaign-optimization` with 1,536 dimensions
2. **Embeddings**: OpenAI `text-embedding-3-small` model
3. **Reranking**: BM25 algorithm for hybrid search (70% vector similarity + 30% BM25)
4. **Data Sources**: 1,286 documents across 4 types:
   - 500 Campaign documents
   - 500 Content documents  
   - 86 Metrics documents (30-day trend analysis)
   - 200 Comments documents (sentiment analysis)

### Key Features

- **Semantic Search**: Natural language queries over campaign data
- **Hybrid Scoring**: Combines vector similarity with BM25 keyword matching
- **Rich Metadata**: Performance tiers, sentiment classifications, platform filters
- **Multiple Document Types**: Campaigns, content, metrics, and comments
- **Advanced Filtering**: Platform, status, performance tier, sentiment filters

## Available Tools

### 1. `search_campaign_data`

**Purpose**: Primary semantic search tool for campaign data analysis

**Parameters**:
- `query` (str): Natural language search query
- `filters` (str, optional): JSON string of metadata filters
- `top_k` (int): Number of results (default: 5, max: 20)
- `doc_types` (str, optional): Comma-separated document types

**Examples**:
```python
# Basic search
search_campaign_data.invoke({
    "query": "high performing Facebook campaigns with positive sentiment",
    "top_k": 3
})

# Filtered search
search_campaign_data.invoke({
    "query": "engagement rate optimization strategies",
    "filters": '{"platform": "instagram"}',
    "doc_types": "campaign,content"
})
```

**Use Cases**:
- Find high-performing campaigns by metrics
- Analyze content strategies by type
- Search for sentiment patterns
- Filter by platform or status

### 2. `search_similar_campaigns`

**Purpose**: Find campaigns similar to a reference campaign

**Parameters**:
- `campaign_id` (str): Reference campaign ID
- `similarity_type` (str): Type of similarity ("performance", "content", "audience", "overall")
- `top_k` (int): Number of similar campaigns (default: 5, max: 15)

**Examples**:
```python
# Find performance-similar campaigns
search_similar_campaigns.invoke({
    "campaign_id": "fa_camp_0173",
    "similarity_type": "performance",
    "top_k": 5
})
```

**Use Cases**:
- Campaign benchmarking
- Strategy replication
- Performance analysis
- Audience targeting insights

### 3. `analyze_campaign_trends`

**Purpose**: Analyze trends and patterns across campaigns

**Parameters**:
- `metric` (str): Trend metric ("performance", "engagement", "sentiment", "content", "budget")
- `time_period` (str): Analysis period (default: "last_30_days")
- `platform` (str, optional): Platform filter ("facebook", "instagram")
- `top_k` (int): Number of insights (default: 10)

**Examples**:
```python
# Performance trend analysis
analyze_campaign_trends.invoke({
    "metric": "performance",
    "platform": "facebook",
    "top_k": 5
})

# Sentiment trend analysis
analyze_campaign_trends.invoke({
    "metric": "sentiment"
})
```

**Use Cases**:
- Performance trend identification
- Sentiment pattern analysis
- Content type effectiveness
- Budget optimization insights

## Data Structure

### Campaign Documents
- **Content**: Comprehensive campaign overview with performance metrics
- **Metadata**: Platform, status, performance tier, ROAS, CTR, engagement rate, sentiment
- **Performance Tiers**: high_performer, medium_performer, low_performer
- **Budget Tiers**: high_budget, medium_budget, low_budget

### Content Documents
- **Content**: Rich content analysis with creative strategies
- **Metadata**: Content type, complexity classification, performance metrics
- **Content Types**: video, image, carousel, story, reel, podcast, infographic, live, testimonial, demo
- **Complexity**: simple, moderate, complex

### Metrics Documents
- **Content**: 30-day performance trend analysis
- **Metadata**: Aggregated metrics, stability analysis, best/worst performing days
- **Trend Analysis**: Performance patterns, optimization opportunities

### Comments Documents
- **Content**: Sentiment distribution and engagement analysis
- **Metadata**: Sentiment scores, engagement metrics, theme extraction
- **Sentiment**: positive, negative, neutral with confidence scores

## Integration with Agent System

### Tool Registration

The vector search tools are automatically registered in the agent system:

```python
# In Backend/app/tools/__init__.py
from .vector_search_tools import get_vector_search_tools

def get_all_tools():
    tools = []
    tools.extend(get_vector_search_tools())  # Vector search tools
    tools.extend(get_search_tools())         # Web search tools
    tools.extend(get_facebook_campaign_tools())  # Facebook API tools
    # ... other tools
    return tools
```

### Usage in Agents

Agents can use these tools for:

1. **Performance Analysis**: Find top-performing campaigns and analyze success factors
2. **Content Optimization**: Identify effective content strategies and creative approaches
3. **Sentiment Monitoring**: Track sentiment trends and identify issues
4. **Competitive Analysis**: Compare campaign performance and strategies
5. **Trend Identification**: Spot emerging patterns and optimization opportunities

## Performance Metrics

### Search Performance
- **Processing Rate**: 5.5 documents/second during ingestion
- **Search Latency**: ~200-500ms per query
- **Hybrid Scoring**: 70% vector similarity + 30% BM25 relevance
- **Accuracy**: High relevance with semantic understanding

### Data Coverage
- **Total Documents**: 1,286 documents
- **Campaign Coverage**: 500 campaigns with full performance data
- **Content Analysis**: 500 content pieces with creative insights
- **Trend Analysis**: 86 metrics documents with 30-day trends
- **Sentiment Analysis**: 200 comment analyses with sentiment scores

## Technical Implementation

### Dependencies
```python
langchain-pinecone==0.2.0
langchain-openai==0.2.8
rank-bm25==0.2.2
pinecone-client==5.0.1
```

### Environment Variables
```bash
PINECONE_API_KEY=your_pinecone_api_key
OPENAI_API_KEY=your_openai_api_key
```

### Error Handling
- Connection retry logic for Pinecone
- Graceful degradation for missing metadata
- Input validation and sanitization
- Comprehensive logging and monitoring

## Testing

The implementation includes comprehensive tests covering:

- Basic semantic search functionality
- Filtered search with metadata constraints
- Similar campaign discovery
- Trend analysis across different metrics
- Content-specific searches
- Error handling and edge cases

**Test Results**: All tests pass successfully with realistic campaign data queries.

## Future Enhancements

1. **Real-time Updates**: Implement incremental data updates
2. **Advanced Analytics**: Add more sophisticated trend analysis
3. **Personalization**: User-specific search preferences
4. **Multi-modal Search**: Support for image and video content search
5. **Performance Optimization**: Caching and query optimization

## Conclusion

The vector search tools provide a powerful foundation for semantic analysis of campaign data, enabling agents to:

- Perform natural language queries over complex campaign datasets
- Identify patterns and trends across multiple dimensions
- Make data-driven recommendations for campaign optimization
- Support advanced analytics and competitive intelligence

The hybrid search approach (vector + BM25) ensures both semantic understanding and keyword relevance, while the rich metadata structure enables precise filtering and analysis capabilities. 