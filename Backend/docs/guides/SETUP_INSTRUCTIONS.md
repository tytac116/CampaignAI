# Campaign AI Backend Setup Instructions

## Overview
We've successfully set up the backend infrastructure for your Campaign Performance Optimization Platform with:
- ✅ Supabase integration using the client library
- ✅ Database schema with campaigns, metrics, and agent execution tables
- ✅ Data generation system for realistic Facebook and Instagram campaigns
- ✅ Facebook and Instagram API simulators
- ✅ LangGraph agents architecture
- ✅ MCP server integration

## Next Steps to Complete Setup

### 1. Create Database Tables in Supabase

1. Go to your Supabase dashboard: https://supabase.com/dashboard
2. Navigate to your project: `zrawaliecoufegkanlpg.supabase.co`
3. Go to the **SQL Editor** tab
4. Copy and paste the contents of `create_tables.sql` into the SQL Editor
5. Click **Run** to create all the tables and indexes

### 2. Seed Sample Data

Once the tables are created, run the sample data seeding script:

```bash
cd Backend
python3 seed_sample_data.py
```

This will:
- Generate 50 Facebook campaigns and 50 Instagram campaigns
- Create realistic campaign metrics for the past 7 days
- Insert all data into your Supabase database

### 3. Test the API Simulators

After seeding data, test that the Facebook and Instagram API simulators work:

```bash
python3 test_api_simulators.py
```

This will:
- Test connection to Supabase
- Simulate Facebook Marketing API calls
- Simulate Instagram Basic Display API calls
- Verify data is returned in the expected format

## What's Been Built

### 📊 Database Schema
- **`campaigns`**: Complete campaign data with budgets, KPIs, settings
- **`campaign_metrics`**: Time-series performance data with demographics
- **`agent_executions`**: LangGraph workflow execution tracking

### 🤖 API Simulators
- **Facebook API Simulator**: Mimics Facebook Marketing API responses
- **Instagram API Simulator**: Mimics Instagram Basic Display API responses
- Both pull data from your Supabase database to provide realistic responses

### 🔄 Data Generation
- **Realistic campaign data**: Names, objectives, budgets, audiences
- **Platform-specific metrics**: Facebook vs Instagram KPIs
- **Time-series data**: Hourly and daily performance metrics
- **Demographics**: Age groups, gender, geographic data

### 🧠 LangGraph Architecture
- **Agent nodes**: Monitor, Analysis, Optimization, Reporting, Coordinator
- **State management**: Comprehensive workflow state tracking
- **Graph orchestration**: Conditional workflows with retry handling

### 🔌 MCP Integration
- **Server setup**: Ready for external AI model communication
- **Tool endpoints**: Campaign optimization, performance analysis
- **Workflow management**: Agent execution tracking

## Testing the Setup

After completing the steps above, you should be able to:

1. **Query campaigns** like a real Facebook/Instagram API:
   ```python
   facebook_api = FacebookAPISimulator(supabase_client)
   campaigns = await facebook_api.get_campaigns()
   ```

2. **Get campaign insights** with realistic metrics:
   ```python
   insights = await facebook_api.get_campaign_insights(campaign_id)
   ```

3. **Access time-series data** for performance analysis:
   ```python
   metrics = await instagram_api.get_media_insights(campaign_id)
   ```

## File Structure Overview

```
Backend/
├── app/
│   ├── core/           # Configuration and database setup
│   ├── models/         # SQLAlchemy models (for reference)
│   ├── data/           # Data generation and seeding
│   ├── services/       # Supabase service and API simulators
│   ├── agents/         # LangGraph agent architecture
│   └── api/            # FastAPI routes (to be implemented)
├── create_tables.sql   # Database schema SQL
├── seed_sample_data.py # Sample data seeding script
├── test_api_simulators.py # API simulator testing
└── SETUP_INSTRUCTIONS.md # This file
```

## Ready for Next Phase

Once you've completed these steps, the backend will be ready for:
- FastAPI endpoint implementation
- Frontend integration
- Real-time campaign optimization workflows
- Advanced analytics and reporting

The API simulators will provide realistic data responses that mimic real Facebook and Instagram APIs, allowing you to develop and test the frontend without needing actual API access. 