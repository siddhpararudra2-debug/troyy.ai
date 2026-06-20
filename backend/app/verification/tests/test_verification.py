"""
Verification Platform Unit Tests
"""
from app.verification.services.verification_planning_service import VerificationPlanningService
from app.verification.schemas.schemas import VerificationPlanRequest


def test_verification_plan_creation():
    request = VerificationPlanRequest(
        project_id="PROJ-123",
        verification_type="system"
    )
    response = VerificationPlanningService.create_plan(request)
    assert response.project_id == "PROJ-123"
    assert len(response.activities) > 0
