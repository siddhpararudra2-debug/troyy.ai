"""
Troy — Requirements Extraction Engine (Adapter)
Converts user requests into structured engineering requirements by delegating to RequirementsService.
"""

from __future__ import annotations

from app.solver.engines.base import BaseEngine
from app.solver.models import SolverState


class RequirementsExtractionEngine(BaseEngine):
    name = "RequirementsExtractionEngine"

    async def _execute(self, state: SolverState) -> SolverState:
        from app.solver.services.requirements_service import RequirementsService
        service = RequirementsService()
        state.requirements = await service.extract_requirements(state.user_query)
        state.domain = state.requirements.raw_extracted.get("domain_inferred", "multi")
        return state
