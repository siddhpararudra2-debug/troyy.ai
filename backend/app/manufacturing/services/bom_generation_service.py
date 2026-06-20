"""
BOM Generation Service
"""
import uuid
import time
from datetime import datetime
from app.manufacturing.schemas.schemas import (
    BOMRequest,
    BOMResponse,
    BOMItem
)


class BOMGenerationService:
    @staticmethod
    def generate(request: BOMRequest) -> BOMResponse:
        start_time = time.time()
        items = [
            BOMItem(part_number="MECH-001", name="Frame", quantity=1, material="Aluminum 6061"),
            BOMItem(part_number="ELEC-001", name="Flight Controller", quantity=1, material="PCB"),
            BOMItem(part_number="FAST-001", name="M3 Bolt", quantity=24, material="Steel")
        ]
        return BOMResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            items=items,
            total_items=len(items),
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
