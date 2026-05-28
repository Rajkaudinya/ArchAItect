import os
import json
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Path
from typing import List
from app.config import settings
from app.models.project import ProjectInDB, ProjectCreate, ProjectUpdate

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
    return projects

@router.post("", response_model=ProjectInDB)
def create_project(payload: ProjectCreate):
    projects = load_projects()
    new_project = {
        "id": f"project-{uuid4().hex[:8]}",
        "name": payload.name,
        "description": payload.description or "",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "version": 1
    }
    projects.append(new_project)
    save_projects(projects)
    return new_project

@router.delete("/{project_id}")
def delete_project(project_id: str = Path(...)):
    projects = load_projects()
    filtered = [p for p in projects if p["id"] != project_id]
    if len(filtered) == len(projects):
        raise HTTPException(status_code=404, detail="Project not found")
    save_projects(filtered)
    return {"success": True, "message": "Project deleted"}
