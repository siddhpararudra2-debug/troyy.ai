"""
Troy — Variable Service Tests
"""

from __future__ import annotations

import pytest
from app.solver.models.domain_models import AssumptionData, RequirementData
from app.solver.services.variable_service import VariableService


@pytest.mark.asyncio
async def test_extract_variables_drone():
    service = VariableService()
    req = RequirementData(
        project_type="drone",
        payload="1.5 kg",
        flight_time="30 min",
    )
    assumptions = [
        AssumptionData(
            missing_information="safety_factor",
            assumption="1.5",
            reasoning="Default assumption",
        )
    ]
    variables = await service.extract_variables("drones", req, assumptions)
    
    assert "m_payload" in variables.known
    assert variables.known["m_payload"]["value"] == 1.5
    assert "t_endurance" in variables.known
    assert variables.known["t_endurance"]["value"] == 30.0
    assert "g" in variables.constants
    assert "T_motor" in variables.unknown
