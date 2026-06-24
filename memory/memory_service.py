"""
Memory Service - Central interface for the Engineering OS Memory System.
Coordinates storage, retrieval, and context assembly.
"""
import logging
import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from memory.memory_storage import MemoryStorage
from memory.memory_retrieval import MemoryRetrieval, RetrievalResult

logger = logging.getLogger(__name__)


class MemoryService:
    """
    Central service for managing engineering project memory.
    Provides unified interface for storing, retrieving, and searching memories.
    """

    def __init__(self, session: AsyncSession):
        self.storage = MemoryStorage(session)
        self.retrieval = MemoryRetrieval(session)
        self.session = session

    async def store(
        self,
        project_id: uuid.UUID,
        memory_type: str,
        content: str,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        source: Optional[str] = None,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> dict:
        """Store a memory entry and return its details."""
        entry = await self.storage.store_memory(
            project_id=project_id,
            memory_type=memory_type,
            content=content,
            title=title,
            summary=summary,
            source=source,
            importance=importance,
            tags=tags,
            metadata=metadata,
        )
        return {
            "id": str(entry.id),
            "project_id": str(entry.project_id),
            "memory_type": entry.memory_type,
            "title": entry.title,
            "summary": entry.summary,
            "importance": entry.importance,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
        }

    async def search(
        self,
        query: str,
        project_id: Optional[uuid.UUID] = None,
        memory_types: Optional[list[str]] = None,
        limit: int = 20,
        use_semantic: bool = False,
    ) -> list[RetrievalResult]:
        """
        Search memories by query text.
        
        Args:
            query: Search query text
            project_id: Optional project filter
            memory_types: Optional type filter
            limit: Max results
            use_semantic: Use semantic search (requires embedding service)
        """
        if project_id:
            return await self.retrieval.retrieve_relevant_context(
                query=query,
                project_id=project_id,
                memory_types=memory_types,
                max_results=limit,
            )
        else:
            # Fall back to text search across all projects
            results = await self.storage.search_memories(
                query=query,
                memory_type=memory_types[0] if memory_types else None,
                limit=limit,
            )
            return [
                RetrievalResult(
                    content=r.content,
                    memory_type=r.memory_type,
                    title=r.title,
                    summary=r.summary,
                    source=r.source,
                    importance=r.importance,
                    score=r.importance,
                    metadata=r.metadata or {},
                )
                for r in results
            ]

    async def get_context(
        self,
        query: str,
        project_id: uuid.UUID,
        max_tokens: int = 4096,
    ) -> str:
        """Assemble context string from project memories for AI prompts."""
        return await self.retrieval.assemble_context(
            query=query,
            project_id=project_id,
            max_tokens=max_tokens,
        )

    async def store_conversation_memory(
        self,
        project_id: uuid.UUID,
        user_message: str,
        assistant_response: str,
        model_used: str,
    ) -> dict:
        """Store a conversation exchange as memory."""
        content = f"User: {user_message}\n\nAssistant ({model_used}): {assistant_response}"
        summary = f"Conversation about: {user_message[:100]}..."
        
        return await self.store(
            project_id=project_id,
            memory_type="conversation",
            content=content,
            summary=summary,
            source=model_used,
            importance=0.8,
            tags=["conversation", model_used],
        )

    async def store_requirement(
        self,
        project_id: uuid.UUID,
        title: str,
        description: str,
        tags: Optional[list[str]] = None,
    ) -> dict:
        """Store an engineering requirement."""
        return await self.store(
            project_id=project_id,
            memory_type="requirement",
            content=description,
            title=title,
            importance=0.9,
            tags=tags,
        )

    async def store_decision(
        self,
        project_id: uuid.UUID,
        title: str,
        decision: str,
        rationale: Optional[str] = None,
        alternatives: Optional[list[dict]] = None,
        decision_makers: Optional[list[str]] = None,
    ) -> dict:
        """Store an engineering decision."""
        entry = await self.storage.store_decision(
            project_id=project_id,
            title=title,
            decision=decision,
            rationale=rationale,
            alternatives=alternatives,
            decision_makers=decision_makers,
        )
        return {
            "id": str(entry.id),
            "project_id": str(entry.project_id),
            "title": entry.title,
            "status": entry.status,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
        }

    async def get_project_summary(self, project_id: uuid.UUID) -> dict:
        """Get summary of all memory for a project."""
        return await self.storage.get_project_summary(project_id)

    async def get_recent_activity(
        self,
        project_id: uuid.UUID,
        limit: int = 10,
    ) -> list[dict]:
        """Get recent memory activity for a project."""
        entries = await self.storage.get_project_memories(
            project_id=project_id,
            limit=limit,
        )
        return [
            {
                "id": str(e.id),
                "type": e.memory_type,
                "title": e.title,
                "summary": e.summary,
                "importance": e.importance,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in entries
        ]