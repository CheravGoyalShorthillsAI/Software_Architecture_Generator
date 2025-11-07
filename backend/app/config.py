"""
Configuration settings for The Genesis Engine

This module handles all configuration and environment variables.
"""

import os
from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_CANDIDATES = [
    BASE_DIR / ".env",
    BASE_DIR.parent / ".env",
    BASE_DIR.parent.parent / ".env",
]

for candidate in ENV_CANDIDATES:
    if candidate and candidate.exists():
        DEFAULT_ENV_PATH = candidate
        break
else:
    DEFAULT_ENV_PATH = ENV_CANDIDATES[0]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=str(DEFAULT_ENV_PATH),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields in .env file
    )
    
    # Application settings
    app_name: str = "The Genesis Engine"
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    frontend_origin: str = Field(default="", alias="FRONTEND_ORIGIN", description="Allowed CORS origin for hosted frontend")
    
    # Tiger Cloud Database Configuration
    tiger_service_id: str = Field(default="", alias="TIGER_SERVICE_ID")
    tiger_db_host: str = Field(default="", alias="TIGER_DB_HOST")
    tiger_db_port: int = Field(default=5432, alias="TIGER_DB_PORT")
    tiger_db_name: str = Field(default="", alias="TIGER_DB_NAME")
    tiger_db_user: str = Field(default="", alias="TIGER_DB_USER")
    tiger_db_password: str = Field(default="", alias="TIGER_DB_PASSWORD")
    
    # AI Provider API Keys
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    gemini_model_name: str = Field(default="models/gemini-2.5-pro", alias="GEMINI_MODEL_NAME")
    gemini_embedding_model: str = Field(
        default="models/text-embedding-004",
        alias="GEMINI_EMBEDDING_MODEL",
        description="Gemini embedding model identifier"
    )
    gemini_embedding_dimension: int = Field(
        default=768,
        alias="GEMINI_EMBEDDING_DIMENSION",
        description="Expected dimensionality of embedding vectors"
    )
    
    # Optional GitHub Token
    github_token: str = Field(default="", alias="GITHUB_TOKEN")
    
    @property
    def database_url(self) -> str:
        """Construct database URL from Tiger Cloud configuration."""
        return (
            f"postgresql://{self.tiger_db_user}:{self.tiger_db_password}"
            f"@{self.tiger_db_host}:{self.tiger_db_port}/{self.tiger_db_name}"
        )

@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()

# Global settings instance
settings = get_settings()
