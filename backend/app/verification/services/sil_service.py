"""
Software-In-The-Loop (SIL) Service
"""
import uuid
import time
from datetime import datetime
from app.verification.schemas.schemas import (
    SILRequest,
    SILResponse
)


class SILService:
    @staticmethod
    def run_sil(request: SILRequest) -> SILResponse:
        return SILResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            status="completed",
            results={"status": "pass", "coverage": 85.0},
            execution_time_sec=5.0,
            created_at=datetime.utcnow()
        )
