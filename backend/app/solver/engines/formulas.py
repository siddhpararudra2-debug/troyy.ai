"""
Troy — Formula Selection Engine (Adapter)
Selects the appropriate formulas from the registry by delegating to FormulaSelectionService.
"""

from __future__ import annotations

from app.solver.engines.base import BaseEngine
from app.solver.models import SolverState


class FormulaSelectionEngine(BaseEngine):
    name = "FormulaSelectionEngine"

    async def _execute(self, state: SolverState) -> SolverState:
        from app.solver.services.formula_selection_service import FormulaSelectionService
        service = FormulaSelectionService()
        state.selected_formulas = await service.select_formulas(state.domain, state.variables)
        return state
