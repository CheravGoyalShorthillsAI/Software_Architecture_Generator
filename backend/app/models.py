"""
Database models for The Genesis Engine

This module contains SQLAlchemy ORM models for database tables.
"""

import uuid
from sqlalchemy import Column, String, DateTime, Text, Integer, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Project(Base):
    """Project model for storing user projects and their generation status."""
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_prompt = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to blueprints
    blueprints = relationship("Blueprint", back_populates="project", cascade="all, delete-orphan")


class Blueprint(Base):
    """Blueprint model for storing generated architecture blueprints."""
    __tablename__ = "blueprints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    pros = Column(JSON, nullable=True)
    cons = Column(JSON, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="blueprints")
    analyses = relationship("Analysis", back_populates="blueprint", cascade="all, delete-orphan")


class Analysis(Base):
    """Analysis model for storing detailed analysis of blueprints."""
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    blueprint_id = Column(UUID(as_uuid=True), ForeignKey("blueprints.id"), nullable=False)
    category = Column(String(100), nullable=False)
    finding = Column(Text, nullable=False)
    severity = Column(Integer, nullable=False)

    # Relationship
    blueprint = relationship("Blueprint", back_populates="analyses")
