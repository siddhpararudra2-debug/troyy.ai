"""
Troy — Memory API Router
REST endpoints for project memory management.
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.memory import service
from app.memory.schemas import MemoryCreate, MemoryResponse, MemoryListResponse
from app.core.dependencies import DbSession

router = APIRouter(prefix="/memory", tags=["memory"])


@router.post("", response_model=MemoryResponse, status_code=201)
async def add_memory(data: MemoryCreate, db: DbSession):
    """Add a memory entry (decision, assumption, constraint, note, reference)."""
    return await service.add_memory(data, db)


@router.get("/project/{project_id}", response_model=MemoryListResponse)
async def get_project_memory(
    project_id: str,
    db: DbSession,
    entry_type: str | None = Query(None, description="Filter by entry type"),
):
    """Get all memory entries for a project."""
    return await service.get_project_memory(project_id, db, entry_type)


@router.get("/search", response_model=MemoryListResponse)
async def search_memory(
    q: str = Query(..., description="Search query"),
    project_id: str | None = Query(None, description="Optional project filter"),
    db: DbSession = None,
):
    """Search memory entries across projects."""
    return await service.search_memory(q, db, project_id)
