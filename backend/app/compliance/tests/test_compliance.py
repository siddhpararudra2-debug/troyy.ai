"""
Compliance Platform Unit Tests
"""
from app.compliance.services.standards_service import StandardsService
from app.compliance.schemas.schemas import StandardRequest


def test_standard_creation():
    request = StandardRequest(
        standard_type="ISO",
        name="ISO 12100:2010",
        code="ISO 12100:2010",
        description="Safety of machinery"
    )
    result = StandardsService.create_standard(request)
    assert result.code == "ISO 12100:2010"
    assert result.standard_type == "ISO"
