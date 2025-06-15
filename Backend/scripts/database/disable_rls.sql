-- Disable Row Level Security for all campaign tables
-- Run this in your Supabase SQL Editor

-- Disable RLS on campaigns table
ALTER TABLE campaigns DISABLE ROW LEVEL SECURITY;

-- Disable RLS on campaign_metrics table  
ALTER TABLE campaign_metrics DISABLE ROW LEVEL SECURITY;

-- Disable RLS on agent_executions table
ALTER TABLE agent_executions DISABLE ROW LEVEL SECURITY;

-- Verify RLS is disabled (optional check)
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE tablename IN ('campaigns', 'campaign_metrics', 'agent_executions'); 