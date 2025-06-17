# Campaign AI - Unified System

## 🚀 Overview

Campaign AI is now a **unified system** that combines:
- **Direct REST API** for fast data display (campaigns, analytics)
- **MCP-integrated endpoints** for agentic operations (optimization, analysis, content generation)
- **Automatic server management** - one command starts everything

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Campaign AI System                       │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Next.js 15)                                     │
│  ├── Direct Data Access (fast display)                     │
│  └── MCP Tool Calls (agentic operations)                   │
├─────────────────────────────────────────────────────────────┤
│  Backend (FastAPI + MCP Server)                            │
│  ├── FastAPI App (port 8000)                               │
│  │   ├── /api/campaigns (direct DB access)                 │
│  │   ├── /api/dashboard/stats (direct DB access)           │
│  │   ├── /optimize (MCP workflow)                          │
│  │   ├── /workflow (MCP coordinator)                       │
│  │   └── /api/mcp (direct MCP tool calls)                  │
│  └── MCP Server (auto-started)                             │
│      └── 18 MCP Tools (AI, API, Search, Actions)           │
├─────────────────────────────────────────────────────────────┤
│  Database (Supabase)                                       │
│  └── campaigns table (direct access for display)           │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Key Benefits

1. **Fast Data Display**: Direct database queries for campaigns and analytics
2. **Intelligent Operations**: MCP tools for AI-powered analysis and optimization
3. **Unified Startup**: One command starts both FastAPI and MCP server
4. **Clean Architecture**: Separation of concerns between data display and agentic operations
5. **Real-time Integration**: Frontend connects to live backend data

## 🚀 Quick Start

### 1. Start the Unified System

```bash
cd Backend
python start_campaign_ai.py
```

This single command:
- ✅ Starts FastAPI server on `http://localhost:8000`
- ✅ Auto-starts MCP server in background
- ✅ Provides all endpoints for frontend
- ✅ Manages server lifecycle

### 2. Create Sample Data (Optional)

```bash
cd Backend
python create_sample_data.py
```

### 3. Start Frontend

```bash
cd ..  # Back to root
npm run dev
```

Frontend will be available at `http://localhost:3000`

## 📊 Available Endpoints

### Direct Data Access (Fast Display)
- `GET /api/campaigns` - List campaigns with filters
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/campaigns/{id}` - Campaign details

### Agentic Operations (MCP-Powered)
- `POST /optimize` - Campaign optimization workflow
- `POST /workflow` - Full coordinator workflow
- `POST /api/mcp` - Direct MCP tool calls

### System Health
- `GET /health` - System health check
- `GET /tools` - Available MCP tools
- `GET /` - API documentation

## 🛠️ MCP Tools Available

### 🧠 AI Tools
- `mcp_analyze_campaign_performance` - AI-powered performance analysis
- `mcp_generate_campaign_content` - AI content generation
- `mcp_optimize_campaign_strategy` - AI strategy optimization
- `mcp_general_marketing_assistant` - General marketing AI assistant

### 🎯 Campaign Actions
- `mcp_create_campaign` - Create new campaigns
- `mcp_update_campaign` - Update existing campaigns
- `mcp_bulk_campaign_operation` - Bulk operations
- `mcp_list_campaigns_by_criteria` - Advanced campaign filtering

### 📱 API Integration
- `mcp_get_facebook_campaigns` - Facebook API integration
- `mcp_get_facebook_campaign_details` - Facebook campaign details
- `mcp_get_instagram_campaigns` - Instagram API integration
- `mcp_get_instagram_campaign_details` - Instagram campaign details

### 🔍 Search & Analysis
- `mcp_search_campaign_data` - Vector-based campaign search
- `mcp_analyze_campaign_trends` - Trend analysis
- `mcp_tavily_search` - Web search
- `mcp_wikipedia_search` - Wikipedia search

### 🔧 System Tools
- `get_server_info` - Server information
- `test_connection` - Connection testing

## 🎨 Frontend Integration

### Data Display (Direct Access)
```typescript
// Fast, direct database access
const { campaigns, loading, error } = useCampaigns({
  platform: 'facebook',
  status: 'active'
});

const { stats } = useDashboardStats();
```

### Agentic Operations (MCP)
```typescript
// AI-powered operations
const { analyzeCampaign } = useCampaignAnalysis();
const { generateContent } = useContentGeneration();
const { optimizeStrategy } = useStrategyOptimization();

// Direct MCP tool calls
const result = await mcpClient.callMCPTool('mcp_analyze_campaign_performance', {
  campaign_data: JSON.stringify(campaign)
});
```

## 🔧 Configuration

### Environment Variables
```bash
# Supabase (required)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# OpenAI (required for AI tools)
OPENAI_API_KEY=your_openai_key

# Optional
TAVILY_API_KEY=your_tavily_key
LANGSMITH_API_KEY=your_langsmith_key
```

### Frontend Environment
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📁 File Structure

```
Backend/
├── start_campaign_ai.py          # 🚀 Unified startup script
├── create_sample_data.py         # 📊 Sample data creator
├── mcp_server.py                 # 🤖 MCP server (18 tools)
├── app/
│   ├── main.py                   # 🌐 FastAPI app with dual endpoints
│   ├── services/
│   │   └── supabase_service.py   # 🗄️ Database connection
│   ├── tools/                    # 🛠️ MCP tool implementations
│   └── agents/                   # 🤖 Agent implementations
└── requirements.txt              # 📦 Dependencies

Frontend/
├── lib/
│   ├── services/mcp-client.ts    # 🔌 Unified MCP client
│   ├── hooks/use-mcp.ts          # ⚛️ React hooks for data & MCP
│   └── types/campaign.ts         # 📝 TypeScript types
├── app/
│   ├── dashboard/page.tsx        # 📊 Real-time dashboard
│   └── campaigns/page.tsx        # 📋 Campaign management
└── components/                   # 🎨 UI components
```

## 🧹 Cleanup Completed

### Removed Files
- ❌ `Backend/run_mcp_server.py` (replaced by unified startup)
- ❌ Various duplicate/test files (cleaned up)

### Consolidated Features
- ✅ Single startup command
- ✅ Unified client service
- ✅ Clean separation of concerns
- ✅ Comprehensive error handling

## 🚦 System Status

The system now provides:
- ✅ **Fast Data Display**: Direct database access for campaigns and analytics
- ✅ **Intelligent Operations**: 18 MCP tools for AI-powered operations
- ✅ **Unified Management**: Single command starts everything
- ✅ **Real-time Integration**: Frontend connects to live backend
- ✅ **Clean Architecture**: Proper separation between display and operations
- ✅ **Error Handling**: Comprehensive error handling and fallbacks
- ✅ **Health Monitoring**: System health and connection status

## 🎉 Ready to Use!

Your Campaign AI system is now ready with:
1. **Unified startup** - one command starts everything
2. **Real data integration** - frontend shows live database data
3. **AI-powered operations** - MCP tools for intelligent campaign management
4. **Clean architecture** - fast display + powerful operations

Start the system with:
```bash
cd Backend && python start_campaign_ai.py
```

Then start the frontend and enjoy your fully integrated Campaign AI system! 🚀 