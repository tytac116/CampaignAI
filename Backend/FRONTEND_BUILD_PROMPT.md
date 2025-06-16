# 🚀 Campaign AI Frontend Build Prompt for Next.js 15

## 🎯 Project Overview

Build a sophisticated **Campaign AI Management Platform** frontend using **Next.js 15** that connects to a multi-agent AI system via Model Context Protocol (MCP). This is for an **AI-powered marketing agency** that specializes in intelligent campaign management across Facebook and Instagram platforms.

## 🏗️ System Architecture & Constraints

### **Backend Integration Requirements**
- **CRITICAL**: All AI functionality MUST go through MCP server at `Backend/mcp_server.py`
- **18 Available MCP Tools** across 5 categories (detailed below)
- **Multi-Agent System**: Campaign Agent (analysis) + Action Agent (database operations)
- **LangGraph Workflow**: Intelligent routing based on user intent (analysis/action/hybrid)
- **LangSmith Tracing**: All workflows are traced for observability
- **No Direct Database Access**: UI must use MCP tools for all data operations

### **Proven System Capabilities** (from live demo)
✅ **Campaign Analysis**: Performance reviews, trend analysis, optimization recommendations  
✅ **Campaign Actions**: Create, update, bulk operations (pause/activate campaigns)  
✅ **Multi-Platform**: Facebook and Instagram campaign management  
✅ **Intent Detection**: Automatically routes requests to appropriate agents  
✅ **Research Integration**: Web search + Wikipedia for market research  
✅ **Validation**: Hallucination detection and output validation  
✅ **Safety**: No delete operations, comprehensive error handling  

## 🛠️ Available MCP Tools (18 Total)

### **1. Server Management (2 tools)**
- `get_server_info()` - Server status and capabilities
- `test_connection()` - Connection health check

### **2. LLM Analysis Tools (4 tools)**
- `mcp_analyze_campaign_performance(campaign_data)` - AI-powered performance analysis
- `mcp_generate_campaign_content(campaign_type, target_audience, platform)` - Content generation
- `mcp_optimize_campaign_strategy(campaign_data, goals)` - Strategy optimization
- `mcp_general_marketing_assistant(query)` - General marketing Q&A

### **3. Vector Search & Analytics (2 tools)**
- `mcp_search_campaign_data(query, limit=5)` - Semantic campaign search
- `mcp_analyze_campaign_trends(time_period="30_days")` - Trend analysis

### **4. Platform API Tools (4 tools)**
- `mcp_get_facebook_campaigns(limit=10)` - Fetch Facebook campaigns
- `mcp_get_facebook_campaign_details(campaign_id)` - Detailed Facebook data
- `mcp_get_instagram_campaigns(limit=10)` - Fetch Instagram campaigns  
- `mcp_get_instagram_campaign_details(campaign_id)` - Detailed Instagram data

### **5. Campaign Action Tools (4 tools)**
- `mcp_create_campaign(name, platform, objective, budget_amount, ...)` - Create new campaigns
- `mcp_update_campaign(campaign_id, name, status, budget_amount, ...)` - Update campaigns
- `mcp_bulk_campaign_operation(operation, filters, updates)` - Bulk operations
- `mcp_list_campaigns_by_criteria(platform, status, min_budget, ...)` - Advanced filtering

### **6. External Search Tools (2 tools)**
- `mcp_tavily_search(query)` - Web search for market research
- `mcp_wikipedia_search(query)` - Wikipedia research

## 📊 Campaign Data Model

### **Campaign Structure**
```typescript
interface Campaign {
  campaign_id: string;
  name: string;
  platform: 'facebook' | 'instagram';
  status: 'active' | 'paused' | 'completed' | 'draft';
  objective: string; // 'conversions', 'traffic', 'awareness', etc.
  budget_type: 'daily' | 'lifetime';
  budget_amount: number;
  spend_amount: number;
  remaining_budget: number;
  
  // Performance Metrics
  impressions: number;
  clicks: number;
  conversions: number;
  revenue: number;
  ctr: number; // Click-through rate
  cpc: number; // Cost per click
  cpm: number; // Cost per mille
  cpa: number; // Cost per acquisition
  roas: number; // Return on ad spend
  
  // Targeting & Creative
  target_audience: object;
  ad_creative: object;
  campaign_settings: object;
  
  // Dates
  start_date: string;
  end_date?: string;
  created_at: string;
  updated_at: string;
  
  // Optimization
  is_optimized: boolean;
  optimization_score: number;
}
```

