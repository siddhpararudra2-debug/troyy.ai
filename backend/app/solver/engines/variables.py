"""
Troy — Variable Extraction Engine (Adapter)
Extracts Known, Unknown, Dependent, and Derived variables by delegating to VariableService.
"""

from __future__ import annotations

from app.solver.engines.base import BaseEngine
from app.solver.models import SolverState


class VariableExtractionEngine(BaseEngine):
    name = "VariableExtractionEngine"

    async def _execute(self, state: SolverState) -> SolverState:
        from app.solver.services.variable_service import VariableService
        service = VariableService()
        state.variables = await service.extract_variables(state.domain, state.requirements, state.assumptions)
        return state
