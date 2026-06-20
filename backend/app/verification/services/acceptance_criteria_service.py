"""
Acceptance Criteria Service
"""
import uuid
from datetime import datetime
from app.verification.schemas.schemas import (
    AcceptanceCriteriaRequest,
    AcceptanceCriteriaResponse,
    AcceptanceCriterion
)


class AcceptanceCriteriaService:
    @staticmethod
    def generate_criteria(request: AcceptanceCriteriaRequest) -> AcceptanceCriteriaResponse:
        criteria = [
            AcceptanceCriterion(
                id=str(uuid.uuid4()),
                name="Flight Time",
                description="Total flight duration",
                target_value="30 minutes"
            ),
            AcceptanceCriterion(
                id=str(uuid.uuid4()),
                name="Payload Capacity",
                description="Maximum payload weight",
                target_value="5 kg"
            )
        ]
        return AcceptanceCriteriaResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            system_type=request.system_type,
            criteria=criteria,
            created_at=datetime.utcnow()
        )