## 🎨 UI Requirements & Design Guidelines

### **Design Philosophy**
- **Modern AI-First Interface**: Clean, professional, data-driven
- **Guided User Experience**: Structured workflows, not free-form chaos
- **Marketing Agency Aesthetic**: Professional, trustworthy, results-focused
- **Responsive Design**: Desktop-first, mobile-friendly
- **Real-time Feedback**: Loading states, progress indicators, status updates

### **Color Palette & Branding**
- **Primary**: Deep blue (#1e40af) - Trust, professionalism
- **Secondary**: Emerald green (#059669) - Growth, success
- **Accent**: Orange (#ea580c) - Action, urgency
- **Neutral**: Gray scale (#f8fafc to #1e293b)
- **Status Colors**: Green (success), Red (error), Yellow (warning), Blue (info)

### **Typography**
- **Headings**: Inter or Poppins (bold, modern)
- **Body**: Inter or System UI (readable, clean)
- **Monospace**: JetBrains Mono (code, IDs, metrics)

## 📱 Core Application Structure

### **1. Dashboard Page (`/dashboard`)**
**Purpose**: Main overview and quick actions

**Components**:
- **KPI Cards**: Total campaigns, active spend, ROAS, conversion rate
- **Quick Actions Panel**: 
  - "Create New Campaign" (guided form)
  - "Analyze Performance" (last 30 days)
  - "Bulk Operations" (pause underperformers)
- **Recent Activity Feed**: Latest campaign changes, optimizations
- **Performance Chart**: Spend vs Revenue over time
- **Platform Distribution**: Facebook vs Instagram breakdown

**MCP Integration**:
- Use `mcp_list_campaigns_by_criteria()` for overview data
- Use `mcp_analyze_campaign_trends()` for charts
- Use `mcp_analyze_campaign_performance()` for insights

### **2. Campaigns Page (`/campaigns`)**
**Purpose**: Campaign management and operations

**Components**:
- **Filter Panel**: Platform, status, budget range, performance metrics
- **Campaign Table**: 
  - Columns: Name, Platform, Status, Budget, Spend, CTR, ROAS, Actions
  - Sortable, searchable, paginated
  - Bulk selection for operations
- **Action Buttons**: Create, Edit, Pause/Resume, Analyze
- **Bulk Operations Modal**: 
  - Pause campaigns with CTR < X%
  - Increase budget for high ROAS campaigns
  - Update targeting for specific criteria

**MCP Integration**:
- Use `mcp_list_campaigns_by_criteria()` with filters
- Use `mcp_bulk_campaign_operation()` for bulk actions
- Use `mcp_update_campaign()` for individual updates

### **3. Campaign Creation Wizard (`/campaigns/create`)**
**Purpose**: Guided campaign creation process

**Steps**:
1. **Platform Selection**: Facebook or Instagram
2. **Campaign Basics**: Name, objective, budget type
3. **Budget & Schedule**: Amount, start/end dates
4. **Audience Targeting**: Demographics, interests (guided form)
5. **Creative Assets**: Ad copy, images (upload/generate)
6. **Review & Launch**: Summary, validation, creation

**MCP Integration**:
- Use `mcp_generate_campaign_content()` for content suggestions
- Use `mcp_tavily_search()` for audience research
- Use `mcp_create_campaign()` for final creation

### **4. Analytics & Insights Page (`/analytics`)**
**Purpose**: Deep performance analysis and reporting

**Components**:
- **Time Period Selector**: Last 7/30/90 days, custom range
- **Performance Dashboard**: 
  - Spend trends, conversion funnels, ROAS analysis
  - Platform comparison charts
  - Top/bottom performing campaigns
- **AI Insights Panel**: 
  - Automated performance analysis
  - Optimization recommendations
  - Trend predictions
- **Export Options**: PDF reports, CSV data

**MCP Integration**:
- Use `mcp_analyze_campaign_performance()` for insights
- Use `mcp_analyze_campaign_trends()` for trend data
- Use `mcp_optimize_campaign_strategy()` for recommendations

### **5. AI Chat Assistant (`/chat` + Sidebar)**
**Purpose**: Natural language campaign management

**Components**:
- **Chat Interface**: Message history, typing indicators
- **Quick Actions**: Pre-defined prompts for common tasks
- **Context Panel**: Current campaign context, recent actions
- **Intent Indicators**: Show detected intent (analysis/action/hybrid)

**Example Prompts**:
- "Show me all Facebook campaigns with ROAS below 2.0"
- "Create a new Instagram campaign for eco-friendly products"
- "Pause all campaigns spending more than $100 daily with CTR under 1%"
- "Generate a performance report for last month"

**MCP Integration**:
- Send natural language to workflow via MCP
- Display workflow progress and results
- Show LangSmith trace links for debugging

### **6. Reports Page (`/reports`)**
**Purpose**: Generate and manage reports

**Components**:
- **Report Templates**: 
  - Weekly Performance Summary
  - Monthly Campaign Review
  - Platform Comparison Report
  - ROI Analysis Report
- **Custom Report Builder**: 
  - Select metrics, time periods, filters
  - Preview before generation
- **Report History**: Previously generated reports
- **Export Options**: PDF, Excel, PowerPoint

**MCP Integration**:
- Use `mcp_analyze_campaign_performance()` for report data
- Use `mcp_general_marketing_assistant()` for insights
- Use multiple tools to compile comprehensive reports

## 🔧 Technical Implementation

### **Tech Stack**
- **Framework**: Next.js 15 (App Router)
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: Zustand or React Query
- **Charts**: Recharts or Chart.js
- **Forms**: React Hook Form + Zod validation
- **Icons**: Lucide React or Heroicons
- **PDF Generation**: jsPDF or Puppeteer

### **MCP Integration Pattern**
```typescript
// MCP Client Service
class MCPClient {
  async callTool(toolName: string, params: object) {
    const response = await fetch('/api/mcp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tool: toolName, params })
    });
    return response.json();
  }
}

// Usage in components
const { data, loading, error } = useMCPTool('mcp_list_campaigns_by_criteria', {
  platform: 'facebook',
  status: 'active',
  limit: 20
});
```

### **API Routes Structure**
- `/api/mcp` - Main MCP proxy endpoint
- `/api/campaigns` - Campaign CRUD operations (via MCP)
- `/api/analytics` - Analytics data (via MCP)
- `/api/chat` - Chat workflow endpoint
- `/api/reports` - Report generation

### **State Management**
```typescript
interface AppState {
  campaigns: Campaign[];
  filters: CampaignFilters;
  selectedCampaigns: string[];
  chatHistory: ChatMessage[];
  currentWorkflow?: WorkflowStatus;
}
```

## 🎯 Guided User Flows

### **Flow 1: Campaign Performance Review**
1. User clicks "Analyze Performance" on dashboard
2. System shows time period selector (default: 30 days)
3. Triggers `mcp_analyze_campaign_performance()` workflow
4. Shows loading with progress indicators
5. Displays AI-generated insights with charts
6. Offers action buttons: "Optimize", "Create Report", "Export"

### **Flow 2: Bulk Campaign Optimization**
1. User navigates to Campaigns page
2. Applies filters (e.g., "CTR < 1.5%")
3. System shows matching campaigns in table
4. User selects "Bulk Operations" → "Pause Underperformers"
5. Confirmation modal with impact preview
6. Triggers `mcp_bulk_campaign_operation()` workflow
7. Shows real-time progress and results

### **Flow 3: AI-Assisted Campaign Creation**
1. User starts Campaign Creation Wizard
2. System asks for campaign goals and target audience
3. Uses `mcp_tavily_search()` for market research
4. Generates content suggestions via `mcp_generate_campaign_content()`
5. User reviews and customizes suggestions
6. System validates and creates via `mcp_create_campaign()`
7. Shows success with campaign details and next steps

## 🚫 System Limitations & Constraints

### **What the System CAN Do**:
✅ Create, update, and manage campaigns  
✅ Analyze performance and generate insights  
✅ Bulk operations (pause, activate, update budgets)  
✅ Generate marketing content and strategies  
✅ Search and filter campaigns by criteria  
✅ Conduct market research via web search  
✅ Generate comprehensive reports  
✅ Optimize campaign strategies  
✅ Multi-platform management (Facebook + Instagram)  

### **What the System CANNOT Do**:
❌ Delete campaigns (safety constraint)  
❌ Direct database access (must use MCP tools)  
❌ Real-time bidding or automated budget changes  
❌ Image/video processing or generation  
❌ Email marketing or other platforms beyond FB/IG  
❌ User authentication (focus on campaign management)  
❌ Financial transactions or payment processing  

### **UI Constraints**:
- **No Free-Form Database Queries**: All data access via MCP tools
- **Guided Workflows Only**: Structured forms, not open-ended inputs
- **Limited Bulk Operations**: Only pause, activate, budget updates
- **Platform Restriction**: Facebook and Instagram only
- **Read-Heavy Interface**: More analysis than creation

## 📋 Component Library Requirements

### **Core Components Needed**:
- `CampaignCard` - Campaign overview with key metrics
- `CampaignTable` - Sortable, filterable campaign list
- `MetricCard` - KPI display with trend indicators
- `FilterPanel` - Advanced filtering interface
- `BulkOperationModal` - Bulk action confirmation
- `CampaignWizard` - Multi-step campaign creation
- `ChatInterface` - AI assistant chat
- `ReportBuilder` - Custom report configuration
- `PerformanceChart` - Various chart types for metrics
- `LoadingWorkflow` - Workflow progress indicator

### **Data Visualization Components**:
- Line charts for trends (spend, ROAS over time)
- Bar charts for comparisons (platform performance)
- Pie charts for distribution (budget allocation)
- Funnel charts for conversion analysis
- Heatmaps for performance matrices

## 🔄 Workflow Integration

### **Chat-to-Workflow Pattern**:
```typescript
// User types: "Show me underperforming Facebook campaigns"
// System detects intent: "analysis"
// Routes to Campaign Agent via MCP
// Returns structured data + insights
// UI renders results in appropriate format
```

### **Action Confirmation Pattern**:
```typescript
// User requests: "Pause all campaigns with CTR < 1%"
// System detects intent: "action"
// Shows preview of affected campaigns
// Requires explicit user confirmation
// Executes via Action Agent
// Shows real-time progress and results
```

## 🎨 Mock Data Structure

### **For Development Phase**:
```typescript
// Use realistic mock data that matches the actual schema
const mockCampaigns: Campaign[] = [
  {
    campaign_id: "facebook_eco_bottles_1703123456",
    name: "Eco-Friendly Water Bottles - Holiday Sale",
    platform: "facebook",
    status: "active",
    objective: "conversions",
    budget_amount: 50.0,
    spend_amount: 32.45,
    ctr: 2.3,
    roas: 4.2,
    // ... full structure
  }
];
```

## 🚀 Development Priorities

### **Phase 1: Core Infrastructure**
1. Next.js 15 setup with App Router
2. MCP client integration
3. Basic dashboard with mock data
4. Campaign table with filtering

### **Phase 2: Campaign Management**
1. Campaign creation wizard
2. Bulk operations interface
3. Performance analytics
4. AI chat integration

### **Phase 3: Advanced Features**
1. Report generation
2. Advanced analytics
3. Workflow progress tracking
4. Export functionality

## 🔗 Integration Checklist

### **MCP Connection Requirements**:
- [ ] MCP server running on `Backend/mcp_server.py`
- [ ] All 18 tools accessible via API proxy
- [ ] Proper error handling for tool failures
- [ ] Loading states for long-running workflows
- [ ] LangSmith trace link integration

### **Data Flow Validation**:
- [ ] Campaign CRUD operations work via MCP
- [ ] Bulk operations execute correctly
- [ ] Analytics data renders properly
- [ ] Chat workflows complete successfully
- [ ] Report generation functions

## 🎯 Success Criteria

### **User Experience**:
- Users can manage campaigns without technical knowledge
- All actions are guided and validated
- Real-time feedback for all operations
- Professional, agency-quality interface

### **Technical Performance**:
- Fast loading times (<2s for most operations)
- Responsive design across devices
- Proper error handling and recovery
- Seamless MCP integration

### **Business Value**:
- Reduces campaign management time by 70%
- Increases campaign performance through AI insights
- Provides professional reporting capabilities
- Scales to handle 100+ campaigns efficiently

---

**🎉 Build a production-ready Campaign AI frontend that showcases the power of multi-agent AI systems while maintaining a guided, professional user experience suitable for marketing agencies and campaign managers.**
