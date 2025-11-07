"""
The Genesis Engine - FastAPI Main Application

This is the main entry point for The Genesis Engine backend API.
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

from . import crud, models, schemas, agents
from .database import (
    get_db,
    get_db_connection_string,
    SessionLocal,
    TIGER_AVAILABLE,
    TIGER_CLI_PATH,
)
from .utils import get_tiger_cli_path
from .config import Settings

# Initialize settings and logging
settings = Settings()
logger = logging.getLogger(__name__)

PRIMARY_FORK_NAME = "__primary__"

app = FastAPI(
    title="The Genesis Engine API",
    description="A powerful AI-driven application built for hackathon excellence",
    version="1.0.0"
)

# Determine allowed CORS origins (local dev + optional hosted frontend)
default_origins = {
    "http://localhost:3000",
    "http://127.0.0.1:3000",
}

if settings.frontend_origin:
    normalized_origin = settings.frontend_origin.rstrip("/")
    if normalized_origin:
        default_origins.add(normalized_origin)
        if normalized_origin.startswith("http://"):
            default_origins.add(normalized_origin.replace("http://", "https://", 1))
        elif normalized_origin.startswith("https://"):
            default_origins.add(normalized_origin.replace("https://", "http://", 1))

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(default_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

force_primary_mode = (not TIGER_AVAILABLE) or (not settings.tiger_service_id)


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


class SearchRequest(BaseModel):
    """Request payload for hybrid project search."""
    query: str


def serialize_project(project: models.Project) -> Dict[str, Any]:
    return {
        "id": project.id,
        "user_prompt": project.user_prompt,
        "status": project.status,
        "created_at": project.created_at,
        "blueprints": [],
    }


# Helper Functions
def create_fork_session(fork_name: Optional[str]) -> Session:
    """
    Create a new SQLAlchemy session connected to a specific fork database.
    
    Args:
        fork_name: Name of the database fork
        
    Returns:
        SQLAlchemy session connected to the fork
    """
    if force_primary_mode or not TIGER_AVAILABLE or not fork_name or fork_name == PRIMARY_FORK_NAME:
        return SessionLocal()

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
        
        ForkSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=fork_engine)
        return ForkSessionLocal()
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
    global force_primary_mode

    fork_name = f"project_{project_id}_blueprint_{blueprint_index}"

    if force_primary_mode or not TIGER_AVAILABLE or not settings.tiger_service_id:
        logger.warning(
            "Tiger CLI unavailable or configuration incomplete. Using primary database for project %s blueprint %s",
            project_id,
            blueprint_index,
        )
        force_primary_mode = True
        return PRIMARY_FORK_NAME

    try:
        tiger_cli = TIGER_CLI_PATH or get_tiger_cli_path()

        # Use tiger fork create command
        process = await asyncio.create_subprocess_exec(
            tiger_cli,
            "service",
            "fork",
            settings.tiger_service_id,
            "--now",
            "--name",
            fork_name,
            "--no-set-default",
            "--output",
            "json",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown error"
            logger.error(f"Tiger fork creation failed: {error_msg}")
            if "authentication required" in error_msg.lower() or "not logged in" in error_msg.lower():
                logger.warning(
                    "Tiger CLI not authenticated. Falling back to primary database for project %s blueprint %s",
                    project_id,
                    blueprint_index,
                )
            else:
                logger.warning(
                    "Tiger CLI fork command returned non-zero exit code. Falling back to primary database for project %s blueprint %s",
                    project_id,
                    blueprint_index,
                )
            force_primary_mode = True
            return PRIMARY_FORK_NAME

        if stdout:
            logger.debug("Tiger fork response: %s", stdout.decode())
        
        logger.info(f"Successfully created database fork: {fork_name}")
        return fork_name
        
    except FileNotFoundError:
        logger.warning("Tiger CLI not found. Falling back to primary database.")
        force_primary_mode = True
        return PRIMARY_FORK_NAME
    except Exception as e:
        logger.error(f"Fork creation failed: {str(e)}")
        force_primary_mode = True
        return PRIMARY_FORK_NAME


async def blueprint_analysis_orchestrator(
    project_id: str,
    blueprint_data: Dict[str, Any],
    fork_name: str,
    systems_analyst_prompt: Optional[str] = None,
    bizops_analyst_prompt: Optional[str] = None
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
        systems_analyst_prompt: Optional custom prompt for systems analyst
        bizops_analyst_prompt: Optional custom prompt for bizops analyst
    """
    try:
        logger.info(f"Starting analysis orchestrator for project {project_id}, fork {fork_name}")
        
        # Run analysis agents on the blueprint with custom prompts if provided
        analyses = await agents.run_analyst_agents(
            blueprint_data,
            custom_systems_prompt=systems_analyst_prompt,
            custom_bizops_prompt=bizops_analyst_prompt
        )

        # Generate embeddings for each analysis finding in parallel
        embedding_tasks = [
            agents.generate_embedding(analysis.get("finding", ""))
            for analysis in analyses
        ]

        embedding_results = await asyncio.gather(*embedding_tasks, return_exceptions=True)

        for analysis, embedding_result in zip(analyses, embedding_results):
            if isinstance(embedding_result, Exception):
                logger.error(
                    "Embedding generation failed for analysis '%s': %s",
                    analysis.get("category", "unknown"),
                    embedding_result
                )
                analysis["finding_embedding"] = None
            else:
                analysis["finding_embedding"] = embedding_result if embedding_result else None

        # Add analyses to blueprint data
        blueprint_with_analyses = blueprint_data.copy()
        blueprint_with_analyses["analyses"] = analyses
        
        # Generate Mermaid diagram AFTER analyses are complete (so risks can be visualized)
        logger.info(f"Generating architecture diagram with risk markers for project {project_id}")
        try:
            # Get user prompt from main database
            main_db = next(get_db())
            try:
                project = main_db.query(models.Project).filter(models.Project.id == project_id).first()
                user_prompt = project.user_prompt if project else ""
            finally:
                main_db.close()
            
            mermaid_diagram = await agents.generate_mermaid_diagram(
                blueprint_with_analyses, 
                user_prompt
            )
            blueprint_with_analyses["mermaid_diagram"] = mermaid_diagram
            logger.info(f"Successfully generated diagram for project {project_id}")
        except Exception as diagram_error:
            logger.error(f"Diagram generation failed: {str(diagram_error)}")
            # Don't fail the entire process if diagram fails
            blueprint_with_analyses["mermaid_diagram"] = None
        
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
        if force_primary_mode or not TIGER_AVAILABLE:
            main_db = next(get_db())
            try:
                project = crud.get_project(main_db, project_id)
                if project and project.blueprints:
                    if all(blueprint.analyses for blueprint in project.blueprints):
                        crud.update_project_status(main_db, project_id, "completed")
                        logger.info(f"Project {project_id} marked as completed (primary DB fallback)")
            finally:
                main_db.close()
            return

        # Check blueprint fork to see if it has data (now only generating 1 microservices blueprint)
        fork_0_name = f"project_{project_id}_blueprint_0"
        
        blueprints_complete = 0
        
        try:
            fork_session = create_fork_session(fork_0_name)
            blueprints = fork_session.query(models.Blueprint).all()
            fork_session.close()
            
            if blueprints:
                blueprints_complete += 1
        except Exception:
            # Fork might not exist yet or have issues
            pass
        
        # Update main project status if blueprint is complete (only 1 microservices blueprint now)
        if blueprints_complete == 1:
            main_db = next(get_db())
            crud.update_project_status(main_db, project_id, "completed")
            main_db.close()
            logger.info(f"Project {project_id} marked as completed")
        
    except Exception as e:
        logger.error(f"Failed to update project completion status: {str(e)}")


