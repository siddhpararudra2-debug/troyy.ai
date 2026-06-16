"""
Troy — Documentation Trigger Engine (Adapter)
Formats the final engineering solution into a structured report by delegating to DocumentationService.
"""

from __future__ import annotations

from app.solver.engines.base import BaseEngine
from app.solver.models import SolverState


class DocumentationTriggerEngine(BaseEngine):
    name = "DocumentationTriggerEngine"

    async def _execute(self, state: SolverState) -> SolverState:
        from app.solver.services.documentation_service import DocumentationService
        from app.core.database import async_session_factory

        service = DocumentationService()
        async with async_session_factory() as db:
            state.generated_report_id = await service.generate_report(state, db)
        return state
