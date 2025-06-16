#!/usr/bin/env python3
"""
Campaign Action Tool

This tool provides campaign management capabilities including:
- Creating new campaigns
- Updating existing campaigns (status, budget, settings)
- Bulk operations on campaigns
- Campaign lifecycle management

This tool integrates with Supabase and follows the existing tool patterns.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from ..services.supabase_service import supabase_service
from ..models.campaign import PlatformType, CampaignStatus

logger = logging.getLogger(__name__)

# Pydantic models for structured inputs
class CampaignCreateRequest(BaseModel):
    """Model for creating a new campaign."""
    name: str = Field(..., description="Campaign name")
    platform: str = Field(..., description="Platform: 'facebook' or 'instagram'")
    objective: str = Field(..., description="Campaign objective (conversions, traffic, awareness, etc.)")
    budget_amount: float = Field(..., description="Budget amount")
    budget_type: str = Field(default="daily", description="Budget type: 'daily' or 'lifetime'")
    target_audience: Optional[Dict[str, Any]] = Field(default=None, description="Target audience settings")
    ad_creative: Optional[Dict[str, Any]] = Field(default=None, description="Ad creative content")
    start_date: Optional[str] = Field(default=None, description="Campaign start date (ISO format)")
    end_date: Optional[str] = Field(default=None, description="Campaign end date (ISO format)")
    campaign_settings: Optional[Dict[str, Any]] = Field(default=None, description="Additional campaign settings")

class CampaignUpdateRequest(BaseModel):
    """Model for updating an existing campaign."""
    campaign_id: str = Field(..., description="Campaign ID to update")
    name: Optional[str] = Field(default=None, description="New campaign name")
    status: Optional[str] = Field(default=None, description="New status: 'active', 'paused', 'completed', 'draft'")
    budget_amount: Optional[float] = Field(default=None, description="New budget amount")
    budget_type: Optional[str] = Field(default=None, description="New budget type")
    target_audience: Optional[Dict[str, Any]] = Field(default=None, description="Updated target audience")
    ad_creative: Optional[Dict[str, Any]] = Field(default=None, description="Updated ad creative")
    end_date: Optional[str] = Field(default=None, description="Updated end date")
    campaign_settings: Optional[Dict[str, Any]] = Field(default=None, description="Updated campaign settings")

class BulkCampaignOperation(BaseModel):
    """Model for bulk campaign operations."""
    operation: str = Field(..., description="Operation: 'pause', 'activate', 'update_budget'")
    filters: Dict[str, Any] = Field(..., description="Filters to select campaigns")
    updates: Optional[Dict[str, Any]] = Field(default=None, description="Updates to apply")

@tool
def create_campaign(
    name: str,
    platform: str,
    objective: str,
    budget_amount: float,
    budget_type: str = "daily",
    target_audience: Optional[str] = None,
    ad_creative: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    campaign_settings: Optional[str] = None
) -> str:
    """
    Create a new campaign in the database.
    
    Use this tool to create new marketing campaigns with specified parameters.
    
    Args:
        name: Campaign name (required)
        platform: Platform - 'facebook' or 'instagram' (required)
        objective: Campaign objective like 'conversions', 'traffic', 'awareness' (required)
        budget_amount: Budget amount in currency units (required)
        budget_type: Budget type - 'daily' or 'lifetime' (default: 'daily')
        target_audience: JSON string of target audience settings (optional)
        ad_creative: JSON string of ad creative content (optional)
        start_date: Campaign start date in ISO format (optional, defaults to now)
        end_date: Campaign end date in ISO format (optional)
        campaign_settings: JSON string of additional campaign settings (optional)
        
    Returns:
        JSON string with campaign creation result
    """
    try:
        logger.info(f"Creating new campaign: {name} on {platform}")
        
        # Validate platform
        if platform.lower() not in ['facebook', 'instagram']:
            return json.dumps({
                "success": False,
                "error": "Platform must be 'facebook' or 'instagram'"
            })
        
        # Validate budget
        if budget_amount <= 0:
            return json.dumps({
                "success": False,
                "error": "Budget amount must be greater than 0"
            })
        
        # Parse JSON strings
        target_audience_data = None
        if target_audience:
            try:
                target_audience_data = json.loads(target_audience)
            except json.JSONDecodeError:
                return json.dumps({
                    "success": False,
                    "error": "Invalid target_audience JSON format"
                })
        
        ad_creative_data = None
        if ad_creative:
            try:
                ad_creative_data = json.loads(ad_creative)
            except json.JSONDecodeError:
                return json.dumps({
                    "success": False,
                    "error": "Invalid ad_creative JSON format"
                })
        
        campaign_settings_data = None
        if campaign_settings:
            try:
                campaign_settings_data = json.loads(campaign_settings)
            except json.JSONDecodeError:
                return json.dumps({
                    "success": False,
                    "error": "Invalid campaign_settings JSON format"
                })
        
        # Set default dates
        start_date_obj = datetime.utcnow()
        if start_date:
            try:
                start_date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                return json.dumps({
                    "success": False,
                    "error": "Invalid start_date format. Use ISO format."
                })
        
        end_date_obj = None
        if end_date:
            try:
                end_date_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                return json.dumps({
                    "success": False,
                    "error": "Invalid end_date format. Use ISO format."
                })
        
        # Generate unique campaign ID
        campaign_id = f"{platform}_{name.lower().replace(' ', '_')}_{int(datetime.utcnow().timestamp())}"
        
        # Prepare campaign data
        campaign_data = {
            "campaign_id": campaign_id,
            "name": name,
            "platform": platform.lower(),
            "status": "draft",  # New campaigns start as draft
            "objective": objective,
            "budget_type": budget_type,
            "budget_amount": budget_amount,
            "spend_amount": 0.0,
            "remaining_budget": budget_amount,
            "impressions": 0,
            "clicks": 0,
            "conversions": 0,
            "revenue": 0.0,
            "ctr": 0.0,
            "cpc": 0.0,
            "cpm": 0.0,
            "cpa": 0.0,
            "roas": 0.0,
            "is_optimized": False,
            "optimization_score": 0.0,
            "target_audience": target_audience_data,
            "ad_creative": ad_creative_data,
            "campaign_settings": campaign_settings_data,
            "start_date": start_date_obj.isoformat(),
            "end_date": end_date_obj.isoformat() if end_date_obj else None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Insert into database
        client = supabase_service.get_client()
        if not client:
            return json.dumps({
                "success": False,
                "error": "Database connection failed"
            })
        
        response = client.table('campaigns').insert(campaign_data).execute()
        
        if response.data:
            logger.info(f"✅ Campaign created successfully: {campaign_id}")
            return json.dumps({
                "success": True,
                "campaign_id": campaign_id,
                "message": f"Campaign '{name}' created successfully on {platform}",
                "data": response.data[0]
            })
        else:
            return json.dumps({
                "success": False,
                "error": "Failed to create campaign in database"
            })
            
    except Exception as e:
        logger.error(f"❌ Error creating campaign: {str(e)}")
        return json.dumps({
            "success": False,
            "error": f"Campaign creation failed: {str(e)}"
        })

@tool
def update_campaign(
    campaign_id: str,
    name: Optional[str] = None,
    status: Optional[str] = None,
    budget_amount: Optional[float] = None,
    budget_type: Optional[str] = None,
    target_audience: Optional[str] = None,
    ad_creative: Optional[str] = None,
    end_date: Optional[str] = None,
    campaign_settings: Optional[str] = None
) -> str:
    """
    Update an existing campaign in the database.
    
    Use this tool to modify campaign settings, status, budget, or other parameters.
    
    Args:
        campaign_id: Campaign ID to update (required)
        name: New campaign name (optional)
        status: New status - 'active', 'paused', 'completed', 'draft' (optional)
        budget_amount: New budget amount (optional)
        budget_type: New budget type - 'daily' or 'lifetime' (optional)
        target_audience: JSON string of updated target audience (optional)
        ad_creative: JSON string of updated ad creative (optional)
        end_date: Updated end date in ISO format (optional)
        campaign_settings: JSON string of updated campaign settings (optional)
        
    Returns:
        JSON string with update result
    """
    try:
        logger.info(f"Updating campaign: {campaign_id}")
        
        # Get Supabase client
        client = supabase_service.get_client()
        if not client:
            return json.dumps({
                "success": False,
                "error": "Database connection failed"
            })
        
        # Check if campaign exists
        existing_response = client.table('campaigns').select('*').eq('campaign_id', campaign_id).execute()
        
        if not existing_response.data:
            return json.dumps({
                "success": False,
                "error": f"Campaign '{campaign_id}' not found"
            })
        
        existing_campaign = existing_response.data[0]
        
        # Build update data
        update_data = {"updated_at": datetime.utcnow().isoformat()}
        changes_made = []
        
        if name:
            update_data['name'] = name
            changes_made.append(f"name: '{existing_campaign['name']}' → '{name}'")
        
        if status:
            valid_statuses = ['active', 'paused', 'completed', 'draft']
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Status must be one of: {', '.join(valid_statuses)}"
                })
            update_data['status'] = status
            changes_made.append(f"status: '{existing_campaign['status']}' → '{status}'")
        
        if budget_amount is not None:
            if budget_amount <= 0:
                return json.dumps({
                    "success": False,
                    "error": "Budget amount must be greater than 0"
                })
            update_data['budget_amount'] = budget_amount
            # Update remaining budget proportionally
            spent_ratio = existing_campaign.get('spend_amount', 0) / max(existing_campaign.get('budget_amount', 1), 1)
            update_data['remaining_budget'] = budget_amount * (1 - spent_ratio)
            changes_made.append(f"budget: {existing_campaign.get('budget_amount', 0)} → {budget_amount}")
        
        if budget_type:
            if budget_type not in ['daily', 'lifetime']:
                return json.dumps({
                    "success": False,
                    "error": "Budget type must be 'daily' or 'lifetime'"
                })
            update_data['budget_type'] = budget_type
            changes_made.append(f"budget_type: '{existing_campaign.get('budget_type', '')}' → '{budget_type}'")
        
        # Parse JSON fields
        if target_audience:
            try:
                target_audience_data = json.loads(target_audience)
                update_data['target_audience'] = target_audience_data
                changes_made.append("target_audience updated")
            except json.JSONDecodeError:
                return json.dumps({
                    "success": False,
                    "error": "Invalid target_audience JSON format"
                })
        
        if ad_creative:
            try:
                ad_creative_data = json.loads(ad_creative)
                update_data['ad_creative'] = ad_creative_data
                changes_made.append("ad_creative updated")
            except json.JSONDecodeError:
                return json.dumps({
                    "success": False,
                    "error": "Invalid ad_creative JSON format"
                })
        
        if campaign_settings:
            try:
                campaign_settings_data = json.loads(campaign_settings)
                update_data['campaign_settings'] = campaign_settings_data
                changes_made.append("campaign_settings updated")
            except json.JSONDecodeError:
                return json.dumps({
                    "success": False,
                    "error": "Invalid campaign_settings JSON format"
                })
        
        if end_date:
            try:
                end_date_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                update_data['end_date'] = end_date_obj.isoformat()
                changes_made.append(f"end_date updated to {end_date}")
            except ValueError:
                return json.dumps({
                    "success": False,
                    "error": "Invalid end_date format. Use ISO format."
                })
        
        if not changes_made:
            return json.dumps({
                "success": False,
                "error": "No valid updates provided"
            })
        
        # Perform update
        response = client.table('campaigns').update(update_data).eq('campaign_id', campaign_id).execute()
        
        if response.data:
            logger.info(f"✅ Campaign updated successfully: {campaign_id}")
            return json.dumps({
                "success": True,
                "campaign_id": campaign_id,
                "message": f"Campaign '{campaign_id}' updated successfully",
                "changes": changes_made,
                "data": response.data[0]
            })
        else:
            return json.dumps({
                "success": False,
                "error": "Failed to update campaign in database"
            })
            
    except Exception as e:
        logger.error(f"❌ Error updating campaign: {str(e)}")
        return json.dumps({
            "success": False,
            "error": f"Campaign update failed: {str(e)}"
        })

@tool
def bulk_campaign_operation(
    operation: str,
    filters: str,
    updates: Optional[str] = None
) -> str:
    """
    Perform bulk operations on multiple campaigns.
    
    Use this tool to perform operations on multiple campaigns that match certain criteria.
    
    Args:
        operation: Operation to perform - 'pause', 'activate', 'update_budget', 'update_status'
        filters: JSON string with filters to select campaigns (e.g., {"platform": "facebook", "ctr": {"<": 0.02}})
        updates: JSON string with updates to apply (required for update operations)
        
    Returns:
        JSON string with bulk operation results
    """
    try:
        logger.info(f"Performing bulk operation: {operation}")
        
        # Parse filters
        try:
            filter_data = json.loads(filters)
        except json.JSONDecodeError:
            return json.dumps({
                "success": False,
                "error": "Invalid filters JSON format"
            })
        
        # Parse updates if provided
        update_data = None
        if updates:
            try:
                update_data = json.loads(updates)
            except json.JSONDecodeError:
                return json.dumps({
                    "success": False,
                    "error": "Invalid updates JSON format"
                })
        
        # Get Supabase client
        client = supabase_service.get_client()
        if not client:
            return json.dumps({
                "success": False,
                "error": "Database connection failed"
            })
        
        # Build query based on filters
        query = client.table('campaigns').select('*')
        
        # Apply filters
        for field, value in filter_data.items():
            if isinstance(value, dict):
                # Handle comparison operators
                for op, op_value in value.items():
                    if op == '<':
                        query = query.lt(field, op_value)
                    elif op == '>':
                        query = query.gt(field, op_value)
                    elif op == '<=':
                        query = query.lte(field, op_value)
                    elif op == '>=':
                        query = query.gte(field, op_value)
                    elif op == '!=':
                        query = query.neq(field, op_value)
            else:
                # Direct equality
                query = query.eq(field, value)
        
        # Execute query to find matching campaigns
        response = query.execute()
        
        if not response.data:
            return json.dumps({
                "success": True,
                "message": "No campaigns matched the specified filters",
                "campaigns_affected": 0
            })
        
        matching_campaigns = response.data
        campaign_ids = [camp['campaign_id'] for camp in matching_campaigns]
        
        # Prepare bulk update based on operation
        bulk_update = {"updated_at": datetime.utcnow().isoformat()}
        
        if operation == 'pause':
            bulk_update['status'] = 'paused'
        elif operation == 'activate':
            bulk_update['status'] = 'active'
        elif operation == 'update_budget' and update_data:
            if 'budget_amount' in update_data:
                bulk_update['budget_amount'] = update_data['budget_amount']
        elif operation == 'update_status' and update_data:
            if 'status' in update_data:
                bulk_update['status'] = update_data['status']
        elif operation.startswith('update_') and update_data:
            # Generic update operation
            bulk_update.update(update_data)
        else:
            return json.dumps({
                "success": False,
                "error": f"Invalid operation '{operation}' or missing update data"
            })
        
        # Perform bulk update
        results = []
        for campaign_id in campaign_ids:
            try:
                update_response = client.table('campaigns').update(bulk_update).eq('campaign_id', campaign_id).execute()
                if update_response.data:
                    results.append({
                        "campaign_id": campaign_id,
                        "success": True,
                        "data": update_response.data[0]
                    })
                else:
                    results.append({
                        "campaign_id": campaign_id,
                        "success": False,
                        "error": "Update failed"
                    })
            except Exception as e:
                results.append({
                    "campaign_id": campaign_id,
                    "success": False,
                    "error": str(e)
                })
        
        successful_updates = [r for r in results if r['success']]
        failed_updates = [r for r in results if not r['success']]
        
        logger.info(f"✅ Bulk operation completed: {len(successful_updates)} successful, {len(failed_updates)} failed")
        
        return json.dumps({
            "success": True,
            "operation": operation,
            "campaigns_matched": len(matching_campaigns),
            "campaigns_updated": len(successful_updates),
            "campaigns_failed": len(failed_updates),
            "successful_updates": successful_updates,
            "failed_updates": failed_updates,
            "filters_applied": filter_data,
            "updates_applied": bulk_update
        })
        
    except Exception as e:
        logger.error(f"❌ Error in bulk operation: {str(e)}")
        return json.dumps({
            "success": False,
            "error": f"Bulk operation failed: {str(e)}"
        })

@tool
def get_campaign_details(campaign_id: str) -> str:
    """
    Get detailed information about a specific campaign.
    
    Use this tool to retrieve comprehensive campaign data before making updates.
    
    Args:
        campaign_id: Campaign ID to retrieve
        
    Returns:
        JSON string with campaign details
    """
    try:
        logger.info(f"Retrieving campaign details: {campaign_id}")
        
        # Get Supabase client
        client = supabase_service.get_client()
        if not client:
            return json.dumps({
                "success": False,
                "error": "Database connection failed"
            })
        
        # Query campaign
        response = client.table('campaigns').select('*').eq('campaign_id', campaign_id).execute()
        
        if not response.data:
            return json.dumps({
                "success": False,
                "error": f"Campaign '{campaign_id}' not found"
            })
        
        campaign = response.data[0]
        
        # Calculate additional metrics
        campaign['days_running'] = 0
        if campaign.get('start_date'):
            try:
                start_date = datetime.fromisoformat(campaign['start_date'].replace('Z', '+00:00'))
                campaign['days_running'] = (datetime.utcnow() - start_date).days
            except:
                pass
        
        # Calculate budget utilization
        budget_amount = campaign.get('budget_amount', 0)
        spend_amount = campaign.get('spend_amount', 0)
        campaign['budget_utilization'] = (spend_amount / budget_amount * 100) if budget_amount > 0 else 0
        
        logger.info(f"✅ Campaign details retrieved: {campaign_id}")
        
        return json.dumps({
            "success": True,
            "campaign": campaign
        })
        
    except Exception as e:
        logger.error(f"❌ Error retrieving campaign: {str(e)}")
        return json.dumps({
            "success": False,
            "error": f"Failed to retrieve campaign: {str(e)}"
        })

@tool
def list_campaigns_by_criteria(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    min_budget: Optional[float] = None,
    max_budget: Optional[float] = None,
    min_ctr: Optional[float] = None,
    max_ctr: Optional[float] = None,
    min_roas: Optional[float] = None,
    max_roas: Optional[float] = None,
    limit: int = 50
) -> str:
    """
    List campaigns that match specific criteria.
    
    Use this tool to find campaigns for analysis or bulk operations.
    
    Args:
        platform: Filter by platform - 'facebook' or 'instagram' (optional)
        status: Filter by status - 'active', 'paused', 'completed', 'draft' (optional)
        min_budget: Minimum budget amount (optional)
        max_budget: Maximum budget amount (optional)
        min_ctr: Minimum click-through rate (optional)
        max_ctr: Maximum click-through rate (optional)
        min_roas: Minimum return on ad spend (optional)
        max_roas: Maximum return on ad spend (optional)
        limit: Maximum number of campaigns to return (default: 50)
        
    Returns:
        JSON string with matching campaigns
    """
    try:
        logger.info("Listing campaigns by criteria")
        
        # Get Supabase client
        client = supabase_service.get_client()
        if not client:
            return json.dumps({
                "success": False,
                "error": "Database connection failed"
            })
        
        # Build query
        query = client.table('campaigns').select('*')
        
        # Apply filters
        if platform:
            query = query.eq('platform', platform.lower())
        
        if status:
            query = query.eq('status', status.lower())
        
        if min_budget is not None:
            query = query.gte('budget_amount', min_budget)
        
        if max_budget is not None:
            query = query.lte('budget_amount', max_budget)
        
        if min_ctr is not None:
            query = query.gte('ctr', min_ctr)
        
        if max_ctr is not None:
            query = query.lte('ctr', max_ctr)
        
        if min_roas is not None:
            query = query.gte('roas', min_roas)
        
        if max_roas is not None:
            query = query.lte('roas', max_roas)
        
        # Apply limit and execute
        response = query.limit(limit).execute()
        
        campaigns = response.data or []
        
        # Add calculated fields
        for campaign in campaigns:
            # Calculate budget utilization
            budget_amount = campaign.get('budget_amount', 0)
            spend_amount = campaign.get('spend_amount', 0)
            campaign['budget_utilization'] = (spend_amount / budget_amount * 100) if budget_amount > 0 else 0
            
            # Calculate days running
            campaign['days_running'] = 0
            if campaign.get('start_date'):
                try:
                    start_date = datetime.fromisoformat(campaign['start_date'].replace('Z', '+00:00'))
                    campaign['days_running'] = (datetime.utcnow() - start_date).days
                except:
                    pass
        
        logger.info(f"✅ Found {len(campaigns)} campaigns matching criteria")
        
        return json.dumps({
            "success": True,
            "campaigns": campaigns,
            "count": len(campaigns),
            "filters_applied": {
                "platform": platform,
                "status": status,
                "min_budget": min_budget,
                "max_budget": max_budget,
                "min_ctr": min_ctr,
                "max_ctr": max_ctr,
                "min_roas": min_roas,
                "max_roas": max_roas
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error listing campaigns: {str(e)}")
        return json.dumps({
            "success": False,
            "error": f"Failed to list campaigns: {str(e)}"
        }) 