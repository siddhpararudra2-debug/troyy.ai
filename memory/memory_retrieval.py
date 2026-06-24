"""
Memory retrieval service for the Engineering OS.
Handles semantic search, ranked retrieval, and context assembly.
"""
import logging
import uuid
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from memory.memory_storage import MemoryStorage
from database.models import MemoryEntry

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Result of a memory retrieval operation."""
    content: str
    memory_type: str
    title: Optional[str] = None
    summary: Optional[str] = None
    source: Optional[str] = None
    importance: float = 1.0
    score: float = 0.0
    metadata: dict = field(default_factory=dict)


class MemoryRetrieval:
    """
    Retrieves and ranks memories for context-aware AI interactions.
    Supports semantic search, project-scoped queries, and context assembly.
    """

    def __init__(self, session: AsyncSession):
        self.storage = MemoryStorage(session)

    async def retrieve_relevant_context(
        self,
        query: str,
        project_id: uuid.UUID,
        memory_types: Optional[list[str]] = None,
        max_results: int = 10,
        min_importance: float = 0.0,
    ) -> list[RetrievalResult]:
        """
        Retrieve the most relevant memory entries for a query.
        Uses text search with importance ranking.
        """
        # Get all project memories with type filter
        results = []
        if memory_types:
            for mt in memory_types:
                memories = await self.storage.get_project_memories(
                    project_id=project_id,
                    memory_type=mt,
                    limit=max_results,
                )
                results.extend(memories)
        else:
            results = await self.storage.get_project_memories(
                project_id=project_id,
                limit=max_results * 2,
            )

        # Score and rank
        scored = []
        for mem in results:
            if mem.importance < min_importance:
                continue
            
            score = self._calculate_relevance(query, mem)
            if score > 0.1:
                scored.append((score, mem))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        
        return [
            RetrievalResult(
                content=mem.content,
                memory_type=mem.memory_type,
                title=mem.title,
                summary=mem.summary,
                source=mem.source,
                importance=mem.importance,
                score=score,
                metadata=mem.metadata or {},
            )
            for score, mem in scored[:max_results]
        ]

    async def retrieve_recent_context(
        self,
        project_id: uuid.UUID,
        memory_types: Optional[list[str]] = None,
        limit: int = 5,
    ) -> list[RetrievalResult]:
        """Retrieve the most recent memory entries."""
        memories = await self.storage.get_project_memories(
            project_id=project_id,
            memory_type=memory_types[0] if memory_types else None,
            limit=limit,
        )
        
        return [
            RetrievalResult(
                content=mem.content,
                memory_type=mem.memory_type,
                title=mem.title,
                summary=mem.summary,
                source=mem.source,
                importance=mem.importance,
                score=1.0 - (i / limit),
                metadata=mem.metadata or {},
            )
            for i, mem in enumerate(memories)
        ]

    async def retrieve_high_importance(
        self,
        project_id: uuid.UUID,
        min_importance: float = 0.7,
        limit: int = 20,
    ) -> list[RetrievalResult]:
        """Retrieve high-importance memory entries."""
        memories = await self.storage.get_project_memories(
            project_id=project_id,
            limit=limit,
        )
        
        return [
            RetrievalResult(
                content=mem.content,
                memory_type=mem.memory_type,
                title=mem.title,
                summary=mem.summary,
                source=mem.source,
                importance=mem.importance,
                score=mem.importance,
                metadata=mem.metadata or {},
            )
            for mem in memories
            if mem.importance >= min_importance
        ]

    async def assemble_context(
        self,
        query: str,
        project_id: uuid.UUID,
        max_tokens: int = 4096,
    ) -> str:
        """
        Assemble a context string from relevant memories for AI prompts.
        """
        relevant = await self.retrieve_relevant_context(
            query=query,
            project_id=project_id,
            max_results=15,
        )
        
        if not relevant:
            return ""
        
        parts = ["### Relevant Project Context\n"]
        token_estimate = 0
        
        for result in relevant:
            # Rough token estimation (4 chars per token)
            entry_text = f"\n**{result.memory_type.upper()}**"
            if result.title:
                entry_text += f": {result.title}"
            entry_text += f"\n{result.content[:500]}...\n"
            
            entry_tokens = len(entry_text) // 4
            
            if token_estimate + entry_tokens > max_tokens:
                break
            
            parts.append(entry_text)
            token_estimate += entry_tokens
        
        return "\n".join(parts)

    def _calculate_relevance(self, query: str, memory: MemoryEntry) -> float:
        """
        Calculate relevance score between a query and a memory entry.
        Uses keyword matching and importance weighting.
        """
        query_lower = query.lower()
        score = 0.0
        
        # Title match (highest weight)
        if memory.title:
            title_lower = memory.title.lower()
            if query_lower in title_lower:
                score += 0.5
            elif any(word in title_lower for word in query_lower.split()):
                score += 0.3
        
        # Content match
        content_lower = memory.content.lower()
        matched_terms = sum(1 for word in query_lower.split() if word in content_lower)
        if matched_terms > 0:
            content_score = min(matched_terms / len(query_lower.split()), 1.0) * 0.4
            score += content_score
        
        # Summary match
        if memory.summary:
            summary_lower = memory.summary.lower()
            if query_lower in summary_lower:
                score += 0.3
            elif any(word in summary_lower for word in query_lower.split()):
                score += 0.1
        
        # Tag match
        if memory.tags:
            tag_match = sum(1 for tag in memory.tags if tag.lower() in query_lower)
            score += min(tag_match * 0.1, 0.2)
        
        # Apply importance multiplier
        score *= (0.5 + 0.5 * memory.importance)
        
        return min(score, 1.0)