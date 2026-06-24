"""
Simulation Module Tests
"""
from app.simulation.services.circuit_simulation_service import CircuitSimulationService
from app.simulation.schemas.schemas import CircuitSimulationRequest
from app.simulation.services.fea_engine import FEAEngine
from app.simulation.services.cfd_engine import CFDEngine
from app.simulation.services.verification.requirement_validator import RequirementValidator
from app.simulation.schemas.schemas import (
    FEASimulationRequest,
    CFDSimulationRequest,
    VerificationRequest
)


def test_circuit_simulation():
    request = CircuitSimulationRequest(
        project_id="test-123",
        simulation_type="circuit"
    )
    response = CircuitSimulationService.simulate(request)
    assert response.project_id == "test-123"
    assert response.voltages.get("Vcc") == 12.0


def test_fea_static_analysis():
    engine = FEAEngine()
    result = engine.run_static_analysis(
        material_properties={"E": 70e9, "yield": 250e6},
        loads=[{"force": 1000, "direction": "z"}],
        constraints=[{"type": "fixed", "face": "bottom"}]
    )
    assert "stress_results" in result
    assert "safety_factors" in result
    assert result["safety_factors"]["yield"] > 1.0


def test_fea_modal_analysis():
    engine = FEAEngine()
    result = engine.run_modal_analysis(
        material_properties={"E": 70e9, "density": 2700}
    )
    assert "natural_frequencies" in result
    assert len(result["natural_frequencies"]) == 3


def test_cfd_external_aerodynamics():
    engine = CFDEngine()
    result = engine.run_external_aerodynamics(
        geometry={},
        fluid_props={"density": 1.225, "viscosity": 1.8e-5},
        boundary_conditions=[{"type": "inlet", "velocity": 50}]
    )
    assert "lift_coefficient" in result
    assert "drag_coefficient" in result
    assert result["lift_coefficient"] > 0


def test_verification():
    validator = RequirementValidator()
    result = validator.verify_requirements(
        requirements=[
            {"id": "R-001", "description": "Max stress < 200MPa", "criteria": True},
            {"id": "R-002", "description": "Mass < 5kg", "criteria": True}
        ],
        project_id="test-456"
    )
    assert len(result["requirements_verified"]) == 2
    assert all(req["status"] == "passed" for req in result["requirements_verified"])
