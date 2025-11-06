"""
CRUD operations for The Genesis Engine

This module contains database CRUD (Create, Read, Update, Delete) operations.
"""

from sqlalchemy import bindparam, func, select
from sqlalchemy.orm import Session
from typing import List, Optional, Type, TypeVar, Generic, Dict, Any
from pydantic import BaseModel
from uuid import UUID
import uuid

from . import models
from pgvector.sqlalchemy import Vector

# Generic types for CRUD operations
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base CRUD class with generic database operations."""
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize CRUD object with model.
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model
    
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Get a single record by ID."""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination."""
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        obj_data = obj_in.dict()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        """Update an existing record."""
        obj_data = obj_in.dict(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: int) -> ModelType:
        """Delete a record by ID."""
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

# Specific CRUD functions for The Genesis Engine


def create_project(db: Session, prompt: str) -> models.Project:
    """
    Create a new project in the database.
    
    Args:
        db: Database session
        prompt: User's project prompt
        
    Returns:
        Created project instance
    """
    try:
        db_project = models.Project(
            user_prompt=prompt,
            status="pending"
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to create project: {str(e)}")


def get_project(db: Session, project_id: str) -> Optional[models.Project]:
    """
    Retrieve a project by its ID.
    
    Args:
        db: Database session
        project_id: UUID string of the project
        
    Returns:
        Project instance if found, None otherwise
    """
    try:
        # Convert string to UUID if needed
        if isinstance(project_id, str):
            project_uuid = UUID(project_id)
        else:
            project_uuid = project_id
            
        return db.query(models.Project).filter(
            models.Project.id == project_uuid
        ).first()
    except ValueError as e:
        raise ValueError(f"Invalid project ID format: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to retrieve project: {str(e)}")


def save_blueprint_and_analyses(
    db: Session, 
    project_id: str, 
    blueprint_data: Dict[str, Any]
) -> models.Blueprint:
    """
    Save a blueprint and its analyses from AI agent output.
    
    This is a critical function that takes the full JSON output for one blueprint
    from an AI agent and saves it to the Blueprint and Analysis tables correctly,
    linking them together.
    
    Args:
        db: Database session
        project_id: UUID string of the parent project
        blueprint_data: Dictionary containing blueprint and analysis data
        
    Expected blueprint_data structure:
        {
            "name": "Architecture Name",
            "description": "Architecture description",
            "pros": [{"point": "...", "description": "..."}],
            "cons": [{"point": "...", "description": "..."}],
            "analyses": [
                {
                    "category": "Security",
                    "finding": "Analysis finding",
                    "severity": 7
                }
            ]
        }
        
    Returns:
        Created blueprint instance with analyses
    """
    try:
        # Convert project_id to UUID
        if isinstance(project_id, str):
            project_uuid = UUID(project_id)
        else:
            project_uuid = project_id
            
        # Verify project exists
        project = get_project(db, project_uuid)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        # Create blueprint
        db_blueprint = models.Blueprint(
            project_id=project_uuid,
            name=blueprint_data.get("name", "Unnamed Blueprint"),
            description=blueprint_data.get("description", ""),
            pros=blueprint_data.get("pros", []),
            cons=blueprint_data.get("cons", [])
        )
        
        db.add(db_blueprint)
        db.flush()  # Get the blueprint ID before creating analyses
        
        # Create analyses if provided
        analyses_data = blueprint_data.get("analyses", [])
        created_analyses = []
        
        for analysis_data in analyses_data:
            # Validate required fields
            if not all(key in analysis_data for key in ["category", "finding", "severity"]):
                raise ValueError("Analysis data must contain 'category', 'finding', and 'severity'")
            
            # Validate severity range
            severity = analysis_data["severity"]
            if not isinstance(severity, int) or severity < 1 or severity > 10:
                raise ValueError(f"Severity must be an integer between 1 and 10, got: {severity}")
            
            db_analysis = models.Analysis(
                blueprint_id=db_blueprint.id,
                category=analysis_data["category"],
                finding=analysis_data["finding"],
                severity=severity,
                finding_embedding=analysis_data.get("finding_embedding")
            )
            
            db.add(db_analysis)
            created_analyses.append(db_analysis)
        
        # Commit the transaction
        db.commit()
        
        # Refresh to get all relationships
        db.refresh(db_blueprint)
        
        return db_blueprint
        
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to save blueprint and analyses: {str(e)}")


def hybrid_search_in_fork(
    db: Session,
    query_text: str,
    query_embedding: List[float],
    limit: int = 15
) -> List[models.Analysis]:
    """Perform hybrid keyword and vector search within a forked database."""

    if not query_text or not query_embedding:
        return []

    ts_query_param = bindparam("query_text")
    embedding_param = bindparam("query_embedding", type_=Vector(768))

    stmt = (
        select(models.Analysis)
        .where(
            func.to_tsvector("english", models.Analysis.finding).op("@@")( 
                func.to_tsquery("english", ts_query_param)
            )
        )
        .order_by(models.Analysis.finding_embedding.op("<=>")(embedding_param))
        .limit(limit)
    )

    result = db.execute(
        stmt,
        {
            "query_text": query_text,
            "query_embedding": query_embedding,
        }
    )
    return result.scalars().all()


# Additional utility functions
def get_project_with_blueprints(db: Session, project_id: str) -> Optional[models.Project]:
    """
    Get a project with all its blueprints and analyses loaded.
    
    Args:
        db: Database session
        project_id: UUID string of the project
        
    Returns:
        Project instance with blueprints and analyses, None if not found
    """
    try:
        if isinstance(project_id, str):
            project_uuid = UUID(project_id)
        else:
            project_uuid = project_id
            
        return db.query(models.Project)\
            .filter(models.Project.id == project_uuid)\
            .first()
    except ValueError as e:
        raise ValueError(f"Invalid project ID format: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to retrieve project with blueprints: {str(e)}")


def update_project_status(db: Session, project_id: str, status: str) -> Optional[models.Project]:
    """
    Update the status of a project.
    
    Args:
        db: Database session
        project_id: UUID string of the project
        status: New status value
        
    Returns:
        Updated project instance, None if not found
    """
    try:
        project = get_project(db, project_id)
        if project:
            project.status = status
            db.commit()
            db.refresh(project)
        return project
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to update project status: {str(e)}")


# CRUD class instances for generic operations
class CRUDProject(CRUDBase[models.Project, dict, dict]):
    """CRUD operations for Project model."""
    pass


class CRUDBlueprint(CRUDBase[models.Blueprint, dict, dict]):
    """CRUD operations for Blueprint model."""
    pass


class CRUDAnalysis(CRUDBase[models.Analysis, dict, dict]):
    """CRUD operations for Analysis model."""
    pass


# Instantiate CRUD objects
project = CRUDProject(models.Project)
blueprint = CRUDBlueprint(models.Blueprint)
analysis = CRUDAnalysis(models.Analysis)
