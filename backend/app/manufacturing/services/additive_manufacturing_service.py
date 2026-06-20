"""
Additive Manufacturing Planning Service
"""
import uuid
import time
from datetime import datetime
from app.manufacturing.schemas.schemas import (
    PrintPlanRequest,
    PrintPlanResponse
)


class AdditiveManufacturingService:
    @staticmethod
    def plan(request: PrintPlanRequest) -> PrintPlanResponse:
        start_time = time.time()
        return PrintPlanResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            orientation="Flat",
            support_strategy="Tree Supports",
            material="PLA",
            print_time_hours=8.0,
            recommendations=["Increase infill to 20%"],
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
