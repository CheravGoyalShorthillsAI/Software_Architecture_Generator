"""
Database configuration for The Genesis Engine

This module handles database connection and session management.
"""

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional

from .config import Settings

# Initialize settings
settings = Settings()

def get_db_connection_string(fork_name: Optional[str] = None) -> str:
    """
    Construct PostgreSQL connection string from settings.
    
    Args:
        fork_name: Optional fork name to append to database name
        
    Returns:
        PostgreSQL connection string
    """
    db_name = settings.tiger_db_name
    if fork_name:
        db_name = f"{db_name}:{fork_name}"
    
    return (
        f"postgresql://{settings.tiger_db_user}:{settings.tiger_db_password}"
        f"@{settings.tiger_db_host}:{settings.tiger_db_port}/{db_name}"
    )

# Create database engine using base connection string (without fork)
engine = create_engine(
    get_db_connection_string(),
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create SessionLocal class for dependency injection
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import Base from models to ensure all models are loaded
from .models import Base

def get_db():
    """
    Dependency to get database session.
    Use this as a FastAPI dependency to get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
