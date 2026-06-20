"""
Mechanical Simulation Service
"""
import uuid
import time
from datetime import datetime
from app.simulation.schemas.schemas import (
    MechanicalSimulationRequest,
    MechanicalSimulationResponse
)


class MechanicalSimulationService:
    @staticmethod
    def simulate(request: MechanicalSimulationRequest) -> MechanicalSimulationResponse:
        start_time = time.time()
        return MechanicalSimulationResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            loads={"arm": 100.0},
            forces={"x": 50.0, "y": 50.0},
            deflections={"tip": 0.5},
            stress_estimates={"max_stress": 50e6},
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
