"""
Troy — Documents API Router
REST endpoints for document generation and retrieval.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.documents import service
from app.documents.schemas import (
    DocumentGenerateRequest,
    DocumentResponse,
    DocumentListResponse,
)
from app.core.dependencies import DbSession

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/generate", response_model=DocumentResponse, status_code=201)
async def generate_document(data: DocumentGenerateRequest, db: DbSession):
    """Generate an engineering document (calculation report or project summary)."""
    return await service.generate_document(data, db)


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str, db: DbSession):
    """Get a specific document."""
    doc = await service.get_document(doc_id, db)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/project/{project_id}", response_model=DocumentListResponse)
async def list_project_documents(project_id: str, db: DbSession):
    """List all documents for a project."""
    return await service.list_project_documents(project_id, db)
