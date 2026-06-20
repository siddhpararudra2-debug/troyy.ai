"""
Hardware Software Mapping Service
"""
import uuid
import time
from datetime import datetime
from app.system_integration.schemas.schemas import (
    HardwareSoftwareMappingRequest,
    HardwareSoftwareMappingResponse,
)


class HardwareSoftwareMappingService:
    @staticmethod
    def map(request: HardwareSoftwareMappingRequest) -> HardwareSoftwareMappingResponse:
        start_time = time.time()
        graph = {
            "imu-sensor": ["imu-driver"],
            "imu-driver": ["sensor-task"],
            "sensor-task": ["state-estimator"],
        }
        mappings = [
            {"hardware": "imu-sensor", "software": "imu-driver"},
            {"hardware": "motor", "software": "motor-driver"},
        ]
        return HardwareSoftwareMappingResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            hw_sw_dependency_graph=graph,
            mappings=mappings,
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow(),
        )
