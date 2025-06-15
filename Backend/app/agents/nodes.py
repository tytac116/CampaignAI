from typing import Dict, Any, List
from datetime import datetime, timedelta
import json
import asyncio
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.prompts import ChatPromptTemplate

from ..core.config import settings
from ..services.facebook_api_sim import FacebookAPISimulator
from ..services.instagram_api_sim import InstagramAPISimulator
from .state import CampaignOptimizationState, AlertData, OptimizationRecommendation, ReportData, Priority, CampaignData


class BaseAgentNode:
    """Base class for all agent nodes."""
    
    def __init__(self, name: str):
        self.name = name
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.3,
            api_key=settings.openai_api_key
        )
        self.facebook_api = FacebookAPISimulator()
        self.instagram_api = InstagramAPISimulator()
    
    async def execute(self, state: CampaignOptimizationState) -> CampaignOptimizationState:
        """Execute the agent node logic."""
        raise NotImplementedError
    
    def _log_execution(self, state: CampaignOptimizationState, message: str):
        """Add execution log entry."""
        timestamp = datetime.utcnow().isoformat()
        state["execution_log"].append(f"[{timestamp}] {self.name}: {message}")
        state["updated_at"] = datetime.utcnow()


class CampaignMonitorNode(BaseAgentNode):
    """
    Node responsible for monitoring campaign performance and detecting anomalies.
    """
    
    def __init__(self):
        super().__init__("CampaignMonitor")
    
    async def execute(self, state: CampaignOptimizationState) -> CampaignOptimizationState:
        """Monitor campaigns and detect performance issues."""
        self._log_execution(state, "Starting campaign monitoring")
        
        try:
            # Fetch campaign data from APIs
            await self._fetch_campaign_data(state)
            
            # Detect anomalies and alerts
            await self._detect_anomalies(state)
            
            # Update campaign performance metrics
            await self._update_performance_metrics(state)
            
            state["completed_agents"].append(self.name)
            state["agent_outputs"][self.name] = {
                "campaigns_monitored": len(state["campaigns"]),
                "alerts_generated": len(state["alerts"]),
                "status": "completed"
            }
            
            self._log_execution(state, f"Monitoring completed. Found {len(state['alerts'])} alerts")
            
        except Exception as e:
            error_msg = f"Error in campaign monitoring: {str(e)}"
            state["errors"].append({
                "agent": self.name,
                "error": error_msg,
                "timestamp": datetime.utcnow().isoformat()
            })
            self._log_execution(state, error_msg)
        
        return state
    
    async def _fetch_campaign_data(self, state: CampaignOptimizationState):
        """Fetch campaign data from simulated APIs."""
        campaigns = []
        facebook_data = {}
        instagram_data = {}
        
        for campaign_id in state["campaign_ids"]:
            # Try Facebook API first
            fb_campaigns = await self.facebook_api.get_campaigns(limit=100)
            fb_campaign = next((c for c in fb_campaigns["data"] if int(c["id"]) == campaign_id), None)
            
            if fb_campaign:
                campaign_data = self._convert_api_to_campaign_data(fb_campaign, "facebook")
                campaigns.append(campaign_data)
                facebook_data[campaign_id] = fb_campaign
                
                # Get insights
                insights = await self.facebook_api.get_campaign_insights(campaign_id)
                facebook_data[f"{campaign_id}_insights"] = insights
            else:
                # Try Instagram API
                ig_campaigns = await self.instagram_api.get_campaigns(limit=100)
                ig_campaign = next((c for c in ig_campaigns["data"] if int(c["id"]) == campaign_id), None)
                
                if ig_campaign:
                    campaign_data = self._convert_api_to_campaign_data(ig_campaign, "instagram")
                    campaigns.append(campaign_data)
                    instagram_data[campaign_id] = ig_campaign
                    
                    # Get insights
                    insights = await self.instagram_api.get_campaign_insights(campaign_id)
                    instagram_data[f"{campaign_id}_insights"] = insights
        
        state["campaigns"] = campaigns
        state["facebook_api_data"] = facebook_data
        state["instagram_api_data"] = instagram_data
    
    async def _detect_anomalies(self, state: CampaignOptimizationState):
        """Detect performance anomalies and generate alerts."""
        alerts = []
        
        for campaign in state["campaigns"]:
            # Check for performance drops
            if campaign.ctr < 0.5:  # CTR below 0.5%
                alerts.append(AlertData(
                    campaign_id=campaign.id,
                    alert_type="performance_drop",
                    severity=Priority.HIGH,
                    message=f"Campaign '{campaign.name}' has low CTR: {campaign.ctr}%",
                    suggested_action="Review and optimize ad creative or targeting"
                ))
            
            # Check for budget overruns
            budget_utilization = (campaign.spend / campaign.budget) * 100
            if budget_utilization > 90:
                alerts.append(AlertData(
                    campaign_id=campaign.id,
                    alert_type="budget_overrun",
                    severity=Priority.CRITICAL if budget_utilization > 100 else Priority.HIGH,
                    message=f"Campaign '{campaign.name}' has used {budget_utilization:.1f}% of budget",
                    suggested_action="Consider increasing budget or pausing campaign"
                ))
            
            # Check for high CPC
            if campaign.cpc > 5.0:  # CPC above $5
                alerts.append(AlertData(
                    campaign_id=campaign.id,
                    alert_type="high_cost",
                    severity=Priority.MEDIUM,
                    message=f"Campaign '{campaign.name}' has high CPC: ${campaign.cpc}",
                    suggested_action="Optimize bidding strategy or targeting"
                ))
            
            # Check for low conversion rate
            if campaign.conversion_rate < 1.0:  # Conversion rate below 1%
                alerts.append(AlertData(
                    campaign_id=campaign.id,
                    alert_type="low_conversions",
                    severity=Priority.MEDIUM,
                    message=f"Campaign '{campaign.name}' has low conversion rate: {campaign.conversion_rate}%",
                    suggested_action="Review landing page and conversion funnel"
                ))
        
        state["alerts"] = alerts
    
    async def _update_performance_metrics(self, state: CampaignOptimizationState):
        """Update performance metrics analysis."""
        metrics = {}
        
        for campaign in state["campaigns"]:
            metrics[campaign.id] = {
                "performance_score": self._calculate_performance_score(campaign),
                "efficiency_rating": self._calculate_efficiency_rating(campaign),
                "optimization_potential": self._calculate_optimization_potential(campaign),
                "last_updated": datetime.utcnow().isoformat()
            }
        
        state["campaign_metrics"] = metrics
    
    def _convert_api_to_campaign_data(self, api_data: Dict[str, Any], platform: str) -> CampaignData:
        """Convert API response to CampaignData."""
        insights = api_data.get("insights", {}).get("data", [{}])[0]
        
        return CampaignData(
            id=int(api_data["id"]),
            name=api_data["name"],
            platform=platform,
            status=api_data["status"].lower(),
            budget=float(api_data.get("budget_remaining", 0)) + float(insights.get("spend", 0)),
            spend=float(insights.get("spend", 0)),
            impressions=int(insights.get("impressions", 0)),
            clicks=int(insights.get("clicks", 0)),
            conversions=int(insights.get("conversions", 0)),
            cpm=float(insights.get("cpm", 0)),
            cpc=float(insights.get("cpc", 0)),
            ctr=float(insights.get("ctr", 0)),
            conversion_rate=float(insights.get("conversion_rate", 0)),
            roas=float(insights.get("roas", 0)) if platform == "facebook" else float(insights.get("purchase_roas", 0))
        )
    
    def _calculate_performance_score(self, campaign: CampaignData) -> float:
        """Calculate overall performance score (0-100)."""
        # Weighted scoring based on key metrics
        ctr_score = min(campaign.ctr * 20, 100)  # CTR weight
        conversion_score = min(campaign.conversion_rate * 25, 100)  # Conversion weight
        roas_score = min(campaign.roas * 10, 100) if campaign.roas > 0 else 0  # ROAS weight
        
        return (ctr_score * 0.3 + conversion_score * 0.4 + roas_score * 0.3)
    
    def _calculate_efficiency_rating(self, campaign: CampaignData) -> str:
        """Calculate efficiency rating."""
        score = self._calculate_performance_score(campaign)
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "average"
        else:
            return "poor"
    
    def _calculate_optimization_potential(self, campaign: CampaignData) -> float:
        """Calculate optimization potential (0-100)."""
        # Higher potential for campaigns with poor performance
        performance_score = self._calculate_performance_score(campaign)
        return max(0, 100 - performance_score)


