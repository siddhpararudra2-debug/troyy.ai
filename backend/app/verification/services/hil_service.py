"""
Hardware-In-The-Loop (HIL) Service
"""
import uuid
import time
from datetime import datetime
from app.verification.schemas.schemas import (
    HILRequest,
    HILResponse
)


class HILService:
    @staticmethod
    def run_hil(request: HILRequest) -> HILResponse:
        return HILResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            status="completed",
            results={"status": "pass", "latency": 1.2},
            created_at=datetime.utcnow()
        )
