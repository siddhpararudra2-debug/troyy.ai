"""
Troy — Constraint Identification Engine (Adapter)
Identifies physical and operational constraints for the engineering problem by delegating to ConstraintsService.
"""

from __future__ import annotations

from app.solver.engines.base import BaseEngine
from app.solver.models import SolverState


class ConstraintsEngine(BaseEngine):
    name = "ConstraintsEngine"

    async def _execute(self, state: SolverState) -> SolverState:
        from app.solver.services.constraints_service import ConstraintsService
        service = ConstraintsService()
        state.constraints = await service.identify_constraints(state.domain, state.requirements, state.assumptions)
        return state
