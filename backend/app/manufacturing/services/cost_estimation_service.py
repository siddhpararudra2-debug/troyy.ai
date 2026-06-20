"""
Cost Estimation Service
"""
import uuid
import time
from datetime import datetime
from app.manufacturing.schemas.schemas import (
    CostEstimateRequest,
    CostEstimateResponse,
    CostBreakdown
)


class CostEstimationService:
    @staticmethod
    def estimate(request: CostEstimateRequest) -> CostEstimateResponse:
        start_time = time.time()
        breakdown = CostBreakdown(
            materials=100.0,
            machining=200.0,
            printing=50.0,
            electronics=300.0,
            pcb=100.0,
            labor=400.0,
            testing=100.0,
            logistics=50.0,
            total=1300.0
        )
        return CostEstimateResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            cost_breakdown=breakdown,
            unit_cost=1300.0,
            batch_size=1,
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
