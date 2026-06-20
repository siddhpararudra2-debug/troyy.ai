"""
System Integration & Hardware-Software Co-Design Tests
"""
from app.system_integration.services.system_architecture_service import SystemArchitectureService
from app.system_integration.schemas.schemas import SystemArchitectureRequest


def test_system_architecture():
    request = SystemArchitectureRequest(project_id="test-123")
    response = SystemArchitectureService.generate(request)
    assert response.project_id == "test-123"
    assert len(response.subsystem_hierarchy) > 0
