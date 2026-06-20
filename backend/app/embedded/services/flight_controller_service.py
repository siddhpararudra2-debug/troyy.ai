"""
Flight Controller Service
"""
import uuid
import time
from datetime import datetime
from app.embedded.schemas.schemas import (
    FlightControllerRequest,
    FlightControllerResponse
)


class FlightControllerService:
    @staticmethod
    def generate(request: FlightControllerRequest) -> FlightControllerResponse:
        start_time = time.time()
        flight_tasks = [
            {"name": "Attitude Estimation", "priority": 1, "rate": 1000},
        ]
        navigation_tasks = [
            {"name": "Position Estimation", "priority": 2, "rate": 100},
        ]
        mission_tasks = [
            {"name": "Waypoint Navigation", "priority":3, "rate": 10},
        ]
        control_tasks = [
            {"name": "Attitude Control", "priority": 1, "rate": 1000},
        ]
        sensor_fusion_tasks = [
            {"name": "IMU + GPS Fusion", "priority": 1, "rate": 500},
        ]
        failsafe_systems = [
            "Low battery", "Lost GPS", "Lost RC",
        ]
        return FlightControllerResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            flight_tasks=flight_tasks,
            navigation_tasks=navigation_tasks,
            mission_tasks=mission_tasks,
            control_tasks=control_tasks,
            sensor_fusion_tasks=sensor_fusion_tasks,
            failsafe_systems=failsafe_systems,
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
