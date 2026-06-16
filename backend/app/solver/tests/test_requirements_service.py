"""
Troy — Requirements Extraction Service Tests
"""

from __future__ import annotations

import pytest
from app.solver.services.requirements_service import RequirementsService


@pytest.mark.asyncio
async def test_extract_drone_requirements():
    service = RequirementsService()
    query = "Design a delivery drone carrying 3.5 kg payload with 45 minutes hover time"
    req = await service.extract_requirements(query)

    assert req.project_type == "drone"
    assert req.mission_type == "delivery"
    assert "3.5kg" in req.payload
    assert "45minutes" in req.flight_time
    assert "range" in req.missing_requirements
    assert "environment" in req.missing_requirements


@pytest.mark.asyncio
async def test_extract_electronics_requirements():
    service = RequirementsService()
    query = "Size an amplifier circuit with 10V voltage input"
    req = await service.extract_requirements(query)

    assert req.project_type == "circuit"
    assert "input_voltage" in req.missing_requirements
