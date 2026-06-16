"""
Troy — Project API Router
REST endpoints for project management.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.projects import service
from app.projects.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from app.core.dependencies import DbSession

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(data: ProjectCreate, db: DbSession):
    """Create a new engineering project."""
    return await service.create_project(data, db)


@router.get("", response_model=ProjectListResponse)
async def list_projects(db: DbSession):
    """List all projects with calculation and document counts."""
    return await service.list_projects(db)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, db: DbSession):
    """Get detailed project information."""
    project = await service.get_project(project_id, db)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, data: ProjectUpdate, db: DbSession):
    """Update project details."""
    project = await service.update_project(project_id, data, db)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: str, db: DbSession):
    """Archive a project (soft delete)."""
    deleted = await service.delete_project(project_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
