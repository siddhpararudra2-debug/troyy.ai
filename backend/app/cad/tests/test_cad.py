"""
CAD Generation & Geometry Tests
"""
from app.cad.services.cad_generation_service import CADGenerationService
from app.cad.schemas.schemas import CADPartRequest


def test_cad_part_generation():
    request = CADPartRequest(project_id="test-123", part_type="bracket")
    response = CADGenerationService.generate_part(request)
    assert response.project_id == "test-123"
    assert len(response.features) > 0
