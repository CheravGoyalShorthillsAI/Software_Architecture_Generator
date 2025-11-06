"""
Pydantic schemas for The Genesis Engine

This module contains Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from uuid import UUID


# Project Schemas
class ProjectBase(BaseModel):
    """Base schema for Project with common fields."""
    user_prompt: str = Field(..., min_length=1, max_length=10000, description="User's project prompt")
    status: str = Field(default="pending", description="Project status")


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    systems_analyst_prompt: Optional[str] = Field(
        None, 
        max_length=5000, 
        description="Optional custom prompt for the systems analyst agent"
    )
    bizops_analyst_prompt: Optional[str] = Field(
        None, 
        max_length=5000, 
        description="Optional custom prompt for the business operations analyst agent"
    )


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    user_prompt: Optional[str] = Field(None, min_length=1, max_length=10000)
    status: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Schema for project responses including relationships."""
    id: UUID
    created_at: datetime
    blueprints: Optional[List["BlueprintResponse"]] = None

    class Config:
        from_attributes = True


# Blueprint Schemas
class BlueprintBase(BaseModel):
    """Base schema for Blueprint with common fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Blueprint name")
    description: str = Field(..., min_length=1, description="Blueprint description")
    pros: Optional[List[Dict[str, Any]]] = Field(None, description="List of pros/advantages")
    cons: Optional[List[Dict[str, Any]]] = Field(None, description="List of cons/disadvantages")
    mermaid_diagram: Optional[str] = Field(None, description="LLM-generated Mermaid diagram syntax")


class BlueprintCreate(BlueprintBase):
    """Schema for creating a new blueprint."""
    project_id: UUID = Field(..., description="ID of the parent project")


class BlueprintUpdate(BaseModel):
    """Schema for updating a blueprint."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    pros: Optional[List[Dict[str, Any]]] = None
    cons: Optional[List[Dict[str, Any]]] = None


class BlueprintResponse(BlueprintBase):
    """Schema for blueprint responses including relationships."""
    id: UUID
    project_id: UUID
    project: Optional["ProjectResponse"] = None
    analyses: Optional[List["AnalysisResponse"]] = None

    class Config:
        from_attributes = True


# Analysis Schemas
class AnalysisBase(BaseModel):
    """Base schema for Analysis with common fields."""
    category: str = Field(..., min_length=1, max_length=100, description="Analysis category")
    finding: str = Field(..., min_length=1, description="Analysis finding or result")
    severity: int = Field(..., ge=1, le=10, description="Severity level (1-10)")
    agent_type: Optional[str] = Field(None, description="Agent type that generated this analysis ('systems' or 'bizops')")


class AnalysisCreate(AnalysisBase):
    """Schema for creating a new analysis."""
    blueprint_id: UUID = Field(..., description="ID of the parent blueprint")


class AnalysisUpdate(BaseModel):
    """Schema for updating an analysis."""
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    finding: Optional[str] = Field(None, min_length=1)
    severity: Optional[int] = Field(None, ge=1, le=10)


class AnalysisResponse(AnalysisBase):
    """Schema for analysis responses including relationships."""
    id: UUID
    blueprint_id: UUID
    blueprint: Optional["BlueprintResponse"] = None

    class Config:
        from_attributes = True


# Update forward references for circular relationships
ProjectResponse.model_rebuild()
BlueprintResponse.model_rebuild()
AnalysisResponse.model_rebuild()


# Additional utility schemas
class PaginationParams(BaseModel):
    """Schema for pagination parameters."""
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of items to return")


class PaginatedResponse(BaseModel):
    """Schema for paginated API responses."""
    items: List[Union[ProjectResponse, BlueprintResponse, AnalysisResponse]]
    total: int = Field(..., ge=0, description="Total number of items")
    skip: int = Field(..., ge=0, description="Number of items skipped")
    limit: int = Field(..., ge=1, description="Maximum number of items requested")


# Status update schemas
class StatusUpdate(BaseModel):
    """Schema for updating status fields."""
    status: str = Field(..., min_length=1, max_length=50)


# Bulk operation schemas
class BulkDeleteResponse(BaseModel):
    """Schema for bulk delete operation responses."""
    deleted_count: int = Field(..., ge=0, description="Number of items deleted")
    deleted_ids: List[UUID] = Field(..., description="List of deleted item IDs")
