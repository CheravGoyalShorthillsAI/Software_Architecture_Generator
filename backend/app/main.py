"""
The Genesis Engine - FastAPI Main Application

This is the main entry point for The Genesis Engine backend API.
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

from . import crud, models, schemas, agents
from .database import get_db, get_db_connection_string
from .config import Settings

# Initialize settings and logging
settings = Settings()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="The Genesis Engine API",
    description="A powerful AI-driven application built for hackathon excellence",
    version="1.0.0"
)


# Request/Response Models
class CreateProjectRequest(BaseModel):
    """Request model for creating a new project."""
    user_prompt: str


class ProjectResponse(BaseModel):
    """Response model for project endpoints."""
    project_id: str
    status: str
    message: str


class CompleteProjectResponse(BaseModel):
    """Complete project response with all data."""
    project: schemas.ProjectResponse
    blueprints: List[Dict[str, Any]]


# Helper Functions
def create_fork_session(fork_name: str) -> Session:
    """
    Create a new SQLAlchemy session connected to a specific fork database.
    
    Args:
        fork_name: Name of the database fork
        
    Returns:
        SQLAlchemy session connected to the fork
    """
    try:
        fork_connection_string = get_db_connection_string(fork_name)
        fork_engine = create_engine(
            fork_connection_string,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
        
        # Create tables in the fork if they don't exist
        models.Base.metadata.create_all(bind=fork_engine)
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=fork_engine)
        return SessionLocal()
    except Exception as e:
        logger.error(f"Failed to create fork session for {fork_name}: {str(e)}")
        raise Exception(f"Failed to connect to fork database: {str(e)}")


async def create_database_fork(project_id: str, blueprint_index: int) -> str:
    """
    Create a new database fork using Tiger CLI.
    
    Args:
        project_id: UUID of the project
        blueprint_index: Index of the blueprint (0 or 1)
        
    Returns:
        Fork name that was created
    """
    fork_name = f"project_{project_id}_blueprint_{blueprint_index}"
    
    try:
        # Use tiger fork create command
        process = await asyncio.create_subprocess_exec(
            "tiger", "fork", "create", fork_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown error"
            logger.error(f"Tiger fork creation failed: {error_msg}")
            raise Exception(f"Failed to create database fork: {error_msg}")
        
        logger.info(f"Successfully created database fork: {fork_name}")
        return fork_name
        
    except FileNotFoundError:
        logger.error("Tiger CLI not found. Make sure it's installed and in PATH.")
        raise Exception("Tiger CLI not available")
    except Exception as e:
        logger.error(f"Fork creation failed: {str(e)}")
        raise Exception(f"Failed to create database fork: {str(e)}")


async def blueprint_analysis_orchestrator(
    project_id: str,
    blueprint_data: Dict[str, Any],
    fork_name: str
):
    """
    Orchestrator function that runs analysis and saves to forked database.
    
    This function runs in the background and:
    1. Analyzes the blueprint using run_analyst_agents
    2. Saves the blueprint and analyses to the forked database
    3. Updates the project status when complete
    
    Args:
        project_id: UUID of the parent project
        blueprint_data: Blueprint data from architect agent
        fork_name: Name of the database fork to use
    """
    try:
        logger.info(f"Starting analysis orchestrator for project {project_id}, fork {fork_name}")
        
        # Run analysis agents on the blueprint
        analyses = await agents.run_analyst_agents(blueprint_data)
        
        # Add analyses to blueprint data
        blueprint_with_analyses = blueprint_data.copy()
        blueprint_with_analyses["analyses"] = analyses
        
        # Create fork session and save data
        fork_session = create_fork_session(fork_name)
        try:
            # Save blueprint and analyses to the forked database
            saved_blueprint = crud.save_blueprint_and_analyses(
                db=fork_session,
                project_id=project_id,
                blueprint_data=blueprint_with_analyses
            )
            
            logger.info(f"Successfully saved blueprint {saved_blueprint.id} to fork {fork_name}")
            
        finally:
            fork_session.close()
        
        # Check if all blueprints are complete and update main project status
        await update_project_status_if_complete(project_id)
        
        logger.info(f"Analysis orchestrator completed for project {project_id}, fork {fork_name}")
        
    except Exception as e:
        logger.error(f"Analysis orchestrator failed for project {project_id}: {str(e)}")
        # Update project status to indicate failure
        try:
            main_db = next(get_db())
            crud.update_project_status(main_db, project_id, "error")
            main_db.close()
        except Exception as status_error:
            logger.error(f"Failed to update project status: {str(status_error)}")


async def update_project_status_if_complete(project_id: str):
    """
    Check if all blueprint analyses are complete and update project status.
    
    Args:
        project_id: UUID of the project to check
    """
    try:
        # Check both forks to see if they have data
        fork_0_name = f"project_{project_id}_blueprint_0"
        fork_1_name = f"project_{project_id}_blueprint_1"
        
        blueprints_complete = 0
        
        for fork_name in [fork_0_name, fork_1_name]:
            try:
                fork_session = create_fork_session(fork_name)
                blueprints = fork_session.query(models.Blueprint).all()
                fork_session.close()
                
                if blueprints:
                    blueprints_complete += 1
            except Exception:
                # Fork might not exist yet or have issues
                pass
        
        # Update main project status if both blueprints are complete
        if blueprints_complete == 2:
            main_db = next(get_db())
            crud.update_project_status(main_db, project_id, "completed")
            main_db.close()
            logger.info(f"Project {project_id} marked as completed")
        
    except Exception as e:
        logger.error(f"Failed to update project completion status: {str(e)}")


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "message": "Welcome to The Genesis Engine API",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/projects", response_model=ProjectResponse)
async def create_project(
    request: CreateProjectRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new project and start blueprint generation and analysis.
    
    This endpoint:
    1. Creates a project in the main database
    2. Generates architectural blueprints using AI
    3. Creates database forks for each blueprint
    4. Starts background analysis for each blueprint
    5. Returns the project ID immediately
    
    Args:
        request: Create project request with user prompt
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Project response with project ID and status
    """
    try:
        logger.info(f"Creating new project with prompt: {request.user_prompt[:100]}...")
        
        # Step 1: Create project in main database
        project = crud.create_project(db, request.user_prompt)
        project_id = str(project.id)
        
        logger.info(f"Created project {project_id}")
        
        # Step 2: Generate architectural blueprints
        try:
            blueprints = await agents.run_architect_agent(request.user_prompt)
            logger.info(f"Generated {len(blueprints)} blueprints for project {project_id}")
        except Exception as e:
            # Update project status to error and re-raise
            crud.update_project_status(db, project_id, "error")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate blueprints: {str(e)}"
            )
        
        # Step 3 & 4: Create forks and start background analysis for each blueprint
        crud.update_project_status(db, project_id, "processing")
        
        for i, blueprint in enumerate(blueprints):
            try:
                # Create database fork
                fork_name = await create_database_fork(project_id, i)
                
                # Start background analysis
                background_tasks.add_task(
                    blueprint_analysis_orchestrator,
                    project_id,
                    blueprint,
                    fork_name
                )
                
                logger.info(f"Started background analysis for blueprint {i} in fork {fork_name}")
                
            except Exception as e:
                logger.error(f"Failed to process blueprint {i}: {str(e)}")
                crud.update_project_status(db, project_id, "error")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to process blueprint {i}: {str(e)}"
                )
        
        return ProjectResponse(
            project_id=project_id,
            status="processing",
            message="Project created successfully. Analysis in progress."
        )
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Project creation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create project: {str(e)}"
        )


