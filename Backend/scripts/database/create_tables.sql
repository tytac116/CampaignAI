-- Create campaigns table
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('facebook', 'instagram')),
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'archived', 'deleted')),
    objective VARCHAR(100) NOT NULL,
    
    -- Budget and Financial Data
    budget_type VARCHAR(50) NOT NULL DEFAULT 'daily' CHECK (budget_type IN ('daily', 'lifetime')),
    budget_amount DECIMAL(10, 2) NOT NULL,
    spend_amount DECIMAL(10, 2) DEFAULT 0,
    remaining_budget DECIMAL(10, 2) DEFAULT 0,
    
    -- Performance Metrics
    impressions BIGINT DEFAULT 0,
    clicks BIGINT DEFAULT 0,
    conversions BIGINT DEFAULT 0,
    revenue DECIMAL(10, 2) DEFAULT 0,
    
    -- KPIs
    ctr DECIMAL(5, 4) DEFAULT 0,
    cpc DECIMAL(10, 2) DEFAULT 0,
    cpm DECIMAL(10, 2) DEFAULT 0,
    cpa DECIMAL(10, 2) DEFAULT 0,
    roas DECIMAL(10, 4) DEFAULT 0,
    
    -- Optimization Flags
    is_optimized BOOLEAN DEFAULT FALSE,
    optimization_score DECIMAL(3, 2) DEFAULT 0,
    last_optimization_date TIMESTAMP,
    
    -- Campaign Settings
    target_audience JSONB,
    ad_creative JSONB,
    campaign_settings JSONB,
    
    -- Timestamps
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create campaign_metrics table
CREATE TABLE IF NOT EXISTS campaign_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id VARCHAR(255) NOT NULL,
    metric_date DATE NOT NULL,
    hour_of_day INTEGER CHECK (hour_of_day >= 0 AND hour_of_day <= 23),
    
    -- Core Metrics
    impressions BIGINT DEFAULT 0,
    clicks BIGINT DEFAULT 0,
    conversions BIGINT DEFAULT 0,
    spend DECIMAL(10, 2) DEFAULT 0,
    revenue DECIMAL(10, 2) DEFAULT 0,
    
    -- Engagement Metrics
    likes BIGINT DEFAULT 0,
    shares BIGINT DEFAULT 0,
    comments BIGINT DEFAULT 0,
    saves BIGINT DEFAULT 0,
    video_views BIGINT DEFAULT 0,
    
    -- Demographics
    demographics JSONB,
    geo_data JSONB,
    device_data JSONB,
    
    -- Quality Scores
    relevance_score DECIMAL(3, 2) DEFAULT 0,
    quality_score DECIMAL(3, 2) DEFAULT 0,
    engagement_rate DECIMAL(5, 4) DEFAULT 0,
    
    -- Composite Indexes
    performance_index DECIMAL(5, 2) DEFAULT 0,
    efficiency_index DECIMAL(5, 2) DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(campaign_id, metric_date, hour_of_day)
);

-- Create agent_executions table
CREATE TABLE IF NOT EXISTS agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id VARCHAR(255) UNIQUE NOT NULL,
    agent_type VARCHAR(100) NOT NULL CHECK (agent_type IN ('monitor', 'analysis', 'optimization', 'reporting', 'coordinator')),
    workflow_id VARCHAR(255),
    
    -- Execution Details
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    
    -- Performance Metrics
    execution_time_ms INTEGER DEFAULT 0,
    tokens_used INTEGER DEFAULT 0,
    api_calls_made INTEGER DEFAULT 0,
    
    -- Metadata
    metadata JSONB,
    
    -- Timestamps
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_campaigns_platform ON campaigns(platform);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_created_at ON campaigns(created_at);
CREATE INDEX IF NOT EXISTS idx_metrics_campaign_date ON campaign_metrics(campaign_id, metric_date DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_performance ON campaign_metrics(performance_index DESC);
CREATE INDEX IF NOT EXISTS idx_agents_type_status ON agent_executions(agent_type, status);
CREATE INDEX IF NOT EXISTS idx_agents_workflow ON agent_executions(workflow_id); 