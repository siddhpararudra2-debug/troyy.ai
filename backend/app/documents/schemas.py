"""
Troy — Document Schemas
Pydantic models for documentation generation.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class DocumentGenerateRequest(BaseModel):
    """Request to generate a document."""
    project_id: str
    calculation_id: str | None = None
    doc_type: str = Field("calculation_report", pattern=r"^(calculation_report|project_summary|custom)$")
    title: str = Field("", max_length=500)
    format: str = Field("markdown", pattern=r"^(markdown|html)$")


class DocumentResponse(BaseModel):
    """Generated document response."""
    id: str
    project_id: str
    calculation_id: str | None
    title: str
    doc_type: str
    format: str
    content: str
    created_at: str


class DocumentListResponse(BaseModel):
    """List of documents."""
    documents: list[DocumentResponse]
    total: int
