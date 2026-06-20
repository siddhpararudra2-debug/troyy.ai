"""
Audit Management Service
"""
import uuid
from datetime import datetime
from app.compliance.schemas.schemas import (
    AuditRequest,
    AuditResponse,
    AuditFinding
)


class AuditService:
    @staticmethod
    def create_audit(request: AuditRequest) -> AuditResponse:
        findings = []
        return AuditResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            audit_type=request.audit_type,
            auditor=request.auditor,
            findings=findings,
            overall_result="pending",
            created_at=datetime.utcnow()
        )
