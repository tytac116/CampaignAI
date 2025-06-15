"""
Supabase-specific data seeding utility for populating the database with campaign data.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from supabase import Client
import json

logger = logging.getLogger(__name__)


class SupabaseDataSeeder:
    """Utility class for seeding database with campaign data using Supabase."""
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.batch_size = 100
        self.total_inserted = 0
    
    def seed_campaigns(self, campaigns_data: List[Dict[str, Any]], platform: str) -> bool:
        """Seed campaign data into the database."""
        try:
            logger.info(f"Starting to seed {len(campaigns_data)} {platform} campaigns")
            
            # Process in batches
            for i in range(0, len(campaigns_data), self.batch_size):
                batch = campaigns_data[i:i + self.batch_size]
                if not self._insert_campaign_batch(batch, platform):
                    return False
                
                self.total_inserted += len(batch)
                logger.info(f"Inserted {self.total_inserted}/{len(campaigns_data)} campaigns")
            
            logger.info(f"Successfully seeded {len(campaigns_data)} {platform} campaigns")
            return True
            
        except Exception as e:
            logger.error(f"Failed to seed campaigns: {e}")
            return False
    
    def _insert_campaign_batch(self, batch: List[Dict[str, Any]], platform: str) -> bool:
        """Insert a batch of campaigns."""
        try:
            # Convert data to Supabase format
            supabase_data = []
            for campaign_data in batch:
                supabase_record = {
                    'campaign_id': campaign_data['campaign_id'],
                    'name': campaign_data['name'],
                    'platform': platform,
                    'status': campaign_data['status'],
                    'objective': campaign_data['objective'],
                    'budget_type': campaign_data['budget_type'],
                    'budget_amount': float(campaign_data['budget_amount']),
                    'spend_amount': float(campaign_data['spend_amount']),
                    'remaining_budget': float(campaign_data['remaining_budget']),
                    'impressions': int(campaign_data['impressions']),
                    'clicks': int(campaign_data['clicks']),
                    'conversions': int(campaign_data['conversions']),
                    'revenue': float(campaign_data['revenue']),
                    'ctr': float(campaign_data['ctr']),
                    'cpc': float(campaign_data['cpc']),
                    'cpm': float(campaign_data['cpm']),
                    'cpa': float(campaign_data['cpa']),
                    'roas': float(campaign_data['roas']),
                    'is_optimized': campaign_data['is_optimized'],
                    'optimization_score': float(campaign_data['optimization_score']),
                    'target_audience': json.dumps(campaign_data['target_audience']) if isinstance(campaign_data['target_audience'], dict) else campaign_data['target_audience'],
                    'ad_creative': json.dumps(campaign_data['ad_creative']) if isinstance(campaign_data['ad_creative'], dict) else campaign_data['ad_creative'],
                    'campaign_settings': json.dumps(campaign_data['campaign_settings']) if isinstance(campaign_data['campaign_settings'], dict) else campaign_data['campaign_settings'],
                    'start_date': campaign_data['start_date'].isoformat() if isinstance(campaign_data['start_date'], datetime) else campaign_data['start_date'],
                    'end_date': campaign_data['end_date'].isoformat() if campaign_data.get('end_date') and isinstance(campaign_data['end_date'], datetime) else campaign_data.get('end_date'),
                    'created_at': campaign_data['created_at'].isoformat() if isinstance(campaign_data['created_at'], datetime) else campaign_data['created_at'],
                    'updated_at': campaign_data['updated_at'].isoformat() if isinstance(campaign_data['updated_at'], datetime) else campaign_data['updated_at']
                }
                supabase_data.append(supabase_record)
            
            # Insert into Supabase
            result = self.client.table('campaigns').insert(supabase_data).execute()
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to insert campaign batch: {e}")
            return False
    
    def seed_campaign_metrics(self, metrics_data: List[Dict[str, Any]]) -> bool:
        """Seed campaign metrics data."""
        try:
            logger.info(f"Starting to seed {len(metrics_data)} campaign metrics")
            
            # Process in batches
            for i in range(0, len(metrics_data), self.batch_size):
                batch = metrics_data[i:i + self.batch_size]
                if not self._insert_metrics_batch(batch):
                    return False
                
                logger.info(f"Inserted {i + len(batch)}/{len(metrics_data)} metrics")
            
            logger.info(f"Successfully seeded {len(metrics_data)} campaign metrics")
            return True
            
        except Exception as e:
            logger.error(f"Failed to seed campaign metrics: {e}")
            return False
    
    def _insert_metrics_batch(self, batch: List[Dict[str, Any]]) -> bool:
        """Insert a batch of campaign metrics."""
        try:
            # Convert data to Supabase format
            supabase_data = []
            for metrics_data in batch:
                supabase_record = {
                    'campaign_id': metrics_data['campaign_id'],
                    'metric_date': metrics_data['metric_date'].date().isoformat() if isinstance(metrics_data['metric_date'], datetime) else metrics_data['metric_date'],
                    'hour_of_day': metrics_data.get('hour_of_day'),
                    'impressions': int(metrics_data['impressions']),
                    'clicks': int(metrics_data['clicks']),
                    'conversions': int(metrics_data['conversions']),
                    'spend': float(metrics_data['spend']),
                    'revenue': float(metrics_data['revenue']),
                    'likes': int(metrics_data['likes']),
                    'shares': int(metrics_data['shares']),
                    'comments': int(metrics_data['comments']),
                    'saves': int(metrics_data['saves']),
                    'video_views': int(metrics_data['video_views']),
                    'demographics': json.dumps(metrics_data['demographics']) if isinstance(metrics_data['demographics'], dict) else metrics_data['demographics'],
                    'geo_data': json.dumps(metrics_data['geo_data']) if isinstance(metrics_data['geo_data'], dict) else metrics_data['geo_data'],
                    'device_data': json.dumps(metrics_data['device_data']) if isinstance(metrics_data['device_data'], dict) else metrics_data['device_data'],
                    'relevance_score': float(metrics_data['relevance_score']),
                    'quality_score': float(metrics_data['quality_score']),
                    'engagement_rate': float(metrics_data['engagement_rate']),
                    'performance_index': float(metrics_data['performance_index']),
                    'efficiency_index': float(metrics_data['efficiency_index']),
                    'created_at': metrics_data['created_at'].isoformat() if isinstance(metrics_data['created_at'], datetime) else metrics_data['created_at'],
                    'updated_at': metrics_data['updated_at'].isoformat() if isinstance(metrics_data['updated_at'], datetime) else metrics_data['updated_at']
                }
                supabase_data.append(supabase_record)
            
            # Insert into Supabase
            result = self.client.table('campaign_metrics').insert(supabase_data).execute()
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to insert metrics batch: {e}")
            return False
    
    def seed_agent_executions(self, executions_data: List[Dict[str, Any]]) -> bool:
        """Seed agent execution data."""
        try:
            logger.info(f"Starting to seed {len(executions_data)} agent executions")
            
            supabase_data = []
            for execution_data in executions_data:
                supabase_record = {
                    'execution_id': execution_data['execution_id'],
                    'agent_type': execution_data['agent_type'],
                    'workflow_id': execution_data.get('workflow_id'),
                    'status': execution_data['status'],
                    'input_data': json.dumps(execution_data.get('input_data')) if execution_data.get('input_data') else None,
                    'output_data': json.dumps(execution_data.get('output_data')) if execution_data.get('output_data') else None,
                    'error_message': execution_data.get('error_message'),
                    'execution_time_ms': execution_data.get('execution_time_ms', 0),
                    'tokens_used': execution_data.get('tokens_used', 0),
                    'api_calls_made': execution_data.get('api_calls_made', 0),
                    'metadata': json.dumps(execution_data.get('metadata')) if execution_data.get('metadata') else None,
                    'started_at': execution_data.get('started_at').isoformat() if execution_data.get('started_at') else None,
                    'completed_at': execution_data.get('completed_at').isoformat() if execution_data.get('completed_at') else None,
                    'created_at': execution_data['created_at'].isoformat() if isinstance(execution_data['created_at'], datetime) else execution_data['created_at'],
                    'updated_at': execution_data['updated_at'].isoformat() if isinstance(execution_data['updated_at'], datetime) else execution_data['updated_at']
                }
                supabase_data.append(supabase_record)
            
            # Insert into Supabase
            result = self.client.table('agent_executions').insert(supabase_data).execute()
            
            logger.info(f"Successfully seeded {len(executions_data)} agent executions")
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to seed agent executions: {e}")
            return False
    
    def clear_all_data(self) -> bool:
        """Clear all data from tables (for testing)."""
        try:
            # Clear in order due to foreign key constraints
            self.client.table('campaign_metrics').delete().neq('id', 'null').execute()
            self.client.table('agent_executions').delete().neq('id', 'null').execute()
            self.client.table('campaigns').delete().neq('id', 'null').execute()
            
            logger.info("Successfully cleared all data")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear data: {e}")
            return False
    
    def get_seeding_stats(self) -> Dict[str, int]:
        """Get statistics about seeded data."""
        try:
            # Count records in each table
            campaign_result = self.client.table('campaigns').select('id', count='exact').execute()
            metrics_result = self.client.table('campaign_metrics').select('id', count='exact').execute()
            execution_result = self.client.table('agent_executions').select('id', count='exact').execute()
            
            return {
                "campaigns": campaign_result.count or 0,
                "campaign_metrics": metrics_result.count or 0,
                "agent_executions": execution_result.count or 0,
            }
            
        except Exception as e:
            logger.error(f"Failed to get seeding stats: {e}")
            return {} 