# Campaign AI Agent System Documentation

## Overview

The Campaign AI Agent System is a comprehensive, multi-agent platform built with LangChain and LangGraph that provides intelligent campaign monitoring, analysis, optimization, and reporting capabilities. The system features specialized agents, validation tools, and MCP (Model Context Protocol) integration for dynamic tool discovery and orchestration.

## System Architecture

### Core Components

1. **Specialized Agents**
   - Campaign Monitor Agent
   - Data Analysis Agent  
   - Optimization Agent
   - Reporting Agent
   - Coordinator Agent (via LangGraph workflow)

2. **Validation System**
   - Hallucination Grader
   - Enforcer Agent (loop prevention)

3. **MCP Server**
   - Dynamic tool discovery
   - Agent registration
   - Tool invocation tracking

4. **LangGraph Workflow**
   - Conditional routing
   - State management
   - Error handling

## Agent Specifications

### Campaign Monitor Agent
**Role**: Monitor campaign performance and detect issues
**Tools Assigned**:
- `get_facebook_campaigns`
- `get_facebook_campaign_details`
- `get_instagram_campaigns`
- `get_instagram_campaign_details`

**Capabilities**:
- Monitor campaigns across Facebook and Instagram
- Detect underperforming campaigns (ROAS < 3.0x, CTR < 1.0%)
- Campaign health assessment
- Performance threshold alerting

### Data Analysis Agent
**Role**: Enrich data with analytics and external research
**Tools Assigned**:
- `get_campaign_analytics`
- `get_platform_performance_comparison`
- `get_top_performing_campaigns`
- `search_campaign_data`
- `search_similar_campaigns`
- `analyze_campaign_trends`
- `wikipedia_search`
- `tavily_search`

**Capabilities**:
- Comprehensive performance analysis
- Vector database search for similar campaigns
- Market context enrichment
- Industry benchmark research
- Trend analysis and pattern identification

### Optimization Agent
**Role**: Generate and apply optimization recommendations
**Tools Assigned**:
- `update_facebook_campaign`
- `update_instagram_campaign`
- `analyze_campaign_performance`
- `generate_campaign_content`
- `optimize_campaign_strategy`
- `general_marketing_assistant`

**Capabilities**:
- Generate optimization strategies
- Create optimized content and creatives
- Apply campaign updates via APIs
- AI-powered strategic recommendations
- Risk-aware optimization with impact estimation

### Reporting Agent
**Role**: Generate comprehensive reports and summaries
**Tools Assigned**:
- `get_campaign_content`
- `analyze_content_performance`
- `get_hashtag_analysis`
- `get_campaign_comments`
- `analyze_sentiment_trends`
- `get_engagement_insights`

**Capabilities**:
- Generate comprehensive campaign reports
- Executive summaries for stakeholders
- Content engagement analysis
- Optimization results tracking
- Professional report formatting

## Validation System

### Hallucination Grader
**Purpose**: Detect hallucinations and factual inaccuracies in LLM outputs
**Method**: Uses GPT-4o-mini with low temperature for consistent evaluation
**Output**: Binary decision ("yes" if hallucination detected, "no" if valid)

**Evaluation Criteria**:
- Factual accuracy and consistency
- Logical coherence and reasoning
- Unsupported claims or made-up statistics
- Consistency with provided context/data

### Enforcer Agent
**Purpose**: Prevent infinite loops by tracking iterations and enforcing limits
**Method**: Tracks iterations per workflow and retries per operation
**Output**: Binary decision ("continue" or "stop")

**Default Limits**:
- Maximum iterations: 5
- Maximum retries per operation: 3

## LangGraph Workflow

### Workflow States
```python
class WorkflowState(TypedDict):
    workflow_id: str
    current_step: str
    campaign_ids: List[str]
    platforms: List[str]
    
    # Agent results
    monitoring_results: Dict[str, Any]
    analysis_results: Dict[str, Any]
    optimization_results: Dict[str, Any]
    reporting_results: Dict[str, Any]
    
    # Validation and control
    validation_results: Dict[str, Any]
    iteration_count: int
    should_continue: bool
    
    # Final outputs
    final_report: Dict[str, Any]
    errors: List[str]
```

### Workflow Flow
1. **Monitor Campaigns** → Check Limits
2. **Analyze Data** → Validate Output
3. **Optimize Campaigns** → Validate Output  
4. **Generate Report** → Finalize Workflow

### Conditional Routing
- **After Monitoring**: Continue if limits not exceeded, stop otherwise
- **After Analysis**: Valid → Optimize, Invalid → Re-analyze, Stop if limits exceeded
- **After Optimization**: Valid → Report, Invalid → Re-optimize, Stop if limits exceeded

## MCP Server Integration

### Tool Registration
The MCP server automatically registers all available tools:
- Campaign APIs (Facebook, Instagram)
- Analytics APIs
- Vector search tools
- LLM tools
- Content management APIs
- Social engagement APIs
- Search tools
- Validation tools

### Tool Categories
- `campaign_api`: Facebook and Instagram campaign management
- `analytics`: Performance analytics and comparisons
- `vector_search`: Pinecone vector database operations
- `llm_tools`: AI-powered analysis and content generation
- `content_management`: Content and hashtag analysis
- `social_engagement`: Engagement and sentiment analysis
- `search`: Wikipedia and web search
- `validation`: Hallucination detection and loop prevention

### Agent Registration
Agents can be registered with the MCP server for discovery:
```python
server.register_agent(
    agent_name="campaign_monitor",
    agent_instance=monitor_agent,
    capabilities=["Monitor performance", "Detect issues"]
)
```

## Usage Examples

