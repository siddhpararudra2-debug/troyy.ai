"""
Troy — Recommendation Service Tests
"""

from __future__ import annotations

import pytest
from app.solver.models.domain_models import SolverState
from app.solver.services.recommendation_service import RecommendationService


@pytest.mark.asyncio
async def test_generate_recommendations():
    service = RecommendationService()
    state = SolverState(
        session_id="test_sess",
        project_id="test_proj",
        user_query="test",
        domain="drones",
    )
    state.calculation_results = {"t_flight_min": 15.0}
    state.variables.known = {"t_endurance": {"value": 20.0}}
    
    res = await service.generate_recommendations(state)
    assert len(res.recommendations) > 0
    rec_texts = [r.recommendation for r in res.recommendations]
    assert any("Battery" in text for text in rec_texts)
