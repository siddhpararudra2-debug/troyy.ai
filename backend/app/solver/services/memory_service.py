"""
Troy — Memory Integration Service
Integrates the Engineering Solver with the Project Memory system.
Auto-persists solver assumptions, constraints, and recommendations, and
allows recalling them for project continuity.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.schemas import MemoryCreate
from app.memory.service import add_memory, get_project_memory
from app.solver.models.domain_models import SolverState

logger = logging.getLogger("solver.services.memory")


class MemoryService:
    """Manages reading and writing solver state to/from Project Memory."""

    async def save_to_memory(self, state: SolverState, db: AsyncSession) -> None:
        """
        Auto-persist assumptions, constraints, and recommendations to project memory.
        """
        logger.info(f"Saving solver run data to memory for session {state.session_id}")

        tags = ["solver", f"session:{state.session_id}", f"domain:{state.domain}"]

        # 1. Save Assumptions
        for a in state.assumptions:
            # Skip if the user overrode it with something empty, or just save the override if it exists
            content = f"Assumption: {a.user_override or a.assumption} (Confidence: {a.confidence_score})"
            try:
                await add_memory(
                    MemoryCreate(
                        project_id=state.project_id,
                        entry_type="assumption",
                        content=content,
                        context=f"Gap: {a.missing_information}. Reasoning: {a.reasoning}",
                        tags=tags,
                    ),
                    db=db,
                )
            except Exception as e:
                logger.error(f"Failed to save assumption to memory: {e}")

        # 2. Save Constraints
        for c in state.constraints:
            try:
                await add_memory(
                    MemoryCreate(
                        project_id=state.project_id,
                        entry_type="constraint",
                        content=f"Constraint: {c.limit} (Category: {c.category})",
                        context=f"Source: {c.source}",
                        tags=tags,
                    ),
                    db=db,
                )
            except Exception as e:
                logger.error(f"Failed to save constraint to memory: {e}")

        # 3. Save Recommendations
        for r in state.recommendations.recommendations:
            content = f"Recommendation: {r.recommendation}"
            context = f"Reasoning: {r.reasoning}"
            if r.expected_benefits:
                context += f" | Benefits: {r.expected_benefits}"
            if r.potential_risks:
                context += f" | Risks: {r.potential_risks}"

            try:
                await add_memory(
                    MemoryCreate(
                        project_id=state.project_id,
                        entry_type="decision",
                        content=content,
                        context=context,
                        tags=tags,
                    ),
                    db=db,
                )
            except Exception as e:
                logger.error(f"Failed to save recommendation to memory: {e}")

    async def recall_project_memory(self, project_id: str, db: AsyncSession) -> List[dict]:
        """
        Retrieve prior solver-related memory entries for a project.
        """
        logger.info(f"Recalling solver memory for project {project_id}")
        memories = await get_project_memory(project_id=project_id, db=db)
        
        # Filter for solver-generated entries
        solver_memories = []
        for entry in memories.entries:
            if "solver" in entry.tags:
                solver_memories.append({
                    "id": entry.id,
                    "entry_type": entry.entry_type,
                    "content": entry.content,
                    "context": entry.context,
                    "created_at": entry.created_at,
                })
        return solver_memories
