"""
Troy — Assumptions Service Tests
"""

from __future__ import annotations

import pytest
from app.solver.models.domain_models import RequirementData
from app.solver.services.assumptions_service import AssumptionsService


@pytest.mark.asyncio
async def test_generate_drone_assumptions():
    service = AssumptionsService()
    req = RequirementData(
        project_type="drone",
        mission_type="delivery",
        payload=None,
        flight_time=None,
    )
    assumptions = await service.generate_assumptions("drones", req)
    
    # Check that payload and flight time assumptions are generated since they are missing
    missing_info = [a.missing_information for a in assumptions]
    assert "payload" in missing_info
    assert "flight_time" in missing_info
    assert "safety_factor" in missing_info


@pytest.mark.asyncio
async def test_generate_electronics_assumptions():
    service = AssumptionsService()
    req = RequirementData(
        project_type="circuit",
        mission_type="general",
    )
    assumptions = await service.generate_assumptions("electronics", req)
    
    missing_info = [a.missing_information for a in assumptions]
    assert "input_voltage" in missing_info
    assert "ambient_temperature" in missing_info
