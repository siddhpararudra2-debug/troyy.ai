"""
Certification Planning Service
"""
import uuid
from datetime import datetime
from app.compliance.schemas.schemas import (
    CertificationPlanRequest,
    CertificationPlanResponse,
    CertificationTask
)


class CertificationService:
    @staticmethod
    def create_certification_plan(request: CertificationPlanRequest) -> CertificationPlanResponse:
        tasks = [
            CertificationTask(
                id=str(uuid.uuid4()),
                title="Complete System Requirements Document",
                description="Document all system requirements with traceability",
                required_evidence=["Requirements list", "Traceability matrix"]
            ),
            CertificationTask(
                id=str(uuid.uuid4()),
                title="Perform Risk Assessment",
                description="Perform FMEA and risk assessment",
                required_evidence=["Risk register", "FMEA report"]
            )
        ]
        return CertificationPlanResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            certification_type=request.certification_type,
            tasks=tasks,
            timeline={},
            created_at=datetime.utcnow()
        )
