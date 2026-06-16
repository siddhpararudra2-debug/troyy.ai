"""
Troy — Memory Service
Business logic for project memory management.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.schemas import MemoryCreate, MemoryResponse, MemoryListResponse
from app.core.logging import get_logger

logger = get_logger("memory")


async def add_memory(data: MemoryCreate, db: AsyncSession) -> MemoryResponse:
    """Add a memory entry to a project."""
    entry_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    await db.execute(
        text("""
            INSERT INTO memory_entries (id, project_id, entry_type, content, context,
                tags_json, relevance_score, created_at, accessed_at)
            VALUES (:id, :project_id, :type, :content, :context,
                :tags, 1.0, :now, :now)
        """),
        {
            "id": entry_id, "project_id": data.project_id,
            "type": data.entry_type, "content": data.content,
            "context": data.context, "tags": json.dumps(data.tags),
            "now": now,
        },
    )
    await db.commit()

    return MemoryResponse(
        id=entry_id, project_id=data.project_id,
        entry_type=data.entry_type, content=data.content,
        context=data.context, tags=data.tags,
        relevance_score=1.0, created_at=now, accessed_at=now,
    )


async def get_project_memory(
    project_id: str, db: AsyncSession, entry_type: str | None = None
) -> MemoryListResponse:
    """Get all memory entries for a project."""
    if entry_type:
        result = await db.execute(
            text("""
                SELECT id, project_id, entry_type, content, context,
                    tags_json, relevance_score, created_at, accessed_at
                FROM memory_entries
                WHERE project_id = :pid AND entry_type = :type
                ORDER BY created_at DESC
            """),
            {"pid": project_id, "type": entry_type},
        )
    else:
        result = await db.execute(
            text("""
                SELECT id, project_id, entry_type, content, context,
                    tags_json, relevance_score, created_at, accessed_at
                FROM memory_entries
                WHERE project_id = :pid
                ORDER BY created_at DESC
            """),
            {"pid": project_id},
        )

    rows = result.fetchall()
    entries = [
        MemoryResponse(
            id=row[0], project_id=row[1], entry_type=row[2],
            content=row[3], context=row[4],
            tags=json.loads(row[5]) if row[5] else [],
            relevance_score=row[6], created_at=row[7] or "",
            accessed_at=row[8] or "",
        )
        for row in rows
    ]

    return MemoryListResponse(entries=entries, total=len(entries))


async def search_memory(
    query: str, db: AsyncSession, project_id: str | None = None
) -> MemoryListResponse:
    """Search memory entries by content."""
    if project_id:
        result = await db.execute(
            text("""
                SELECT id, project_id, entry_type, content, context,
                    tags_json, relevance_score, created_at, accessed_at
                FROM memory_entries
                WHERE project_id = :pid AND (content LIKE :q OR context LIKE :q OR tags_json LIKE :q)
                ORDER BY relevance_score DESC, created_at DESC
            """),
            {"pid": project_id, "q": f"%{query}%"},
        )
    else:
        result = await db.execute(
            text("""
                SELECT id, project_id, entry_type, content, context,
                    tags_json, relevance_score, created_at, accessed_at
                FROM memory_entries
                WHERE content LIKE :q OR context LIKE :q OR tags_json LIKE :q
                ORDER BY relevance_score DESC, created_at DESC
            """),
            {"q": f"%{query}%"},
        )

    rows = result.fetchall()
    entries = [
        MemoryResponse(
            id=row[0], project_id=row[1], entry_type=row[2],
            content=row[3], context=row[4],
            tags=json.loads(row[5]) if row[5] else [],
            relevance_score=row[6], created_at=row[7] or "",
            accessed_at=row[8] or "",
        )
        for row in rows
    ]

    return MemoryListResponse(entries=entries, total=len(entries))
