from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_anon_key: str = Field(..., env="SUPABASE_ANON_KEY")
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    
    # LangSmith Configuration
    langsmith_api_key: str = Field(..., env="LANGSMITH_API_KEY")
    langsmith_tracing: str = Field("true", env="LANGSMITH_TRACING")
    langsmith_project: str = Field(..., env="LANGSMITH_PROJECT")
    
    # Pinecone Configuration
    pinecone_api_key: str = Field(..., env="PINECONE_API_KEY")
    
    # Redis Configuration
    redis_url: str = Field("redis://localhost:6379", env="REDIS_URL")
    
    # FastAPI Configuration
    secret_key: str = Field(..., env="SECRET_KEY")
    api_v1_str: str = Field("/api/v1", env="API_V1_STR")
    project_name: str = Field("Campaign Performance Optimization Platform", env="PROJECT_NAME")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS and Rate Limiting
    allowed_origins: str = Field("http://localhost:3000", env="ALLOWED_ORIGINS")
    search_rate_limit: str = Field("5/minute", env="SEARCH_RATE_LIMIT")
    explanation_rate_limit: str = Field("5/minute", env="EXPLANATION_RATE_LIMIT")
    general_rate_limit: str = Field("5/minute", env="GENERAL_RATE_LIMIT")
    port: int = Field(8000, env="PORT")
    
    # MCP Configuration
    mcp_host: str = Field("localhost", env="MCP_HOST")
    mcp_port: int = Field(8001, env="MCP_PORT")
    
    # Environment
    environment: str = Field("development", env="ENVIRONMENT")
    
    # Additional settings
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 