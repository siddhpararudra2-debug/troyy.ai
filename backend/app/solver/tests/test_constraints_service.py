"""
Troy — Constraints Service Tests
"""

from __future__ import annotations

import pytest
from app.solver.models.domain_models import AssumptionData, RequirementData
from app.solver.services.constraints_service import ConstraintsService


@pytest.mark.asyncio
async def test_drone_constraints():
    service = ConstraintsService()
    req = RequirementData(
        project_type="drone",
        payload="2.0 kg",
        safety_factor="2.0",
    )
    assumptions = []
    constraints = await service.identify_constraints("drones", req, assumptions)
    
    categories = [c.category for c in constraints]
    assert "Weight limits" in categories
    assert "Structural/Thrust limits" in categories
    
    # Verify the thrust constraint logic (2.0kg * 3.5 = 7.0kg MTOW. 7.0kg * 9.80665 * 2.0 = 137.29N)
    thrust_const = next(c for c in constraints if c.category == "Structural/Thrust limits")
    assert "137.29" in thrust_const.limit or "137" in thrust_const.limit
