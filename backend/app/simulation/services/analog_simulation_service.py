"""
Analog Simulation Service
"""
import uuid
import time
from datetime import datetime
from app.simulation.schemas.schemas import (
    AnalogSimulationRequest,
    AnalogSimulationResponse
)


class AnalogSimulationService:
    @staticmethod
    def simulate(request: AnalogSimulationRequest) -> AnalogSimulationResponse:
        start_time = time.time()
        return AnalogSimulationResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            gain=100.0,
            bandwidth=100000.0,
            noise=0.01,
            response_curves={"gain_vs_freq": [100, 100, 10]},
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
