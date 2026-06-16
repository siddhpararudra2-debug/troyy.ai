"""
Troy — Chat Service
Business logic for chat sessions, messages, and mock AI responses incorporating project memory.
"""

from __future__ import annotations

import json
import uuid
import asyncio
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.chat_schemas import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionListResponse,
    ChatMessageCreate,
    ChatMessageResponse
)
from app.memory.context import ContextEngine
from app.solver.orchestrator import CalculationOrchestrator
from app.core.logging import get_logger

logger = get_logger("chat_service")
orchestrator = CalculationOrchestrator()


async def create_chat_session(data: ChatSessionCreate, db: AsyncSession) -> ChatSessionResponse:
    """Create a new chat session for a project."""
    session_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    await db.execute(
        text("""
            INSERT INTO chat_sessions (id, project_id, title, created_at, updated_at)
            VALUES (:id, :pid, :title, :now, :now)
        """),
        {"id": session_id, "pid": data.project_id, "title": data.title, "now": now}
    )
    await db.commit()

    return ChatSessionResponse(
        id=session_id, project_id=data.project_id, title=data.title,
        created_at=now, updated_at=now, messages=[]
    )


async def get_project_sessions(project_id: str, db: AsyncSession) -> ChatSessionListResponse:
    """List all chat sessions for a project."""
    res = await db.execute(
        text("SELECT id, project_id, title, created_at, updated_at FROM chat_sessions WHERE project_id = :pid ORDER BY updated_at DESC"),
        {"pid": project_id}
    )
    rows = res.fetchall()
    
    sessions = [
        ChatSessionResponse(
            id=row[0], project_id=row[1], title=row[2],
            created_at=row[3], updated_at=row[4]
        ) for row in rows
    ]
    return ChatSessionListResponse(sessions=sessions, total=len(sessions))


async def get_session_messages(session_id: str, db: AsyncSession) -> list[ChatMessageResponse]:
    """Get all messages for a session."""
    res = await db.execute(
        text("SELECT id, session_id, role, content, metadata_json, created_at FROM chat_messages WHERE session_id = :sid ORDER BY created_at ASC"),
        {"sid": session_id}
    )
    rows = res.fetchall()
    return [
        ChatMessageResponse(
            id=row[0], session_id=row[1], role=row[2],
            content=row[3], metadata=json.loads(row[4] or "{}"), created_at=row[5]
        ) for row in rows
    ]


async def send_message(session_id: str, data: ChatMessageCreate, db: AsyncSession) -> ChatMessageResponse:
    """
    Process a user message, retrieve context, generate an AI response,
    and save both to the database.
    """
    # 1. Verify session exists
    session_res = await db.execute(
        text("SELECT project_id FROM chat_sessions WHERE id = :sid"),
        {"sid": session_id}
    )
    row = session_res.fetchone()
    if not row:
        raise ValueError("Session not found")
    project_id = row[0]

    now = datetime.utcnow().isoformat()

    # 2. Save user message
    user_msg_id = str(uuid.uuid4())
    await db.execute(
        text("""
            INSERT INTO chat_messages (id, session_id, role, content, metadata_json, created_at)
            VALUES (:id, :sid, 'user', :content, :meta, :now)
        """),
        {"id": user_msg_id, "sid": session_id, "content": data.content, "meta": json.dumps(data.metadata or {}), "now": now}
    )

    # Update session updated_at
    await db.execute(
        text("UPDATE chat_sessions SET updated_at = :now WHERE id = :sid"),
        {"now": now, "sid": session_id}
    )
    await db.commit()

    # 3. Retrieve Context
    context = await ContextEngine.build_context(project_id, db, session_id)
    
    # 4. Generate AI Response using the Orchestrator Multi-Agent Pipeline
    state = await orchestrator.solve(
        session_id=session_id,
        project_id=project_id,
        user_query=data.content,
        db=db
    )
    
    ai_content = f"{state.interpretation.interpretation}\n\n"
    if state.recommendations.recommendations:
        ai_content += "Recommendations:\n"
        for r in state.recommendations.recommendations:
            ai_content += f"- {r}\n"
            
    if state.generated_report_id:
        ai_content += "\n*A detailed engineering report has been generated.*"
        
    if state.errors:
        ai_content = f"I encountered errors while solving this: {state.errors}"

    # 5. Save AI message
    ai_msg_id = str(uuid.uuid4())
    ai_now = datetime.utcnow().isoformat()
    await db.execute(
        text("""
            INSERT INTO chat_messages (id, session_id, role, content, metadata_json, created_at)
            VALUES (:id, :sid, 'assistant', :content, '{}', :now)
        """),
        {"id": ai_msg_id, "sid": session_id, "content": ai_content, "now": ai_now}
    )
    await db.commit()

    return ChatMessageResponse(
        id=ai_msg_id, session_id=session_id, role="assistant",
        content=ai_content, metadata={}, created_at=ai_now
    )
