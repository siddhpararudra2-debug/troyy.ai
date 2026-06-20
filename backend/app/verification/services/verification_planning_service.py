"""
Verification Planning Service
"""
import uuid
from datetime import datetime
from app.verification.schemas.schemas import (
    VerificationPlanRequest,
    VerificationPlanResponse,
    VerificationActivity
)


class VerificationPlanningService:
    @staticmethod
    def create_plan(request: VerificationPlanRequest) -> VerificationPlanResponse:
        activities = [
            VerificationActivity(
                id=str(uuid.uuid4()),
                name="Requirement Verification",
                description="Verify all system requirements",
                method="inspection"
            ),
            VerificationActivity(
                id=str(uuid.uuid4()),
                name="Functional Testing",
                description="Test all functional features",
                method="test"
            )
        ]
        return VerificationPlanResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            verification_type=request.verification_type,
            activities=activities,
            created_at=datetime.utcnow()
        )
