# CampaignAI Backend

A comprehensive campaign optimization platform with Facebook and Instagram API simulation tools for AI agents.

## 📁 Directory Structure

```
Backend/
├── app/                          # Main application code
│   ├── agents/                   # LangGraph agent implementations
│   │   ├── coordinator.py        # Agent coordination logic
│   │   ├── graph.py              # Agent workflow graphs
│   │   ├── nodes.py              # Agent node implementations
│   │   └── state.py              # Agent state management
│   ├── api/                      # FastAPI endpoints
│   ├── core/                     # Core configuration and utilities
│   ├── data/                     # Data generation and seeding utilities
│   │   ├── ai_data_generator.py  # AI-powered data generation
│   │   ├── data_generator.py     # Campaign data generator
│   │   ├── supabase_seeder.py    # Database seeding utilities
│   │   └── seed_data.py          # Data seeding scripts
│   ├── models/                   # Database models
│   ├── services/                 # Business logic services
│   │   ├── mcp_server.py         # MCP server implementation
│   │   └── supabase_service.py   # Supabase database service
│   ├── tools/                    # LangChain/LangGraph tools
│   │   ├── facebook_campaign_api.py    # Facebook campaign management
│   │   ├── instagram_campaign_api.py   # Instagram campaign management
│   │   ├── analytics_api.py            # Analytics and reporting
│   │   ├── content_management_api.py   # Content analysis tools
│   │   ├── social_engagement_api.py    # Social engagement tools
│   │   ├── search_tools.py             # Web search tools
│   │   └── __init__.py                 # Tools registry
│   ├── workers/                  # Background workers
│   └── main.py                   # FastAPI application entry point
├── data/                         # Data storage
│   └── csv/                      # CSV data files
│       ├── campaigns.csv         # Campaign data (500 records)
│       ├── campaign_metrics.csv  # Daily metrics (7,000 records)
│       ├── campaign_content.csv  # Content data (500 records)
│       └── campaign_comments.csv # Comments data (2,500 records)
├── docs/                         # Documentation
│   └── guides/                   # User guides
│       ├── API_TOOLS_GUIDE.md    # Comprehensive API tools guide
│       └── SETUP_INSTRUCTIONS.md # Setup instructions
├── scripts/                      # Utility scripts
│   ├── database/                 # Database management scripts
│   │   ├── create_tables.sql     # Database schema
│   │   ├── disable_rls.sql       # Disable row-level security
│   │   ├── init_database.py      # Database initialization
│   │   └── seed_sample_data.py   # Sample data seeding
│   ├── data_generation/          # Data generation scripts
│   │   ├── generate_enhanced_csv_with_llm.py  # LLM-powered data generation
│   │   └── generate_fast_csv.py              # Fast data generation
│   └── testing/                  # Test scripts
│       ├── test_supabase_client.py     # Supabase connection tests
│       ├── test_api_simulators.py      # API simulator tests
│       ├── test_supabase_data.py       # Data validation tests
│       ├── facebook_api_sim.py         # Legacy Facebook API simulator
│       └── instagram_api_sim.py        # Legacy Instagram API simulator
├── tests/                        # Unit tests
│   ├── test_api.py              # API endpoint tests
│   └── __init__.py
├── alembic/                      # Database migrations
├── requirements.txt              # Python dependencies
├── alembic.ini                   # Alembic configuration
└── .gitignore                    # Git ignore rules
```

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Supabase credentials
```

### 2. Database Setup
```bash
# Initialize database
python scripts/database/init_database.py

# Seed with sample data
python scripts/database/seed_sample_data.py
```

### 3. Test API Tools
```bash
# Test Supabase connection
python scripts/testing/test_supabase_client.py

# Test API simulators
python scripts/testing/test_api_simulators.py
```

### 4. Run Application
```bash
# Start FastAPI server
python app/main.py
```

## 🔧 API Tools for Agents

The system provides 17 production-ready tools for LangChain/LangGraph agents:

### Facebook & Instagram Campaign Management
- **Facebook Tools**: `get_facebook_campaigns`, `get_facebook_campaign_details`, `update_facebook_campaign`
- **Instagram Tools**: `get_instagram_campaigns`, `get_instagram_campaign_details`, `update_instagram_campaign`

### Analytics & Reporting
- `get_campaign_analytics` - Detailed performance analytics
- `get_platform_performance_comparison` - Facebook vs Instagram comparison
- `get_top_performing_campaigns` - Rank campaigns by metrics

### Content Management
- `get_campaign_content` - Retrieve campaign content details
- `analyze_content_performance` - Analyze content type performance
- `get_hashtag_analysis` - Hashtag effectiveness analysis

### Social Engagement
- `get_campaign_comments` - Comments with sentiment filtering
- `analyze_sentiment_trends` - Sentiment pattern analysis
- `get_engagement_insights` - Comprehensive engagement metrics

### Web Search
- `wikipedia_search` - Wikipedia information lookup
- `tavily_search` - Web search using Tavily API

## 📊 Data Overview

- **Campaigns**: 500 records (250 Facebook, 250 Instagram)
- **Metrics**: 7,000 daily performance records
- **Content**: 500 content records with hashtags and descriptions
- **Comments**: 2,500 user comments with sentiment analysis

## 🎯 Agent Integration

```python
from app.tools import get_all_tools
from langgraph.prebuilt import ToolNode

# Get all 17 tools
tools = get_all_tools()

# Create ToolNode for agents
tool_node = ToolNode(tools)

# Use in LangGraph workflows
from langgraph.graph import StateGraph
workflow = StateGraph(YourState)
workflow.add_node("tools", tool_node)
```

## 📚 Documentation

- **[API Tools Guide](docs/guides/API_TOOLS_GUIDE.md)** - Comprehensive guide to all API tools
- **[Setup Instructions](docs/guides/SETUP_INSTRUCTIONS.md)** - Detailed setup instructions

## 🧪 Testing

```bash
# Test database connection
python scripts/testing/test_supabase_client.py

# Test API tools
python scripts/testing/test_api_simulators.py

# Run unit tests
python -m pytest tests/
```

## 🔒 Security

- Environment variables for sensitive data
- Input validation on all API endpoints
- Rate limiting on tool usage
- Error handling for graceful failures

## 📈 Performance

- Optimized database queries
- Built-in pagination and filtering
- Efficient data structures
- Minimal memory footprint

## 🚀 Production Ready

The system is production-ready with:
- ✅ Comprehensive error handling
- ✅ Full test coverage
- ✅ Clean, organized codebase
- ✅ Detailed documentation
- ✅ LangGraph/LangChain compatibility
- ✅ Real campaign data integration

## 🤝 Contributing

1. Follow the organized directory structure
2. Add tests for new features
3. Update documentation
4. Ensure all tools work with ToolNode

## 📄 License

[Your License Here] 