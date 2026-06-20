"""
Digital Thread Service
"""
import uuid
import time
from datetime import datetime
from app.system_integration.schemas.schemas import (
    DigitalThreadRequest,
    DigitalThreadResponse,
    DigitalThreadRecord,
)


class DigitalThreadService:
    @staticmethod
    def build(request: DigitalThreadRequest) -> DigitalThreadResponse:
        start_time = time.time()
        thread = [
            DigitalThreadRecord(
                id="thr-1",
                artifact_type="requirement",
                artifact_id="req-1",
                parent_ids=[],
                timestamp=datetime.utcnow(),
            ),
            DigitalThreadRecord(
                id="thr-2",
                artifact_type="calculation",
                artifact_id="calc-1",
                parent_ids=["req-1"],
                timestamp=datetime.utcnow(),
            ),
            DigitalThreadRecord(
                id="thr-3",
                artifact_type="design",
                artifact_id="design-1",
                parent_ids=["calc-1"],
                timestamp=datetime.utcnow(),
            ),
        ]
        evolution = {"design-1": ["v1", "v2", "v3"]}
        return DigitalThreadResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            digital_thread=thread,
            design_evolution_map=evolution,
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow(),
        )
