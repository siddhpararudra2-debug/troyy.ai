"""
Thermal Simulation Service
"""
import uuid
import time
from datetime import datetime
from app.simulation.schemas.schemas import (
    ThermalSimulationRequest,
    ThermalSimulationResponse
)


class ThermalSimulationService:
    @staticmethod
    def simulate(request: ThermalSimulationRequest) -> ThermalSimulationResponse:
        start_time = time.time()
        return ThermalSimulationResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            temperature_rise={"mosfet": 30.0},
            hotspots=[{"x": 50, "y": 50, "temp": 80.0}],
            cooling_requirements=["Add heatsink"],
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
