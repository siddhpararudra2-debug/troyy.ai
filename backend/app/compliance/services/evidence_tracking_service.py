"""
Evidence Tracking Service
"""
import uuid
from datetime import datetime
from app.compliance.schemas.schemas import (
    EvidenceRequest,
    EvidenceResponse
)


class EvidenceTrackingService:
    @staticmethod
    def add_evidence(request: EvidenceRequest) -> EvidenceResponse:
        return EvidenceResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            requirement_id=request.requirement_id,
            evidence_type=request.evidence_type,
            content=request.content,
            metadata=request.metadata,
            created_at=datetime.utcnow()
        )
