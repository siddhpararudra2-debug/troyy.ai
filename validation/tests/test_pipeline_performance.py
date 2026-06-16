import pytest
import time
import asyncio
from validation.schemas.validation import ValidationRequest
from validation.services.unit_validator import UnitValidator
from validation.services.assumptions_validator import AssumptionsValidator
from validation.services.safety_factor_validator import SafetyFactorValidator

@pytest.mark.asyncio
async def test_full_pipeline_under_500ms():
    request = ValidationRequest(
        project_id="PROJ-001",
        solver_run_id="SOLV-999",
        domain="UAV",
        design_data={"safety_factor": 1.3},
        assumptions=["Motor efficiency is 85%", "Battery weight is 2kg"],
        formulas_used=["P = IV"],
        calculations=[
            {"name": "Lift", "value": 50, "unit": "N", "expected_unit": "N"}
        ]
    )
    
    start = time.perf_counter()
    
    await asyncio.gather(
        UnitValidator().validate(request.model_dump()),
        AssumptionsValidator().validate(request.model_dump()),
        SafetyFactorValidator().validate(request.model_dump())
    )
    
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 500, f"Pipeline took {elapsed_ms}ms, exceeding 500ms target for validators"
