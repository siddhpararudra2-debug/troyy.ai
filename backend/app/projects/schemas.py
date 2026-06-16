"""
Troy — Project Schemas
Pydantic models for project CRUD operations.
"""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    """Request to create a new project."""
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field("", max_length=2000)
    domain: str = Field("multi", pattern=r"^(aerospace|drones|robotics|electronics|multi)$")


class ProjectUpdate(BaseModel):
    """Request to update an existing project."""
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    domain: str | None = Field(None, pattern=r"^(aerospace|drones|robotics|electronics|multi)$")
    status: str | None = Field(None, pattern=r"^(active|archived)$")


class ProjectResponse(BaseModel):
    """Project data returned by the API."""
    id: str
    name: str
    description: str
    domain: str
    status: str
    created_at: str
    updated_at: str
    calculation_count: int = 0
    document_count: int = 0


class ProjectListResponse(BaseModel):
    """List of projects."""
    projects: list[ProjectResponse]
    total: int
