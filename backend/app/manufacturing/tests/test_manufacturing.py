"""
Manufacturing Intelligence Platform Tests
"""
from app.manufacturing.services.bom_generation_service import BOMGenerationService
from app.manufacturing.schemas.schemas import BOMRequest


def test_bom_generation():
    request = BOMRequest(project_id="test-123")
    response = BOMGenerationService.generate(request)
    assert response.project_id == "test-123"
    assert response.total_items > 0
