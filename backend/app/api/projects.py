import os
import json
import logging
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Path, status
from typing import List
from app.config import settings
from app.models.project import ProjectInDB, ProjectCreate, ProjectUpdate

logger = logging.getLogger(__name__)
router = APIRouter()

def get_projects_file() -> str:
    return os.path.join(settings.DATA_DIR, "projects.json")

def load_projects() -> List[dict]:
    p_file = get_projects_file()
    if not os.path.exists(p_file):
        # Create empty template
        with open(p_file, "w") as f:
            json.dump([], f)
        return []
    try:
        with open(p_file, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_projects(projects: List[dict]):
    p_file = get_projects_file()
    with open(p_file, "w") as f:
        json.dump(projects, f, indent=2, default=str)

@router.get("", response_model=List[ProjectInDB])
def list_projects():
    """List all projects with error handling"""
    try:
        projects = load_projects()
        # Add dummy onboarding project if empty
        if not projects:
            onboarding = {
                "id": "project-onboarding",
                "name": "E-Commerce System Blueprint",
                "description": "Demonstration template mapping checkout services, gateways, and catalogs.",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "version": 1
            }
            projects.append(onboarding)
            save_projects(projects)
        logger.info(f"Retrieved {len(projects)} projects")
        return projects
    except Exception as e:
        logger.error(f"Failed to list projects: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve projects"
        )

@router.post("", response_model=ProjectInDB)
def create_project(payload: ProjectCreate):
    """Create a new project with validation"""
    try:
        if not payload.name or len(payload.name.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project name cannot be empty"
            )
        
        if len(payload.name) > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project name must be less than 200 characters"
            )
        
        projects = load_projects()
        
        # Check for duplicate project names
        if any(p["name"].lower() == payload.name.lower() for p in projects):
            logger.warning(f"Attempted to create duplicate project: {payload.name}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A project with this name already exists"
            )
        
        new_project = {
            "id": f"project-{uuid4().hex[:8]}",
            "name": payload.name.strip(),
            "description": payload.description.strip() if payload.description else "",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "version": 1
        }
        projects.append(new_project)
        save_projects(projects)
        
        logger.info(f"Created new project: {new_project['id']} - {new_project['name']}")
        return new_project
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project"
        )

@router.delete("/{project_id}")
def delete_project(project_id: str = Path(...)):
    projects = load_projects()
    filtered = [p for p in projects if p["id"] != project_id]
    if len(filtered) == len(projects):
        raise HTTPException(status_code=404, detail="Project not found")
    save_projects(filtered)
    return {"success": True, "message": "Project deleted"}
