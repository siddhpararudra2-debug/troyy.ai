"""
CNC Planning Service
"""
import uuid
import time
from datetime import datetime
from app.manufacturing.schemas.schemas import (
    CNCPlanRequest,
    CNCPlanResponse,
    CNCOperation
)


class CNCPlanningService:
    @staticmethod
    def plan(request: CNCPlanRequest) -> CNCPlanResponse:
        start_time = time.time()
        operations = [
            CNCOperation(name="Roughing", tool="10mm End Mill", spindle_speed=3000, feed_rate=500, estimated_time_min=10.0),
            CNCOperation(name="Finishing", tool="6mm Ball Mill", spindle_speed=6000, feed_rate=300, estimated_time_min=15.0)
        ]
        return CNCPlanResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            operations=operations,
            tool_selection=["10mm End Mill", "6mm Ball Mill"],
            sequence=["Roughing", "Finishing"],
            cycle_time_min=25.0,
            dfm_recommendations=["Use fillets to reduce stress"],
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
