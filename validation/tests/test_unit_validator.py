import pytest
import asyncio
from validation.services.unit_validator import UnitValidator
from validation.schemas.validation import Severity

@pytest.mark.asyncio
async def test_unit_validator_catches_mismatch():
    validator = UnitValidator()
    data = {
        "calculations": [
            {"name": "Thrust", "value": 10, "unit": "kg", "expected_unit": "N"}
        ]
    }
    issues = await validator.validate(data)
    
    assert len(issues) == 1
    assert issues[0].severity == Severity.CRITICAL
    assert "Unit mismatch" in issues[0].description

@pytest.mark.asyncio
async def test_unit_validator_passes_valid():
    validator = UnitValidator()
    data = {
        "calculations": [
            {"name": "Power", "value": 500, "unit": "W", "expected_unit": "W"}
        ]
    }
    issues = await validator.validate(data)
    assert len(issues) == 0
