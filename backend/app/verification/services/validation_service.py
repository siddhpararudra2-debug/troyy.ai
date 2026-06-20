"""
Validation Service
"""
import uuid
from datetime import datetime
from app.verification.schemas.schemas import (
    BaseVerificationRequest,
    VerificationPlanResponse,
    VerificationActivity
)


class ValidationService:
    @staticmethod
    def create_validation_plan(request: BaseVerificationRequest) -> VerificationPlanResponse:
        activities = [
            VerificationActivity(
                id=str(uuid.uuid4()),
                name="Functional Validation",
                description="Validate system functions meet requirements",
                method="test"
            ),
            VerificationActivity(
                id=str(uuid.uuid4()),
                name="Performance Validation",
                description="Validate system performance meets specifications",
                method="demonstration"
            )
        ]
        return VerificationPlanResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            verification_type="validation",
            activities=activities,
            created_at=datetime.utcnow()
        )
