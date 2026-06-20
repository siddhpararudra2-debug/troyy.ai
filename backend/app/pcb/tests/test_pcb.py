"""
PCB Intelligence Module Tests
"""
from app.pcb.services.pcb_architecture_service import PCBArchitectureService
from app.pcb.schemas.schemas import PCBArchitectureRequest


def test_pcb_architecture():
    request = PCBArchitectureRequest(
        project_id="test-123",
        board_width_mm=100,
        board_height_mm=80
    )
    response = PCBArchitectureService.generate(request)
    assert response.project_id == "test-123"
    assert response.board_width_mm == 100
    assert len(response.subsystem_regions) > 0
