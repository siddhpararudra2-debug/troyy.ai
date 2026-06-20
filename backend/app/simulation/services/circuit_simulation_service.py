"""
Circuit Simulation Service
"""
import uuid
import time
from datetime import datetime
from app.simulation.schemas.schemas import (
    CircuitSimulationRequest,
    CircuitSimulationResponse
)


class CircuitSimulationService:
    @staticmethod
    def simulate(request: CircuitSimulationRequest) -> CircuitSimulationResponse:
        start_time = time.time()
        voltages = {"Vcc": 12.0, "Vout": 5.0}
        currents = {"Iout": 0.5}
        power = {"Pout": 2.5}
        waveforms = {"Vout": [0, 5, 5, 0]}
        return CircuitSimulationResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            voltages=voltages,
            currents=currents,
            power=power,
            waveforms=waveforms,
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
