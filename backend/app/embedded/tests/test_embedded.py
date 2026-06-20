"""
Embedded Systems & Firmware Module Tests
"""
from app.embedded.services.firmware_architecture_service import FirmwareArchitectureService
from app.embedded.schemas.schemas import FirmwareArchitectureRequest


def test_firmware_architecture():
    request = FirmwareArchitectureRequest(project_id="test-123")
    response = FirmwareArchitectureService.generate(request)
    assert response.project_id == "test-123"
    assert len(response.folder_structure) > 0
