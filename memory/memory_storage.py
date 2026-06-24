"""
Memory storage layer for the Engineering OS memory system.
Handles CRUD operations for memory entries in PostgreSQL.
"""
import logging
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import MemoryEntry, EngineeringDecision, Calculation, Document

logger = logging.getLogger(__name__)


class MemoryStorage:
    """PostgreSQL storage layer for memory entries."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def store_memory(
        self,
        project_id: uuid.UUID,
        memory_type: str,
        content: str,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        embedding_id: Optional[str] = None,
        source: Optional[str] = None,
        importance: float = 1.0,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> MemoryEntry:
        """Store a new memory entry."""
        entry = MemoryEntry(
            project_id=project_id,
            memory_type=memory_type,
            title=title,
            content=content,
            summary=summary,
            embedding_id=embedding_id,
            source=source,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
        )
        self.session.add(entry)
        await self.session.flush()
        logger.debug(f"Stored memory {entry.id} of type {memory_type}")
        return entry

    async def get_memory(self, memory_id: uuid.UUID) -> Optional[MemoryEntry]:
        """Retrieve a specific memory entry."""
        stmt = select(MemoryEntry).where(
            MemoryEntry.id == memory_id,
            MemoryEntry.is_deleted == False,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_project_memories(
        self,
        project_id: uuid.UUID,
        memory_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MemoryEntry]:
        """Get memories for a project, optionally filtered by type."""
        stmt = select(MemoryEntry).where(
            MemoryEntry.project_id == project_id,
            MemoryEntry.is_deleted == False,
        )
        if memory_type:
            stmt = stmt.where(MemoryEntry.memory_type == memory_type)
        
        stmt = stmt.order_by(MemoryEntry.importance.desc(), MemoryEntry.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_memory(
        self,
        memory_id: uuid.UUID,
        **kwargs,
    ) -> Optional[MemoryEntry]:
        """Update a memory entry."""
        entry = await self.get_memory(memory_id)
        if not entry:
            return None
        
        for key, value in kwargs.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        
        entry.updated_at = datetime.utcnow()
        await self.session.flush()
        return entry

    async def soft_delete_memory(self, memory_id: uuid.UUID) -> bool:
        """Soft delete a memory entry."""
        entry = await self.get_memory(memory_id)
        if not entry:
            return False
        
        entry.is_deleted = True
        entry.deleted_at = datetime.utcnow()
        await self.session.flush()
        return True

    async def store_decision(
        self,
        project_id: uuid.UUID,
        title: str,
        decision: str,
        description: Optional[str] = None,
        rationale: Optional[str] = None,
        alternatives: Optional[list[dict]] = None,
        criteria: Optional[list[dict]] = None,
        decision_makers: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
    ) -> EngineeringDecision:
        """Store an engineering decision."""
        entry = EngineeringDecision(
            project_id=project_id,
            title=title,
            description=description,
            decision=decision,
            rationale=rationale,
            alternatives=alternatives or [],
            criteria=criteria or [],
            decision_makers=decision_makers or [],
            tags=tags or [],
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def store_calculation(
        self,
        project_id: uuid.UUID,
        title: str,
        calculation_type: str,
        inputs: dict,
        outputs: Optional[dict] = None,
        formula: Optional[str] = None,
        result_summary: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> Calculation:
        """Store an engineering calculation."""
        entry = Calculation(
            project_id=project_id,
            title=title,
            calculation_type=calculation_type,
            inputs=inputs,
            outputs=outputs,
            formula=formula,
            result_summary=result_summary,
            tags=tags or [],
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def get_project_decisions(
        self,
        project_id: uuid.UUID,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> list[EngineeringDecision]:
        """Get engineering decisions for a project."""
        stmt = select(EngineeringDecision).where(
            EngineeringDecision.project_id == project_id,
            EngineeringDecision.is_deleted == False,
        )
        if status:
            stmt = stmt.where(EngineeringDecision.status == status)
        stmt = stmt.order_by(EngineeringDecision.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_project_calculations(
        self,
        project_id: uuid.UUID,
        calculation_type: Optional[str] = None,
        limit: int = 50,
    ) -> list[Calculation]:
        """Get engineering calculations for a project."""
        stmt = select(Calculation).where(
            Calculation.project_id == project_id,
            Calculation.is_deleted == False,
        )
        if calculation_type:
            stmt = stmt.where(Calculation.calculation_type == calculation_type)
        stmt = stmt.order_by(Calculation.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_memories(
        self,
        query: str,
        project_id: Optional[uuid.UUID] = None,
        memory_type: Optional[str] = None,
        limit: int = 20,
    ) -> list[MemoryEntry]:
        """
        Search memories using text-based search.
        Falls back to content matching when vector search unavailable.
        """
        stmt = select(MemoryEntry).where(
            MemoryEntry.is_deleted == False,
        )
        if project_id:
            stmt = stmt.where(MemoryEntry.project_id == project_id)
        if memory_type:
            stmt = stmt.where(MemoryEntry.memory_type == memory_type)
        
        # Simple text search on content and title
        search_pattern = f"%{query}%"
        stmt = stmt.where(
            MemoryEntry.content.ilike(search_pattern) |
            MemoryEntry.title.ilike(search_pattern) |
            MemoryEntry.summary.ilike(search_pattern)
        )
        stmt = stmt.order_by(MemoryEntry.importance.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_project_summary(self, project_id: uuid.UUID) -> dict:
        """Get a summary of all memory data for a project."""
        # Count memories
        mem_count = await self.session.execute(
            select(func.count(MemoryEntry.id)).where(
                MemoryEntry.project_id == project_id,
                MemoryEntry.is_deleted == False,
            )
        )
        total_memories = mem_count.scalar() or 0
        
        # Count decisions
        dec_count = await self.session.execute(
            select(func.count(EngineeringDecision.id)).where(
                EngineeringDecision.project_id == project_id,
                EngineeringDecision.is_deleted == False,
            )
        )
        total_decisions = dec_count.scalar() or 0
        
        # Count calculations
        calc_count = await self.session.execute(
            select(func.count(Calculation.id)).where(
                Calculation.project_id == project_id,
                Calculation.is_deleted == False,
            )
        )
        total_calculations = calc_count.scalar() or 0
        
        # Get memory type distribution
        type_counts = await self.session.execute(
            select(MemoryEntry.memory_type, func.count(MemoryEntry.id))
            .where(
                MemoryEntry.project_id == project_id,
                MemoryEntry.is_deleted == False,
            )
            .group_by(MemoryEntry.memory_type)
        )
        memory_types = {row[0]: row[1] for row in type_counts}
        
        return {
            "project_id": str(project_id),
            "total_memories": total_memories,
            "total_decisions": total_decisions,
            "total_calculations": total_calculations,
            "memory_types": memory_types,
        }