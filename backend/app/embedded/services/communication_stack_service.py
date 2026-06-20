"""
Communication Stack Service
"""
import uuid
import time
from datetime import datetime
from app.embedded.schemas.schemas import (
    CommunicationStackRequest,
    CommunicationStackResponse
)


class CommunicationStackService:
    @staticmethod
    def generate(request: CommunicationStackRequest) -> CommunicationStackResponse:
        start_time = time.time()
        protocol_layers = {"physical": "UART/SPI/I2C", "data_link": "Frame Handling", "application": "Protocol Logic"}
        packet_definitions = {"telemetry": {"size": 64, "id": 0x01}}
        communication_frameworks = [{"name": "MAVLink", "protocol": "UART"}]
        return CommunicationStackResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            protocol_layers=protocol_layers,
            packet_definitions=packet_definitions,
            communication_frameworks=communication_frameworks,
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
