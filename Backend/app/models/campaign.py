from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..core.database import Base


class PlatformType(str, enum.Enum):
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"


class CampaignStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    DRAFT = "draft"


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    platform = Column(Enum(PlatformType), nullable=False, index=True)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT, index=True)
    
    # Budget and financial data
    budget = Column(Float, nullable=False)
    spend = Column(Float, default=0.0)
    daily_budget = Column(Float)
    
    # Campaign objectives and targeting
    objective = Column(String)  # conversions, traffic, awareness, etc.
    target_audience = Column(JSON)  # demographics, interests, behaviors
    
    # Performance metrics (current snapshot)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    
    # Calculated KPIs
    cpm = Column(Float, default=0.0)  # Cost per mille
    cpc = Column(Float, default=0.0)  # Cost per click
    ctr = Column(Float, default=0.0)  # Click-through rate
    conversion_rate = Column(Float, default=0.0)
    roas = Column(Float, default=0.0)  # Return on ad spend
    
    # Additional campaign settings
    ad_creative = Column(JSON)  # ad copy, images, videos
    campaign_settings = Column(JSON)  # placement, schedule, etc.
    
    # Optimization flags
    is_optimized = Column(Boolean, default=False)
    optimization_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    
    # Relationships
    metrics = relationship("CampaignMetrics", back_populates="campaign", cascade="all, delete-orphan")
    agent_executions = relationship("AgentExecution", back_populates="campaign", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Campaign(id={self.id}, name='{self.name}', platform='{self.platform}', status='{self.status}')>" 