def get_project_fork_names(project_id: str, max_forks: int = 10) -> List[str]:
    """Attempt to discover existing fork database names for a project."""
    if force_primary_mode or not TIGER_AVAILABLE:
        return [PRIMARY_FORK_NAME]

    fork_names: List[str] = []
    for index in range(max_forks):
        fork_name = f"project_{project_id}_blueprint_{index}"
        try:
            fork_session = create_fork_session(fork_name)
            fork_session.close()
            fork_names.append(fork_name)
        except Exception:
            # Stop at the first missing fork assuming contiguous indices
            break
    return fork_names


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


@app.get("/projects")
async def list_all_projects(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all projects with pagination and optional status filter.
    
    Query Parameters:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 20, max: 100)
        status: Optional status filter ('pending', 'processing', 'completed', 'error')
        
    Returns:
        List of projects with basic information, ordered by creation date (newest first)
    """
    try:
        # Validate limit
        if limit > 100:
            limit = 100
        
        # Get projects from database
        projects = crud.list_projects(db, skip=skip, limit=limit, status=status)
        
        # Convert to response format
        projects_list = []
        for project in projects:
            projects_list.append({
                "id": str(project.id),
                "user_prompt": project.user_prompt[:200] + "..." if len(project.user_prompt) > 200 else project.user_prompt,
                "status": project.status,
                "created_at": project.created_at.isoformat() if project.created_at else None,
                "updated_at": None  # Model doesn't have updated_at field
            })
        
        return {
            "projects": projects_list,
            "skip": skip,
            "limit": limit,
            "count": len(projects_list)
        }
        
    except Exception as e:
        logger.error(f"Failed to list projects: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list projects: {str(e)}"
        )


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
                
                # Start background analysis with hardcoded prompts
                background_tasks.add_task(
                    blueprint_analysis_orchestrator,
                    project_id,
                    blueprint,
                    fork_name,
                    None,  # systems_analyst_prompt - use default
                    None   # bizops_analyst_prompt - use default
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
        project_response = schemas.ProjectResponse.model_validate(
            serialize_project(project)
        )
        
        # If project is not completed, return basic info
        if project.status != "completed":
            return CompleteProjectResponse(
                project=project_response,
                blueprints=[]
            )
        
        if not TIGER_AVAILABLE or force_primary_mode:
            blueprints_data = []
            for blueprint in project.blueprints:
                blueprint_dict = {
                    "id": str(blueprint.id),
                    "name": blueprint.name,
                    "description": blueprint.description,
                    "pros": blueprint.pros,
                    "cons": blueprint.cons,
                    "mermaid_diagram": blueprint.mermaid_diagram,  # ← CRITICAL: Include diagram!
                    "analyses": [
                        {
                            "id": str(analysis.id),
                            "category": analysis.category,
                            "finding": analysis.finding,
                            "severity": analysis.severity,
                            "agent_type": analysis.agent_type
                        }
                        for analysis in blueprint.analyses
                    ]
                }
                blueprints_data.append(blueprint_dict)

            return CompleteProjectResponse(
                project=project_response,
                blueprints=blueprints_data
            )

        # Project is complete - fetch data from fork (only 1 microservices blueprint)
        blueprints_data = []
        
        for blueprint_index in [0]:  # Only blueprint_0 since we generate 1 microservices blueprint
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
                            "mermaid_diagram": blueprint.mermaid_diagram,  # ← CRITICAL: Include diagram!
                            "analyses": []
                        }
                        
                        # Add analyses
                        for analysis in blueprint.analyses:
                            analysis_dict = {
                                "id": str(analysis.id),
                                "category": analysis.category,
                                "finding": analysis.finding,
                                "severity": analysis.severity,
                                "agent_type": analysis.agent_type
                            }
                            blueprint_dict["analyses"].append(analysis_dict)
                        
                        blueprints_data.append(blueprint_dict)
                
                finally:
                    fork_session.close()
                    
            except Exception as e:
                logger.error(f"Failed to retrieve data from fork {fork_name}: {str(e)}")
                # Continue with other forks, don't fail the entire request
                continue

        # Fallback: if no blueprints were found via forks (common when Tiger CLI
        # isn't available after a restart), load them directly from the primary DB.
        if not blueprints_data:
            logger.warning(
                "No blueprints found via forks for project %s; falling back to primary database",
                project_id,
            )
            project_with_blueprints = crud.get_project_with_blueprints(db, project_id)
            if project_with_blueprints and project_with_blueprints.blueprints:
                for blueprint in project_with_blueprints.blueprints:
                    blueprint_dict = {
                        "id": str(blueprint.id),
                        "name": blueprint.name,
                        "description": blueprint.description,
                        "pros": blueprint.pros,
                        "cons": blueprint.cons,
                        "analyses": [
                            {
                                "id": str(analysis.id),
                                "category": analysis.category,
                                "finding": analysis.finding,
                                "severity": analysis.severity,
                                "agent_type": analysis.agent_type,
                            }
                            for analysis in blueprint.analyses
                        ],
                    }
                    blueprints_data.append(blueprint_dict)
        
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


@app.post("/projects/{project_id}/search", response_model=List[schemas.AnalysisResponse])
async def search_project_forks(
    project_id: str,
    search_request: SearchRequest,
    db: Session = Depends(get_db)
):
    """Hybrid keyword and semantic search across project forks."""

    query_text = search_request.query.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Query must not be empty")

    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        query_embedding = await agents.generate_embedding(query_text)
    except Exception as exc:
        logger.error("Failed to generate query embedding: %s", exc)
        raise HTTPException(status_code=500, detail="Embedding generation failed")

    if not query_embedding:
        raise HTTPException(status_code=400, detail="Embedding unavailable for provided query")

    fork_names = get_project_fork_names(project_id)
    if not fork_names:
        return []

    async def search_single_fork(fork_name: str) -> List[Dict[str, Any]]:
        try:
            fork_session = create_fork_session(fork_name)
        except Exception as exc:
            logger.error("Failed to connect to fork %s: %s", fork_name, exc)
            return []

        try:
            return await asyncio.to_thread(
                crud.hybrid_search_in_fork,
                fork_session,
                query_text,
                query_embedding
            )
        finally:
            fork_session.close()

    search_tasks = [search_single_fork(name) for name in fork_names]
    search_results = await asyncio.gather(*search_tasks, return_exceptions=True)

    combined_results: List[Dict[str, Any]] = []
    for result in search_results:
        if isinstance(result, Exception):
            logger.error("Fork search task failed: %s", result)
            continue
        combined_results.extend(result)

    # Optional re-ranking could be applied here if scores were available
    return [
        schemas.AnalysisResponse.model_validate(analysis)
        for analysis in combined_results
    ]


@app.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a project and all its related data (blueprints and analyses).
    
    Args:
        project_id: UUID string of the project to delete
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If project not found or deletion fails
    """
    try:
        logger.info(f"Attempting to delete project: {project_id}")
        
        # Delete the project (will cascade to blueprints and analyses)
        success = crud.delete_project(db, project_id)
        
        if not success:
            logger.warning(f"Project not found: {project_id}")
            raise HTTPException(status_code=404, detail="Project not found")
        
        logger.info(f"Successfully deleted project: {project_id}")
        return {"message": "Project deleted successfully", "project_id": project_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")
