"""
Tolerance Service
"""
import uuid
import time
from datetime import datetime
from app.cad.schemas.schemas import CADToleranceRequest, CADToleranceResponse


class ToleranceService:
    @staticmethod
    def analyze(request: CADToleranceRequest) -> CADToleranceResponse:
        start_time = time.time()
        tolerances = [
            {"dimension": "Width", "nominal": 50, "tolerance": 0.1},
            {"dimension": "Hole Diameter", "nominal": 5, "tolerance": 0.05},
        ]
        gdt = [
            "Position tolerance for hole pattern",
            "Parallelism requirement for mating face",
        ]
        stackups = [
            {"name": "Stackup 1", "max": 50.2, "min": 49.8},
        ]
        return CADToleranceResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            tolerances=tolerances,
            gdt_recommendations=gdt,
            tolerance_stackups=stackups,
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow(),
        )
