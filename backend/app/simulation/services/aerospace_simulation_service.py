"""
Aerospace Simulation Service
"""
import uuid
import time
from datetime import datetime
from app.simulation.schemas.schemas import (
    AerospaceSimulationRequest,
    AerospaceSimulationResponse
)


class AerospaceSimulationService:
    @staticmethod
    def simulate(request: AerospaceSimulationRequest) -> AerospaceSimulationResponse:
        start_time = time.time()
        return AerospaceSimulationResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            lift=1000.0,
            drag=100.0,
            stability={"static_margin": 0.1},
            performance={"max_speed": 100.0},
            risk_factors=["High angle of attack"],
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
