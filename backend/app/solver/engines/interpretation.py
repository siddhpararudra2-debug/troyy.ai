"""
Troy — Interpretation Engine (Adapter)
Converts calculations into engineering meaning by delegating to InterpretationService.
"""

from __future__ import annotations

from app.solver.engines.base import BaseEngine
from app.solver.models import SolverState


class InterpretationEngine(BaseEngine):
    name = "InterpretationEngine"

    async def _execute(self, state: SolverState) -> SolverState:
        from app.solver.services.interpretation_service import InterpretationService
        service = InterpretationService()
        state.interpretation = await service.interpret_results(state)
        return state