@app.get("/projects/{project_id}", response_model=CompleteProjectResponse)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a complete project with all blueprints and analyses.
    
    This endpoint:
    1. Fetches the project from the main database
    2. If analysis is complete, connects to each fork
    3. Retrieves blueprint and analysis data from forks
    4. Assembles the complete response
    
    Args:
        project_id: UUID of the project
        db: Main database session
        
    Returns:
        Complete project data with blueprints and analyses
    """
    try:
        # Fetch project from main database
        project = crud.get_project(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Convert to response schema
        project_response = schemas.ProjectResponse.from_orm(project)
        
        # If project is not completed, return basic info
        if project.status != "completed":
            return CompleteProjectResponse(
                project=project_response,
                blueprints=[]
            )
        
        # Project is complete - fetch data from forks
        blueprints_data = []
        
        for blueprint_index in [0, 1]:
            fork_name = f"project_{project_id}_blueprint_{blueprint_index}"
            
            try:
                # Create session to fork database
                fork_session = create_fork_session(fork_name)
                
                try:
                    # Get blueprints from fork (should only be one per fork)
                    fork_blueprints = fork_session.query(models.Blueprint).all()
                    
                    for blueprint in fork_blueprints:
                        # Convert to dict and include analyses
                        blueprint_dict = {
                            "id": str(blueprint.id),
                            "name": blueprint.name,
                            "description": blueprint.description,
                            "pros": blueprint.pros,
                            "cons": blueprint.cons,
                            "analyses": []
                        }
                        
                        # Add analyses
                        for analysis in blueprint.analyses:
                            analysis_dict = {
                                "id": str(analysis.id),
                                "category": analysis.category,
                                "finding": analysis.finding,
                                "severity": analysis.severity
                            }
                            blueprint_dict["analyses"].append(analysis_dict)
                        
                        blueprints_data.append(blueprint_dict)
                
                finally:
                    fork_session.close()
                    
            except Exception as e:
                logger.error(f"Failed to retrieve data from fork {fork_name}: {str(e)}")
                # Continue with other forks, don't fail the entire request
        
        return CompleteProjectResponse(
            project=project_response,
            blueprints=blueprints_data
        )
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Failed to retrieve project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve project: {str(e)}"
        )


@app.get("/projects/{project_id}/status")
async def get_project_status(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the current status of a project.
    
    Args:
        project_id: UUID of the project
        db: Database session
        
    Returns:
        Project status information
    """
    try:
        project = crud.get_project(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "project_id": project_id,
            "status": project.status,
            "created_at": project.created_at,
            "user_prompt": project.user_prompt[:100] + "..." if len(project.user_prompt) > 100 else project.user_prompt
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get project status: {str(e)}"
        )
