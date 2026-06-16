"""
Troy — Interpretation Service Tests
"""

from __future__ import annotations

import pytest
from app.solver.models.domain_models import ConstraintData, SolverState
from app.solver.services.interpretation_service import InterpretationService


@pytest.mark.asyncio
async def test_interpret_results():
    service = InterpretationService()
    state = SolverState(
        session_id="test_sess",
        project_id="test_proj",
        user_query="test",
        domain="drones",
        constraints=[
            ConstraintData(
                category="Weight limits",
                limit="Max Takeoff Weight (MTOW) <= 5.00 kg",
                source="Heuristics",
            )
        ],
    )
    # 1. Test violation (calculated 6.0kg vs limit <= 5.0kg)
    state.calculation_results = {"m_total": 6.0}
    res = await service.interpret_results(state)
    assert "Constraint Violated" in res.interpretation

    # 2. Test pass (calculated 4.0kg vs limit <= 5.0kg)
    state.calculation_results = {"m_total": 4.0}
    res2 = await service.interpret_results(state)
    assert "Constraint Passed" in res2.interpretation