### Running Individual Agents
```python
# Campaign Monitor
monitor_agent = CampaignMonitorAgent()
result = monitor_agent.detect_underperforming_campaigns(
    threshold_roas=3.0,
    threshold_ctr=1.0
)

# Data Analysis
analysis_agent = DataAnalysisAgent()
result = analysis_agent.find_optimization_opportunities(
    underperforming_campaigns=["campaign_123"],
    top_performers=["campaign_789"]
)

# Optimization
optimization_agent = OptimizationAgent()
result = optimization_agent.generate_optimization_strategy(
    campaign_data="ROAS 2.1x, CTR 0.8%",
    performance_issues=["Low ROAS", "Poor CTR"],
    optimization_goals=["Improve ROAS", "Increase CTR"]
)

# Reporting
reporting_agent = ReportingAgent()
result = reporting_agent.generate_campaign_report(
    campaign_ids=["campaign_123", "campaign_456"],
    report_type="comprehensive"
)
```

### Running Complete Workflow
```python
# Create workflow
workflow = create_campaign_optimization_workflow()

# Execute workflow
result = workflow.run_workflow(
    campaign_ids=["fb_001", "ig_002"],
    platforms=["facebook", "instagram"]
)
```

### Using MCP Server
```python
# Start MCP server
server = start_mcp_server(host="localhost", port=8765)

# Discover tools
tools = server.discover_tools(category="analytics")

# Invoke tool
result = server.invoke_tool(
    tool_name="get_campaign_analytics",
    campaign_id="campaign_123"
)

# Register agent
server.register_agent(
    agent_name="monitor",
    agent_instance=monitor_agent,
    capabilities=["monitoring", "detection"]
)
```

## Testing and Validation

### Test Scripts
1. **`test_agent_workflow.py`**: Tests individual agents and complete workflow
2. **`test_mcp_integration.py`**: Tests MCP server integration and tool discovery

### Running Tests
```bash
# Test agent workflow
cd Backend
python test_agent_workflow.py

# Test MCP integration
python test_mcp_integration.py
```

### Test Coverage
- Individual agent functionality
- Validation system (hallucination detection, loop prevention)
- Complete workflow execution
- MCP server tool discovery and invocation
- Error handling and recovery
- Agent registration and discovery

## Configuration

### Environment Variables
```bash
# OpenAI API
OPENAI_API_KEY=your_openai_key

# Pinecone Vector Database
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_environment

# Supabase Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Tavily Search
TAVILY_API_KEY=your_tavily_key
```

### Model Configuration
- **Default LLM**: GPT-4o-mini
- **Hallucination Grader**: GPT-4o-mini (temperature: 0.1)
- **Agent Models**: GPT-4o-mini (various temperatures)
- **Vector Embeddings**: text-embedding-3-small (1,536 dimensions)

## Best Practices

### Agent Design
1. **Single Responsibility**: Each agent has a clear, focused role
2. **Tool Assignment**: Tools are logically grouped by agent capability
3. **Error Handling**: Comprehensive error handling with graceful degradation
4. **Logging**: Detailed logging for debugging and monitoring

### Workflow Design
1. **State Management**: Clear state transitions and data flow
2. **Validation**: Output validation at critical steps
3. **Loop Prevention**: Enforcer limits to prevent infinite loops
4. **Conditional Routing**: Binary decisions for clear control flow

### MCP Integration
1. **Tool Registration**: Automatic registration with metadata
2. **Category Organization**: Logical tool categorization
3. **Call Tracking**: Complete audit trail of tool invocations
4. **Error Recovery**: Robust error handling and logging

## Performance Considerations

### Optimization Strategies
1. **Parallel Tool Calls**: Use parallel execution where possible
2. **Caching**: Cache frequently accessed data
3. **Rate Limiting**: Respect API rate limits
4. **Batch Processing**: Process multiple items together

### Monitoring
1. **Tool Call Metrics**: Track tool usage and performance
2. **Agent Performance**: Monitor agent execution times
3. **Error Rates**: Track and alert on error rates
4. **Resource Usage**: Monitor memory and CPU usage

## Future Enhancements

### Planned Features
1. **Multi-Model LLM Routing**: Intelligent routing between OpenAI, Gemini, Claude
2. **Real-Time Monitoring**: Live campaign monitoring and alerting
3. **Advanced Analytics**: Machine learning-powered insights
4. **Enterprise Dashboard**: Web-based management interface
5. **API Gateway**: RESTful API for external integrations

### Scalability Improvements
1. **Distributed Processing**: Multi-node agent execution
2. **Message Queues**: Asynchronous task processing
3. **Database Optimization**: Enhanced vector search performance
4. **Caching Layer**: Redis-based caching for improved performance

## Troubleshooting

### Common Issues
1. **API Rate Limits**: Implement exponential backoff
2. **Vector Search Timeouts**: Optimize query parameters
3. **LLM Hallucinations**: Validation system catches and handles
4. **Workflow Loops**: Enforcer prevents infinite iterations

### Debugging
1. **Enable Debug Logging**: Set log level to DEBUG
2. **Check Tool Call History**: Review MCP server call logs
3. **Validate Environment**: Ensure all API keys are configured
4. **Test Individual Components**: Isolate issues to specific agents

## Support and Maintenance

### Monitoring
- Agent performance metrics
- Tool call success rates
- Workflow completion rates
- Error tracking and alerting

### Updates
- Regular model updates
- Tool enhancement and additions
- Performance optimizations
- Security patches

This documentation provides a comprehensive guide to the Campaign AI Agent System. For additional support or questions, refer to the test scripts and code comments for detailed implementation examples. 