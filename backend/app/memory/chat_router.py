"""
Troy — Chat API Router
REST endpoints for the Copilot chat.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.memory import chat_service
from app.memory.chat_schemas import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionListResponse,
    ChatMessageCreate,
    ChatMessageResponse
)
from app.core.dependencies import DbSession

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions", response_model=ChatSessionResponse, status_code=201)
async def create_session(data: ChatSessionCreate, db: DbSession):
    """Create a new chat session for a project."""
    return await chat_service.create_chat_session(data, db)


@router.get("/sessions/project/{project_id}", response_model=ChatSessionListResponse)
async def get_project_sessions(project_id: str, db: DbSession):
    """Get all chat sessions for a project."""
    return await chat_service.get_project_sessions(project_id, db)


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
async def get_session_messages(session_id: str, db: DbSession):
    """Get all messages for a specific session."""
    return await chat_service.get_session_messages(session_id, db)


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def send_message(session_id: str, data: ChatMessageCreate, db: DbSession):
    """Send a message to the AI and get a response."""
    try:
        return await chat_service.send_message(session_id, data, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