class DataAnalysisNode(BaseAgentNode):
    """
    Node responsible for deep data analysis, trend identification, and insights generation.
    """
    
    def __init__(self):
        super().__init__("DataAnalysis")
    
    async def execute(self, state: CampaignOptimizationState) -> CampaignOptimizationState:
        """Perform comprehensive data analysis."""
        self._log_execution(state, "Starting data analysis")
        
        try:
            # Analyze performance trends
            await self._analyze_trends(state)
            
            # Generate audience insights
            await self._analyze_audience(state)
            
            # Perform AI-powered analysis
            await self._ai_powered_analysis(state)
            
            state["completed_agents"].append(self.name)
            state["agent_outputs"][self.name] = {
                "trends_analyzed": len(state["trend_analysis"]),
                "insights_generated": len(state["performance_analysis"]),
                "status": "completed"
            }
            
            self._log_execution(state, "Data analysis completed")
            
        except Exception as e:
            error_msg = f"Error in data analysis: {str(e)}"
            state["errors"].append({
                "agent": self.name,
                "error": error_msg,
                "timestamp": datetime.utcnow().isoformat()
            })
            self._log_execution(state, error_msg)
        
        return state
    
    async def _analyze_trends(self, state: CampaignOptimizationState):
        """Analyze performance trends across campaigns."""
        trend_analysis = {
            "overall_performance": {},
            "platform_comparison": {},
            "time_based_trends": {},
            "correlation_analysis": {}
        }
        
        if not state["campaigns"]:
            state["trend_analysis"] = trend_analysis
            return
        
        # Overall performance trends
        total_spend = sum(c.spend for c in state["campaigns"])
        total_impressions = sum(c.impressions for c in state["campaigns"])
        total_clicks = sum(c.clicks for c in state["campaigns"])
        total_conversions = sum(c.conversions for c in state["campaigns"])
        
        trend_analysis["overall_performance"] = {
            "total_spend": total_spend,
            "average_cpm": sum(c.cpm for c in state["campaigns"]) / len(state["campaigns"]),
            "average_ctr": sum(c.ctr for c in state["campaigns"]) / len(state["campaigns"]),
            "average_conversion_rate": sum(c.conversion_rate for c in state["campaigns"]) / len(state["campaigns"]),
            "total_roas": sum(c.roas * c.spend for c in state["campaigns"]) / total_spend if total_spend > 0 else 0
        }
        
        # Platform comparison
        facebook_campaigns = [c for c in state["campaigns"] if c.platform == "facebook"]
        instagram_campaigns = [c for c in state["campaigns"] if c.platform == "instagram"]
        
        if facebook_campaigns:
            trend_analysis["platform_comparison"]["facebook"] = {
                "campaign_count": len(facebook_campaigns),
                "avg_ctr": sum(c.ctr for c in facebook_campaigns) / len(facebook_campaigns),
                "avg_cpc": sum(c.cpc for c in facebook_campaigns) / len(facebook_campaigns),
                "avg_conversion_rate": sum(c.conversion_rate for c in facebook_campaigns) / len(facebook_campaigns)
            }
        
        if instagram_campaigns:
            trend_analysis["platform_comparison"]["instagram"] = {
                "campaign_count": len(instagram_campaigns),
                "avg_ctr": sum(c.ctr for c in instagram_campaigns) / len(instagram_campaigns),
                "avg_cpc": sum(c.cpc for c in instagram_campaigns) / len(instagram_campaigns),
                "avg_conversion_rate": sum(c.conversion_rate for c in instagram_campaigns) / len(instagram_campaigns)
            }
        
        state["trend_analysis"] = trend_analysis
    
    async def _analyze_audience(self, state: CampaignOptimizationState):
        """Analyze audience insights and demographics."""
        audience_insights = {
            "demographic_performance": {},
            "targeting_effectiveness": {},
            "audience_recommendations": []
        }
        
        # Get audience data from APIs
        for campaign in state["campaigns"]:
            if campaign.platform == "instagram":
                try:
                    insights = await self.instagram_api.get_audience_insights(campaign.id)
                    audience_insights["demographic_performance"][campaign.id] = insights.get("data", {})
                except:
                    continue
        
        state["audience_insights"] = audience_insights
    
    async def _ai_powered_analysis(self, state: CampaignOptimizationState):
        """Use AI to generate insights and recommendations."""
        if not state["campaigns"]:
            return
        
        # Prepare data for AI analysis
        campaign_summary = []
        for campaign in state["campaigns"]:
            campaign_summary.append({
                "name": campaign.name,
                "platform": campaign.platform,
                "ctr": campaign.ctr,
                "cpc": campaign.cpc,
                "conversion_rate": campaign.conversion_rate,
                "roas": campaign.roas,
                "spend": campaign.spend,
                "budget_utilization": (campaign.spend / campaign.budget) * 100
            })
        
        # Create AI analysis prompt
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a digital marketing expert analyzing campaign performance data. 
            Provide insights, identify patterns, and suggest optimizations based on the campaign data provided.
            Focus on actionable insights and specific recommendations."""),
            HumanMessage(content=f"""
            Analyze the following campaign data and provide insights:
            
            Campaign Data:
            {json.dumps(campaign_summary, indent=2)}
            
            Trend Analysis:
            {json.dumps(state.get('trend_analysis', {}), indent=2)}
            
            Please provide:
            1. Key performance insights
            2. Identified patterns or trends
            3. Potential issues or opportunities
            4. Specific recommendations for optimization
            """)
        ])
        
        # Get AI analysis
        try:
            response = await self.llm.ainvoke(prompt.format_messages())
            ai_insights = response.content
            
            state["performance_analysis"]["ai_insights"] = ai_insights
            state["performance_analysis"]["analysis_timestamp"] = datetime.utcnow().isoformat()
            
        except Exception as e:
            self._log_execution(state, f"AI analysis failed: {str(e)}")


class OptimizationNode(BaseAgentNode):
    """
    Node responsible for generating optimization recommendations and implementing changes.
    """
    
    def __init__(self):
        super().__init__("Optimization")
    
    async def execute(self, state: CampaignOptimizationState) -> CampaignOptimizationState:
        """Generate and implement optimization recommendations."""
        self._log_execution(state, "Starting optimization analysis")
        
        try:
            # Generate recommendations
            await self._generate_recommendations(state)
            
            # Implement approved optimizations
            await self._implement_optimizations(state)
            
            state["completed_agents"].append(self.name)
            state["agent_outputs"][self.name] = {
                "recommendations_generated": len(state["recommendations"]),
                "optimizations_implemented": len(state.get("optimization_results", {})),
                "status": "completed"
            }
            
            self._log_execution(state, f"Generated {len(state['recommendations'])} recommendations")
            
        except Exception as e:
            error_msg = f"Error in optimization: {str(e)}"
            state["errors"].append({
                "agent": self.name,
                "error": error_msg,
                "timestamp": datetime.utcnow().isoformat()
            })
            self._log_execution(state, error_msg)
        
        return state
    
    async def _generate_recommendations(self, state: CampaignOptimizationState):
        """Generate optimization recommendations using AI."""
        recommendations = []
        
        for campaign in state["campaigns"]:
            # Budget optimization
            if campaign.roas > 3.0 and (campaign.spend / campaign.budget) > 0.8:
                recommendations.append(OptimizationRecommendation(
                    campaign_id=campaign.id,
                    recommendation_type="budget",
                    title="Increase Budget for High-Performing Campaign",
                    description=f"Campaign '{campaign.name}' has strong ROAS ({campaign.roas:.2f}) and is near budget limit",
                    expected_impact="20-30% increase in conversions",
                    confidence_score=0.85,
                    implementation_steps=[
                        "Increase daily budget by 25%",
                        "Monitor performance for 3 days",
                        "Adjust based on results"
                    ],
                    estimated_results={
                        "additional_conversions": int(campaign.conversions * 0.25),
                        "estimated_additional_revenue": campaign.roas * campaign.spend * 0.25
                    }
                ))
            
            # CTR optimization
            if campaign.ctr < 1.0:
                recommendations.append(OptimizationRecommendation(
                    campaign_id=campaign.id,
                    recommendation_type="creative",
                    title="Improve Ad Creative for Low CTR",
                    description=f"Campaign '{campaign.name}' has low CTR ({campaign.ctr:.2f}%)",
                    expected_impact="40-60% CTR improvement",
                    confidence_score=0.75,
                    implementation_steps=[
                        "Test new ad headlines",
                        "Update creative images/videos",
                        "A/B test different call-to-actions",
                        "Review targeting relevance"
                    ],
                    estimated_results={
                        "projected_ctr": campaign.ctr * 1.5,
                        "additional_clicks": int(campaign.impressions * 0.005)
                    }
                ))
            
            # Conversion rate optimization
            if campaign.conversion_rate < 2.0 and campaign.ctr > 1.5:
                recommendations.append(OptimizationRecommendation(
                    campaign_id=campaign.id,
                    recommendation_type="targeting",
                    title="Optimize Landing Page for Better Conversions",
                    description=f"Good CTR ({campaign.ctr:.2f}%) but low conversion rate ({campaign.conversion_rate:.2f}%)",
                    expected_impact="25-40% conversion rate improvement",
                    confidence_score=0.70,
                    implementation_steps=[
                        "Analyze landing page user journey",
                        "Optimize page load speed",
                        "Test different form layouts",
                        "Improve value proposition clarity"
                    ],
                    estimated_results={
                        "projected_conversion_rate": campaign.conversion_rate * 1.3,
                        "additional_conversions": int(campaign.clicks * 0.01)
                    }
                ))
        
        # Generate AI-powered recommendations
        if state["campaigns"]:
            ai_recommendations = await self._get_ai_recommendations(state)
            recommendations.extend(ai_recommendations)
        
        state["recommendations"] = recommendations
    
    async def _get_ai_recommendations(self, state: CampaignOptimizationState) -> List[OptimizationRecommendation]:
        """Get AI-powered optimization recommendations."""
        campaign_data = []
        for campaign in state["campaigns"]:
            campaign_data.append({
                "id": campaign.id,
                "name": campaign.name,
                "platform": campaign.platform,
                "metrics": {
                    "ctr": campaign.ctr,
                    "cpc": campaign.cpc,
                    "conversion_rate": campaign.conversion_rate,
                    "roas": campaign.roas,
                    "spend": campaign.spend,
                    "budget": campaign.budget
                }
            })
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert digital marketing optimizer. 
            Generate specific, actionable optimization recommendations based on campaign performance data.
            Focus on recommendations that can be implemented and measured."""),
            HumanMessage(content=f"""
            Based on this campaign data, generate 2-3 specific optimization recommendations:
            
            {json.dumps(campaign_data, indent=2)}
            
            Performance Analysis:
            {json.dumps(state.get('performance_analysis', {}), indent=2)}
            
            Format each recommendation with:
            - Campaign ID
            - Recommendation type (budget/targeting/creative/bidding)
            - Title
            - Description
            - Expected impact
            - Implementation steps
            """)
        ])
        
        try:
            response = await self.llm.ainvoke(prompt.format_messages())
            # In a real implementation, you'd parse the AI response and create OptimizationRecommendation objects
            # For now, return empty list as parsing would require more sophisticated logic
            return []
        except Exception as e:
            self._log_execution(state, f"AI recommendation generation failed: {str(e)}")
            return []
    
    async def _implement_optimizations(self, state: CampaignOptimizationState):
        """Implement approved optimizations."""
        optimization_results = {}
        
        # In a real implementation, you would:
        # 1. Check user preferences for auto-implementation
        # 2. Apply budget changes via API calls
        # 3. Update targeting parameters
        # 4. Test new creatives
        
        # For simulation, we'll just log the potential implementations
        for rec in state["recommendations"]:
            if rec.confidence_score > 0.8:  # Only auto-implement high-confidence recommendations
                optimization_results[rec.campaign_id] = {
                    "recommendation_id": f"rec_{rec.campaign_id}_{rec.recommendation_type}",
                    "status": "pending_approval",  # In real system, some might be "implemented"
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        state["optimization_results"] = optimization_results


class ReportingNode(BaseAgentNode):
    """
    Node responsible for generating comprehensive reports and notifications.
    """
    
    def __init__(self):
        super().__init__("Reporting")
    
    async def execute(self, state: CampaignOptimizationState) -> CampaignOptimizationState:
        """Generate comprehensive reports."""
        self._log_execution(state, "Starting report generation")
        
        try:
            # Generate performance report
            performance_report = await self._generate_performance_report(state)
            
            # Generate insights report
            insights_report = await self._generate_insights_report(state)
            
            # Generate recommendations report
            recommendations_report = await self._generate_recommendations_report(state)
            
            state["reports"] = [performance_report, insights_report, recommendations_report]
            
            # Generate notifications
            await self._generate_notifications(state)
            
            state["completed_agents"].append(self.name)
            state["agent_outputs"][self.name] = {
                "reports_generated": len(state["reports"]),
                "notifications_sent": len(state["notifications"]),
                "status": "completed"
            }
            
            self._log_execution(state, "Report generation completed")
            
        except Exception as e:
            error_msg = f"Error in reporting: {str(e)}"
            state["errors"].append({
                "agent": self.name,
                "error": error_msg,
                "timestamp": datetime.utcnow().isoformat()
            })
            self._log_execution(state, error_msg)
        
        return state
    
    async def _generate_performance_report(self, state: CampaignOptimizationState) -> ReportData:
        """Generate performance summary report."""
        if not state["campaigns"]:
            return ReportData(
                report_type="performance",
                period="current",
                summary="No campaigns to analyze",
                key_metrics={},
                insights=[],
                recommendations=[]
            )
        
        # Calculate key metrics
        total_spend = sum(c.spend for c in state["campaigns"])
        total_impressions = sum(c.impressions for c in state["campaigns"])
        total_clicks = sum(c.clicks for c in state["campaigns"])
        total_conversions = sum(c.conversions for c in state["campaigns"])
        
        key_metrics = {
            "total_campaigns": len(state["campaigns"]),
            "total_spend": total_spend,
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "average_ctr": sum(c.ctr for c in state["campaigns"]) / len(state["campaigns"]),
            "average_cpc": sum(c.cpc for c in state["campaigns"]) / len(state["campaigns"]),
            "average_conversion_rate": sum(c.conversion_rate for c in state["campaigns"]) / len(state["campaigns"]),
            "total_roas": sum(c.roas * c.spend for c in state["campaigns"]) / total_spend if total_spend > 0 else 0
        }
        
        # Generate insights
        insights = []
        if key_metrics["average_ctr"] < 1.0:
            insights.append("Overall CTR is below industry average - consider creative optimization")
        if key_metrics["average_conversion_rate"] < 2.0:
            insights.append("Conversion rates could be improved - review landing pages and user experience")
        if key_metrics["total_roas"] > 3.0:
            insights.append("Strong ROAS performance - consider scaling successful campaigns")
        
        return ReportData(
            report_type="performance",
            period="current_analysis",
            summary=f"Analysis of {len(state['campaigns'])} campaigns with total spend of ${total_spend:.2f}",
            key_metrics=key_metrics,
            insights=insights,
            recommendations=state["recommendations"][:3]  # Top 3 recommendations
        )
    
    async def _generate_insights_report(self, state: CampaignOptimizationState) -> ReportData:
        """Generate insights and trends report."""
        insights = []
        
        # Extract insights from analysis
        if state.get("performance_analysis", {}).get("ai_insights"):
            insights.append(state["performance_analysis"]["ai_insights"])
        
        # Add alert insights
        critical_alerts = [a for a in state["alerts"] if a.severity == Priority.CRITICAL]
        if critical_alerts:
            insights.append(f"Found {len(critical_alerts)} critical issues requiring immediate attention")
        
        # Add trend insights
        if state.get("trend_analysis", {}).get("platform_comparison"):
            platform_comp = state["trend_analysis"]["platform_comparison"]
            if "facebook" in platform_comp and "instagram" in platform_comp:
                fb_ctr = platform_comp["facebook"]["avg_ctr"]
                ig_ctr = platform_comp["instagram"]["avg_ctr"]
                if fb_ctr > ig_ctr * 1.2:
                    insights.append("Facebook campaigns are significantly outperforming Instagram in CTR")
                elif ig_ctr > fb_ctr * 1.2:
                    insights.append("Instagram campaigns are significantly outperforming Facebook in CTR")
        
        return ReportData(
            report_type="insights",
            period="current_analysis",
            summary="Data-driven insights and trend analysis",
            key_metrics=state.get("trend_analysis", {}),
            insights=insights,
            recommendations=[]
        )
    
    async def _generate_recommendations_report(self, state: CampaignOptimizationState) -> ReportData:
        """Generate recommendations summary report."""
        rec_summary = {}
        for rec in state["recommendations"]:
            rec_type = rec.recommendation_type
            if rec_type not in rec_summary:
                rec_summary[rec_type] = 0
            rec_summary[rec_type] += 1
        
        summary = f"Generated {len(state['recommendations'])} optimization recommendations"
        if rec_summary:
            summary += f" ({', '.join([f'{count} {type}' for type, count in rec_summary.items()])})"
        
        return ReportData(
            report_type="recommendations",
            period="current_analysis",
            summary=summary,
            key_metrics=rec_summary,
            insights=[f"High-confidence recommendations: {len([r for r in state['recommendations'] if r.confidence_score > 0.8])}"],
            recommendations=state["recommendations"]
        )
    
    async def _generate_notifications(self, state: CampaignOptimizationState):
        """Generate notifications for critical issues."""
        notifications = []
        
        # Alert-based notifications
        critical_alerts = [a for a in state["alerts"] if a.severity == Priority.CRITICAL]
        for alert in critical_alerts:
            notifications.append({
                "type": "alert",
                "priority": "critical",
                "title": f"Critical Issue: Campaign {alert.campaign_id}",
                "message": alert.message,
                "action_required": True,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # High-impact recommendation notifications
        high_impact_recs = [r for r in state["recommendations"] if r.confidence_score > 0.85]
        if high_impact_recs:
            notifications.append({
                "type": "recommendation",
                "priority": "high",
                "title": f"High-Impact Optimization Opportunities",
                "message": f"Found {len(high_impact_recs)} high-confidence optimization opportunities",
                "action_required": False,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        state["notifications"] = notifications 