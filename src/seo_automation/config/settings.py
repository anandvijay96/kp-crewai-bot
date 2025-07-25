"""
Application configuration management
"""
import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Google Cloud Settings
    google_cloud_project: str = Field(..., description="Google Cloud Project ID")
    vertex_ai_location: str = Field(default="us-central1", description="Vertex AI region")
    google_application_credentials: str = Field(
        default="./credentials/vertex-ai-key.json",
        description="Path to service account key"
    )
    
    # Cost Management
    daily_budget_usd: float = Field(default=15.0, description="Daily budget in USD")
    cost_alert_threshold: float = Field(default=0.8, description="Alert when 80% of budget used")
    
    # Application Settings
    log_level: str = Field(default="INFO", description="Logging level")
    environment: str = Field(default="development", description="Environment name")
    
    # Database (for future phases)
    database_url: Optional[str] = Field(default=None, description="Database connection URL")
    
    # CrewAI Compatibility (required but not used)
    openai_api_key: str = Field(default="dummy_key_not_used_but_required")
    openai_api_base: str = Field(default="https://us-central1-aiplatform.googleapis.com")
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"


# Global settings instance
settings = Settings()
