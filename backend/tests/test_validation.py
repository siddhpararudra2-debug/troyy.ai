import pytest
import asyncio
from typing import List

from app.solver.models import SolverState, RequirementData, AssumptionData, VariableData
from app.validation.service import ValidationService
from app.validation.validators.base import AsyncBaseValidator
from app.validation.validators.missing_requirements import MissingRequirementsValidator
from app.validation.validators.assumptions_check import DangerousAssumptionsValidator
from app.validation.validators.safety_margins import SafetyMarginValidator
from app.validation.validators.unrealistic_values import UnrealisticValuesValidator


@pytest.fixture
def base_solver_state():
    return SolverState(
        session_id="test_session",
        project_id="test_project",
        user_query="Design a standard drone carrying a payload.",
        domain="drones",
        requirements=RequirementData(
            mission_type="Surveillance",
            payload="1kg",
            endurance="30 mins",
            environment="Outdoor",
            safety_factor="1.5",
            missing_requirements=[]
        ),
        assumptions=[],
        variables=VariableData(
            known={"n_safety": {"value": 1.5}},
            derived={"m_total": {"value": 3.2}}
        ),
        calculation_results={"thrust_total": 4.8}
    )


@pytest.mark.asyncio
async def test_validation_service_success(base_solver_state):
    """Test that a healthy SolverState passes validation with no issues."""
    service = ValidationService(validators=[
        MissingRequirementsValidator(),
        DangerousAssumptionsValidator(),
        SafetyMarginValidator(),
        UnrealisticValuesValidator()
    ])
    issues = await service.validate(base_solver_state)
    
    assert isinstance(issues, list)
    assert len(issues) == 0


@pytest.mark.asyncio
async def test_missing_requirements_validator(base_solver_state):
    """Test that missing requirements are correctly flagged."""
    # 1. Unknown requirements should raise an error
    state = base_solver_state.model_copy(deep=True)
    state.requirements.missing_requirements = ["battery_capacity"]
    
    validator = MissingRequirementsValidator()
    issues = await validator.validate(state)
    assert len(issues) == 1
    assert issues[0].severity == "error"
    assert issues[0].category == "Requirements"
    assert "battery_capacity" in issues[0].message
    
    # 2. Drone payload missing should raise a warning
    state_no_payload = base_solver_state.model_copy(deep=True)
    state_no_payload.requirements.payload = None
    issues_no_payload = await validator.validate(state_no_payload)
    assert len(issues_no_payload) == 1
    assert issues_no_payload[0].severity == "warning"
    assert "payload" in issues_no_payload[0].message.lower()


@pytest.mark.asyncio
async def test_dangerous_assumptions_validator(base_solver_state):
    """Test that risky assumptions are flagged."""
    state = base_solver_state.model_copy(deep=True)
    state.assumptions = [
        AssumptionData(
            missing_information="Wind speed",
            assumption="We assume calm weather conditions during flight",
            reasoning="Simplifying assumption"
        )
    ]
    
    validator = DangerousAssumptionsValidator()
    issues = await validator.validate(state)
    assert len(issues) == 1
    assert issues[0].severity == "warning"
    assert "calm weather" in issues[0].message.lower()


@pytest.mark.asyncio
async def test_safety_margin_validator(base_solver_state):
    """Test low safety margins in aerospace and drone domains."""
    validator = SafetyMarginValidator()
    
    # Aerospace: safety factor < 1.5 should be an error
    state_aero = base_solver_state.model_copy(deep=True)
    state_aero.domain = "aerospace"
    state_aero.variables.known["n_safety"] = {"value": 1.4}
    issues_aero = await validator.validate(state_aero)
    assert len(issues_aero) == 1
    assert issues_aero[0].severity == "error"
    assert "aerospace minimum standard" in issues_aero[0].message
    
    # Drones: safety factor < 1.2 should be a warning
    state_drone = base_solver_state.model_copy(deep=True)
    state_drone.domain = "drones"
    state_drone.variables.known["n_safety"] = {"value": 1.1}
    issues_drone = await validator.validate(state_drone)
    assert len(issues_drone) == 1
    assert issues_drone[0].severity == "warning"
    assert "low for UAVs" in issues_drone[0].message


@pytest.mark.asyncio
async def test_unrealistic_values_validator(base_solver_state):
    """Test validator flags non-positive or negative values."""
    validator = UnrealisticValuesValidator()
    
    # 1. Non-positive known variables
    state_var = base_solver_state.model_copy(deep=True)
    state_var.variables.known["mass_limit"] = {"value": -0.5}
    issues = await validator.validate(state_var)
    assert len(issues) == 1
    assert issues[0].severity == "error"
    assert "non-positive value" in issues[0].message
    
    # 2. Negative calculation results
    state_calc = base_solver_state.model_copy(deep=True)
    state_calc.calculation_results["efficiency"] = -10.0
    issues_calc = await validator.validate(state_calc)
    assert len(issues_calc) == 1
    assert issues_calc[0].severity == "error"
    assert "efficiency" in issues_calc[0].message


@pytest.mark.asyncio
async def test_validation_service_extensibility(base_solver_state):
    """Test that custom validators can be passed or registered."""
    class CustomValidator(AsyncBaseValidator):
        name = "CustomValidator"
        async def validate(self, state: SolverState):
            from app.validation.schemas.validation_schemas import ValidationIssueSchema
            return [ValidationIssueSchema(
                severity="warning",
                category="Custom",
                message="Custom warning",
                validator_name=self.name,
                engineering_reasoning="Custom check failed",
                recommendation="Fix custom issue"
            )]
            
    # Test passing custom validators to __init__
    custom_service = ValidationService(validators=[CustomValidator()])
    assert len(custom_service.validators) == 1
    assert isinstance(custom_service.validators[0], CustomValidator)
    
    issues = await custom_service.validate(base_solver_state)
    assert len(issues) == 1
    assert issues[0].category == "Custom"
    
    # Test registering a validator dynamically
    service = ValidationService(validators=[])  # start with empty
    initial_count = len(service.validators)
    service.register_validator(CustomValidator())
    assert len(service.validators) == initial_count + 1
    
    issues2 = await service.validate(base_solver_state)
    assert len(issues2) == 1
    assert issues2[-1].category == "Custom"


@pytest.mark.asyncio
async def test_validation_service_error_handling(base_solver_state):
    """Test that exceptions in individual validators are safely aggregated."""
    class CrashingValidator(AsyncBaseValidator):
        name = "CrashingValidator"
        async def validate(self, state: SolverState):
            raise RuntimeError("Database error or simulation crash")
            
    service = ValidationService(validators=[CrashingValidator()])
    issues = await service.validate(base_solver_state)
    
    assert len(issues) == 1
    assert issues[0].severity == "error"
    assert issues[0].category == "System"
    assert "CrashingValidator" in issues[0].validator_name
    assert "Database error or simulation crash" in issues[0].message
