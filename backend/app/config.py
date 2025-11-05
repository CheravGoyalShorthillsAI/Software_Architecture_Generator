"""
Configuration settings for The Genesis Engine

This module handles all configuration and environment variables.
"""

import os
from functools import lru_cache
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    app_name: str = "The Genesis Engine"
    debug: bool = False
    
    # Tiger Cloud Database Configuration
    tiger_service_id: str = Field(default="", env="TIGER_SERVICE_ID")
    tiger_db_host: str = Field(default="", env="TIGER_DB_HOST")
    tiger_db_port: int = Field(default=5432, env="TIGER_DB_PORT")
    tiger_db_name: str = Field(default="", env="TIGER_DB_NAME")
    tiger_db_user: str = Field(default="", env="TIGER_DB_USER")
    tiger_db_password: str = Field(default="", env="TIGER_DB_PASSWORD")
    
    # AI Provider API Keys
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    
    @property
    def database_url(self) -> str:
        """Construct database URL from Tiger Cloud configuration."""
        return (
            f"postgresql://{self.tiger_db_user}:{self.tiger_db_password}"
            f"@{self.tiger_db_host}:{self.tiger_db_port}/{self.tiger_db_name}"
        )
    
    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()

# Global settings instance
settings = get_settings()
