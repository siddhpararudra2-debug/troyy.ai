"""
Driver Generation Service
"""
import uuid
import time
from datetime import datetime
from app.embedded.schemas.schemas import (
    DriverGenerationRequest,
    DriverGenerationResponse,
    DriverDefinition
)


class DriverGenerationService:
    @staticmethod
    def generate(request: DriverGenerationRequest) -> DriverGenerationResponse:
        start_time = time.time()
        drivers = []
        driver_types = request.driver_types or ["GPIO", "UART", "I2C", "SPI", "ADC"]
        for dt in driver_types:
            drivers.append(DriverDefinition(
                type=dt,
                hal_layer=f"hal_{dt.lower()}.c",
                driver_layer=f"drv_{dt.lower()}.c",
                abstraction_layer=f"abs_{dt.lower()}.c"
            ))
        return DriverGenerationResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            drivers=drivers,
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
