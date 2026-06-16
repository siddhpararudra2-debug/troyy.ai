"""
Troy — Assumptions Engine (Adapter)
Automatically generates engineering assumptions when information is missing by delegating to AssumptionsService.
"""

from __future__ import annotations

from app.solver.engines.base import BaseEngine
from app.solver.models import SolverState


class AssumptionsEngine(BaseEngine):
    name = "AssumptionsEngine"

    async def _execute(self, state: SolverState) -> SolverState:
        from app.solver.services.assumptions_service import AssumptionsService
        service = AssumptionsService()
        state.assumptions = await service.generate_assumptions(state.domain, state.requirements)
        return state
