"""
Troy — Calculation Orchestrator (Legacy Adapter)
Coordinates the Engineering Solver and Reasoning Engine pipeline.
"""

from __future__ import annotations

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.solver.models.domain_models import SolverState
from app.solver.services.orchestration_service import OrchestrationService

logger = logging.getLogger("solver.orchestrator")


class CalculationOrchestrator:
    """Legacy adapter for calculation orchestration."""

    async def solve(
        self,
        session_id: str,
        project_id: str,
        user_query: str,
        db: AsyncSession,
    ) -> SolverState:
        """Delegates to the new OrchestrationService."""
        service = OrchestrationService()
        return await service.solve(
            session_id=session_id,
            project_id=project_id,
            user_query=user_query,
            db=db,
        )
