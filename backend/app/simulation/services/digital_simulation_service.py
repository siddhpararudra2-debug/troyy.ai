"""
Digital Simulation Service
"""
import uuid
import time
from datetime import datetime
from app.simulation.schemas.schemas import (
    DigitalSimulationRequest,
    DigitalSimulationResponse
)


class DigitalSimulationService:
    @staticmethod
    def simulate(request: DigitalSimulationRequest) -> DigitalSimulationResponse:
        start_time = time.time()
        return DigitalSimulationResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            logic_states={"clk": 0, "data": 1},
            timing_analysis={"t_setup": 10e-9},
            bus_activity=[],
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
