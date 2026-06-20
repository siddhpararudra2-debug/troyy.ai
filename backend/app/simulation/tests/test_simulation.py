"""
Simulation Module Tests
"""
from app.simulation.services.circuit_simulation_service import CircuitSimulationService
from app.simulation.schemas.schemas import CircuitSimulationRequest


def test_circuit_simulation():
    request = CircuitSimulationRequest(
        project_id="test-123",
        simulation_type="circuit"
    )
    response = CircuitSimulationService.simulate(request)
    assert response.project_id == "test-123"
    assert response.voltages.get("Vcc") == 12.0
