"""
Troy — Memory Schemas
Pydantic models for project memory (decisions, assumptions, constraints, notes).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class MemoryCreate(BaseModel):
    """Create a new memory entry."""
    project_id: str
    entry_type: str = Field(..., pattern=r"^(decision|assumption|constraint|note|reference)$")
    content: str = Field(..., min_length=1, max_length=5000)
    context: str = Field("", max_length=2000)
    tags: list[str] = []


class MemoryResponse(BaseModel):
    """Memory entry response."""
    id: str
    project_id: str
    entry_type: str
    content: str
    context: str
    tags: list[str]
    relevance_score: float
    created_at: str
    accessed_at: str


class MemoryListResponse(BaseModel):
    """List of memory entries."""
    entries: list[MemoryResponse]
    total: int
