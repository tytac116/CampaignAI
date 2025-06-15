from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Date, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class CampaignMetrics(Base):
    __tablename__ = "campaign_metrics"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    hour = Column(Integer, default=0)  # 0-23 for hourly granularity
    
    # Core metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    revenue = Column(Float, default=0.0)
    
    # Engagement metrics
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    video_views = Column(Integer, default=0)
    video_completion_rate = Column(Float, default=0.0)
    
    # Calculated KPIs
    cpm = Column(Float, default=0.0)  # Cost per mille
    cpc = Column(Float, default=0.0)  # Cost per click
    ctr = Column(Float, default=0.0)  # Click-through rate
    conversion_rate = Column(Float, default=0.0)
    cost_per_conversion = Column(Float, default=0.0)
    roas = Column(Float, default=0.0)  # Return on ad spend
    frequency = Column(Float, default=0.0)  # Average frequency
    reach = Column(Integer, default=0)  # Unique reach
    
    # Demographic breakdown (JSON)
    age_demographics = Column(JSON)  # {"18-24": {"impressions": 1000, "clicks": 50}, ...}
    gender_demographics = Column(JSON)  # {"male": {"impressions": 500}, "female": {"impressions": 500}}
    location_demographics = Column(JSON)  # {"USA": {"impressions": 800}, "Canada": {"impressions": 200}}
    device_demographics = Column(JSON)  # {"mobile": {"impressions": 700}, "desktop": {"impressions": 300}}
    
    # Time-based metrics
    peak_performance_hour = Column(Integer)  # Hour with best performance
    performance_score = Column(Float, default=0.0)  # Overall performance score
    trend_direction = Column(String)  # "up", "down", "stable"
    
    # Attribution and source tracking
    attribution_data = Column(JSON)  # Source attribution breakdown
    placement_performance = Column(JSON)  # Performance by ad placement
    
    # Quality metrics
    quality_score = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="metrics")
    
    # Composite indexes for efficient querying
    __table_args__ = (
        Index('idx_campaign_date', 'campaign_id', 'date'),
        Index('idx_campaign_date_hour', 'campaign_id', 'date', 'hour'),
    )

    def __repr__(self):
        return f"<CampaignMetrics(id={self.id}, campaign_id={self.campaign_id}, date={self.date})>" 