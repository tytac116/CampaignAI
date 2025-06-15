"""
API Tests for Campaign Performance Optimization Platform

Basic test suite covering core API functionality:
- Campaign CRUD operations
- Analytics endpoints
- Optimization workflows
- Background tasks
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_session
from app.models.campaign import Campaign, PlatformType, CampaignStatus

# Test client setup
client = TestClient(app)

class TestCampaignAPI:
    """Test campaign API endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_get_campaigns(self):
        """Test getting campaigns list"""
        response = client.get("/api/v1/campaigns/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_campaign(self):
        """Test creating a new campaign"""
        campaign_data = {
            "name": "Test Campaign",
            "platform": "facebook",
            "budget": 1000.0,
            "start_date": "2024-01-01T00:00:00Z",
            "targeting": {"age": "25-35", "location": "US"},
            "ad_creative": {"title": "Test Ad", "description": "Test Description"}
        }
        
        response = client.post("/api/v1/campaigns/", json=campaign_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Campaign"
        assert data["platform"] == "facebook"
        assert data["budget"] == 1000.0
    
    def test_get_campaign_by_id(self):
        """Test getting a specific campaign"""
        # First create a campaign
        campaign_data = {
            "name": "Test Campaign 2",
            "platform": "instagram",
            "budget": 500.0,
            "start_date": "2024-01-01T00:00:00Z"
        }
        
        create_response = client.post("/api/v1/campaigns/", json=campaign_data)
        campaign_id = create_response.json()["id"]
        
        # Then get it by ID
        response = client.get(f"/api/v1/campaigns/{campaign_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == campaign_id
        assert data["name"] == "Test Campaign 2"
    
    def test_update_campaign(self):
        """Test updating a campaign"""
        # First create a campaign
        campaign_data = {
            "name": "Test Campaign 3",
            "platform": "facebook",
            "budget": 750.0,
            "start_date": "2024-01-01T00:00:00Z"
        }
        
        create_response = client.post("/api/v1/campaigns/", json=campaign_data)
        campaign_id = create_response.json()["id"]
        
        # Update the campaign
        update_data = {
            "name": "Updated Test Campaign",
            "budget": 1250.0,
            "status": "paused"
        }
        
        response = client.put(f"/api/v1/campaigns/{campaign_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Test Campaign"
        assert data["budget"] == 1250.0
    
    def test_get_campaign_metrics(self):
        """Test getting campaign metrics"""
        # Create a campaign first
        campaign_data = {
            "name": "Metrics Test Campaign",
            "platform": "facebook",
            "budget": 1000.0,
            "start_date": "2024-01-01T00:00:00Z"
        }
        
        create_response = client.post("/api/v1/campaigns/", json=campaign_data)
        campaign_id = create_response.json()["id"]
        
        # Get metrics (might be empty for new campaign)
        response = client.get(f"/api/v1/campaigns/{campaign_id}/metrics")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_campaign_performance(self):
        """Test getting campaign performance summary"""
        # Create a campaign first
        campaign_data = {
            "name": "Performance Test Campaign",
            "platform": "instagram",
            "budget": 500.0,
            "start_date": "2024-01-01T00:00:00Z"
        }
        
        create_response = client.post("/api/v1/campaigns/", json=campaign_data)
        campaign_id = create_response.json()["id"]
        
        # Get performance
        response = client.get(f"/api/v1/campaigns/{campaign_id}/performance")
        assert response.status_code == 200
        data = response.json()
        assert "campaign_id" in data
        assert "performance_summary" in data

class TestAnalyticsAPI:
    """Test analytics API endpoints"""
    
    def test_get_analytics_overview(self):
        """Test analytics overview endpoint"""
        response = client.get("/api/v1/analytics/overview")
        assert response.status_code == 200
        data = response.json()
        assert "performance_metrics" in data
        assert "platform_comparison" in data
        assert "trends" in data
        assert "top_performers" in data
    
    def test_get_performance_insights(self):
        """Test performance insights endpoint"""
        response = client.get("/api/v1/analytics/performance")
        assert response.status_code == 200
        data = response.json()
        assert "total_campaigns_analyzed" in data
        assert "key_insights" in data
        assert "performance_segments" in data
        assert "recommendations" in data
    
    def test_get_metric_trends(self):
        """Test metric trends endpoint"""
        response = client.get("/api/v1/analytics/trends/roas")
        assert response.status_code == 200
        data = response.json()
        assert data["metric"] == "roas"
        assert "trend_direction" in data
        assert "data_points" in data
    
    def test_get_platform_comparison(self):
        """Test platform comparison endpoint"""
        response = client.get("/api/v1/analytics/comparison")
        assert response.status_code == 200
        data = response.json()
        assert "platforms" in data
        assert "analysis_period" in data
    
    def test_get_demographic_insights(self):
        """Test demographic insights endpoint"""
        response = client.get("/api/v1/analytics/demographics")
        assert response.status_code == 200
        data = response.json()
        assert "demographic_performance" in data
        assert "insights" in data
        assert "recommendations" in data

class TestOptimizationAPI:
    """Test optimization workflow endpoints"""
    
    def test_optimize_campaign(self):
        """Test campaign optimization endpoint"""
        # Create a campaign first
        campaign_data = {
            "name": "Optimization Test Campaign",
            "platform": "facebook",
            "budget": 1000.0,
            "start_date": "2024-01-01T00:00:00Z"
        }
        
        create_response = client.post("/api/v1/campaigns/", json=campaign_data)
        campaign_id = create_response.json()["id"]
        
        # Start optimization
        response = client.post(f"/api/v1/campaigns/{campaign_id}/optimize")
        assert response.status_code == 200
        data = response.json()
        assert "workflow_id" in data
        assert data["campaign_id"] == campaign_id
        assert "status" in data
    
    def test_batch_optimization(self):
        """Test batch campaign optimization"""
        # Create multiple campaigns
        campaign_ids = []
        for i in range(2):
            campaign_data = {
                "name": f"Batch Test Campaign {i}",
                "platform": "facebook",
                "budget": 500.0,
                "start_date": "2024-01-01T00:00:00Z"
            }
            
            create_response = client.post("/api/v1/campaigns/", json=campaign_data)
            campaign_ids.append(create_response.json()["id"])
        
        # Run batch optimization
        optimization_data = {
            "campaign_ids": campaign_ids,
            "optimization_type": "all",
            "priority": "medium"
        }
        
        response = client.post("/api/v1/campaigns/optimize/batch", json=optimization_data)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == len(campaign_ids)

class TestBackgroundTasksAPI:
    """Test background task endpoints"""
    
    def test_trigger_optimization_task(self):
        """Test triggering optimization task"""
        # Create a campaign first
        campaign_data = {
            "name": "Task Test Campaign",
            "platform": "instagram",
            "budget": 750.0,
            "start_date": "2024-01-01T00:00:00Z"
        }
        
        create_response = client.post("/api/v1/campaigns/", json=campaign_data)
        campaign_id = create_response.json()["id"]
        
        # Trigger optimization task
        response = client.post(f"/api/v1/tasks/optimize/{campaign_id}?priority=high")
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["campaign_id"] == campaign_id
        assert data["priority"] == "high"
    
    def test_trigger_metrics_simulation(self):
        """Test triggering metrics simulation"""
        response = client.post("/api/v1/tasks/simulate-metrics")
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["task_type"] == "metric_simulation"
    
    def test_get_task_status(self):
        """Test getting task status"""
        # First trigger a task
        campaign_data = {
            "name": "Task Status Campaign",
            "platform": "facebook",
            "budget": 600.0,
            "start_date": "2024-01-01T00:00:00Z"
        }
        
        create_response = client.post("/api/v1/campaigns/", json=campaign_data)
        campaign_id = create_response.json()["id"]
        
        task_response = client.post(f"/api/v1/tasks/optimize/{campaign_id}")
        task_id = task_response.json()["task_id"]
        
        # Get task status
        response = client.get(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert "status" in data

class TestSystemAPI:
    """Test system information endpoints"""
    
    def test_system_info(self):
        """Test system info endpoint"""
        response = client.get("/api/v1/system/info")
        assert response.status_code == 200
        data = response.json()
        assert "system" in data
        assert "coordinator" in data
        assert "background_tasks" in data
        assert "database" in data

class TestMCPAPI:
    """Test MCP (Model Context Protocol) endpoints"""
    
    def test_mcp_initialize(self):
        """Test MCP initialization"""
        request_data = {
            "method": "initialize",
            "params": {},
            "id": "test_1"
        }
        
        response = client.post("/api/v1/mcp", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert data["id"] == "test_1"
    
    def test_mcp_list_tools(self):
        """Test MCP list tools"""
        request_data = {
            "method": "tools/list",
            "params": {},
            "id": "test_2"
        }
        
        response = client.post("/api/v1/mcp", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "tools" in data["result"]

# Test fixtures and utilities
@pytest.fixture
def test_campaign_data():
    """Fixture providing test campaign data"""
    return {
        "name": "Test Campaign",
        "platform": "facebook",
        "budget": 1000.0,
        "start_date": "2024-01-01T00:00:00Z",
        "targeting": {"age": "25-35", "location": "US"},
        "ad_creative": {"title": "Test Ad", "description": "Test Description"}
    }

@pytest.fixture
async def test_client():
    """Fixture providing async test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# Integration tests
class TestIntegration:
    """Integration tests covering full workflows"""
    
    def test_full_optimization_workflow(self):
        """Test complete optimization workflow"""
        # 1. Create a campaign
        campaign_data = {
            "name": "Integration Test Campaign",
            "platform": "facebook",
            "budget": 1000.0,
            "start_date": "2024-01-01T00:00:00Z"
        }
        
        create_response = client.post("/api/v1/campaigns/", json=campaign_data)
        assert create_response.status_code == 200
        campaign_id = create_response.json()["id"]
        
        # 2. Start optimization
        optimize_response = client.post(f"/api/v1/campaigns/{campaign_id}/optimize")
        assert optimize_response.status_code == 200
        workflow_id = optimize_response.json()["workflow_id"]
        
        # 3. Check workflow status
        status_response = client.get(f"/api/v1/campaigns/{campaign_id}/workflow/{workflow_id}")
        assert status_response.status_code == 200
        
        # 4. Get campaign performance
        performance_response = client.get(f"/api/v1/campaigns/{campaign_id}/performance")
        assert performance_response.status_code == 200
        
        # 5. Get analytics
        analytics_response = client.get("/api/v1/analytics/overview")
        assert analytics_response.status_code == 200

# Error handling tests
class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_campaign_not_found(self):
        """Test 404 for non-existent campaign"""
        response = client.get("/api/v1/campaigns/nonexistent_id")
        assert response.status_code == 404
    
    def test_invalid_campaign_data(self):
        """Test validation errors"""
        invalid_data = {
            "name": "",  # Empty name should fail validation
            "platform": "invalid_platform",
            "budget": -100  # Negative budget should fail
        }
        
        response = client.post("/api/v1/campaigns/", json=invalid_data)
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_invalid_optimization_priority(self):
        """Test invalid optimization priority"""
        response = client.post("/api/v1/tasks/optimize/test_id?priority=invalid")
        assert response.status_code == 400

if __name__ == "__main__":
    pytest.main([__file__]) 