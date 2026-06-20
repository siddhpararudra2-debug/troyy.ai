"""
Compliance Engine Service
"""
import uuid
import time
from datetime import datetime
from app.compliance.schemas.schemas import (
    ComplianceCheckRequest,
    ComplianceCheckResponse,
    ComplianceIssue
)


class ComplianceEngineService:
    @staticmethod
    def check_compliance(request: ComplianceCheckRequest) -> ComplianceCheckResponse:
        start_time = time.time()
        issues = []
        # Mock issues
        if request.check_type == "mechanical":
            issues = [
                ComplianceIssue(
                    severity="medium",
                    description="Missing risk assessment for moving parts",
                    requirement="ISO 12100:2010 Clause 5"
                )
            ]
        return ComplianceCheckResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            overall_status="in-progress",
            compliance_score=0.75,
            issues=issues,
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
