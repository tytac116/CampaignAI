from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..core.database import Base


class AgentType(str, enum.Enum):
    CAMPAIGN_MONITOR = "campaign_monitor"
    DATA_ANALYSIS = "data_analysis"
    OPTIMIZATION = "optimization"
    REPORTING = "reporting"
    COORDINATOR = "coordinator"


class ExecutionStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String, nullable=False, index=True)  # Unique identifier for the workflow
    agent_type = Column(Enum(AgentType), nullable=False, index=True)
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING, index=True)
    
    # Related campaign (optional)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True, index=True)
    
    # Execution data
    input_data = Column(JSON)  # Input parameters/data for the agent
    output_data = Column(JSON)  # Results/output from the agent
    execution_context = Column(JSON)  # Additional context like user preferences, constraints
    
    # Error handling
    error_message = Column(Text)
    error_details = Column(JSON)
    
    # Performance metrics
    execution_time_ms = Column(Integer)  # Execution time in milliseconds
    tokens_used = Column(Integer)  # Number of AI tokens consumed
    api_calls_made = Column(Integer)  # Number of external API calls
    
    # Workflow tracking
    parent_execution_id = Column(Integer, ForeignKey("agent_executions.id"), nullable=True)
    step_number = Column(Integer, default=1)  # Step in the workflow
    total_steps = Column(Integer, default=1)
    
    # Agent configuration
    agent_version = Column(String)  # Agent version used
    model_name = Column(String)  # AI model used (e.g., gpt-4)
    temperature = Column(String)  # Model temperature setting
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="agent_executions")
    parent_execution = relationship("AgentExecution", remote_side=[id], backref="child_executions")

    def __repr__(self):
        return f"<AgentExecution(id={self.id}, agent_type='{self.agent_type}', status='{self.status}')>" 