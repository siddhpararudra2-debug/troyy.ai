"""
Troy — Chat Schemas
Pydantic models for chat sessions and messages.
"""

from __future__ import annotations

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatMessageCreate(BaseModel):
    """Request to send a new chat message."""
    content: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None


class ChatMessageResponse(BaseModel):
    """Response for a chat message."""
    id: str
    session_id: str
    role: str
    content: str
    metadata: Dict[str, Any]
    created_at: str


class ChatSessionCreate(BaseModel):
    """Request to create a new chat session."""
    project_id: str
    title: Optional[str] = "New Chat"


class ChatSessionResponse(BaseModel):
    """Response for a chat session."""
    id: str
    project_id: str
    title: str
    created_at: str
    updated_at: str
    messages: list[ChatMessageResponse] = []


class ChatSessionListResponse(BaseModel):
    """List of chat sessions."""
    sessions: list[ChatSessionResponse]
    total: int
