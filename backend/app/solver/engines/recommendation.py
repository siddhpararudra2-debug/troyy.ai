"""
Troy — Recommendation Engine (Adapter)
Converts calculations into actionable engineering advice by delegating to RecommendationService.
"""

from __future__ import annotations

from app.solver.engines.base import BaseEngine
from app.solver.models import SolverState


class RecommendationEngine(BaseEngine):
    name = "RecommendationEngine"

    async def _execute(self, state: SolverState) -> SolverState:
        from app.solver.services.recommendation_service import RecommendationService
        service = RecommendationService()
        state.recommendations = await service.generate_recommendations(state)
        return state
