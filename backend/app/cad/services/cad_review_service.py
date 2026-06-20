"""
CAD Review Service
"""
import uuid
import time
from datetime import datetime
from app.cad.schemas.schemas import CADReviewRequest, CADReviewResponse


class CADReviewService:
    @staticmethod
    def review(request: CADReviewRequest) -> CADReviewResponse:
        start_time = time.time()
        warnings = [
            "Part thickness near minimum constraint",
        ]
        recommendations = [
            "Increase wall thickness for rigidity",
            "Add fillets to reduce stress concentration",
        ]
        return CADReviewResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            warnings=warnings,
            recommendations=recommendations,
            approval_status="pending",
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow(),
        )
