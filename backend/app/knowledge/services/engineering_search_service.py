"""
Engineering Search Service
"""
import uuid
import time
from datetime import datetime
from app.knowledge.schemas.schemas import (
    EngineeringSearchRequest,
    EngineeringSearchResponse,
    EngineeringSearchResult
)


class EngineeringSearchService:
    @staticmethod
    def search(request: EngineeringSearchRequest) -> EngineeringSearchResponse:
        start_time = time.time()
        results = [
            EngineeringSearchResult(
                id=str(uuid.uuid4()),
                type="component",
                title="Drone Motor MTR-2212",
                summary="High efficiency motor for quadcopters",
                score=0.95,
                metadata={"manufacturer": "T-Motor"},
                created_at=datetime.utcnow()
            ),
            EngineeringSearchResult(
                id=str(uuid.uuid4()),
                type="material",
                title="Carbon Fiber Tube 16mm",
                summary="Lightweight and strong for drone frames",
                score=0.88,
                metadata={"density": "1.6g/cm³"},
                created_at=datetime.utcnow()
            )
        ]
        return EngineeringSearchResponse(
            results=results,
            execution_time_ms=(time.time() - start_time) * 1000
        )
