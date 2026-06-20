"""
Assembly Generation Service
"""
import uuid
import time
from datetime import datetime
from app.cad.schemas.schemas import CADAassemblyRequest, CADAassemblyResponse


class AssemblyGenerationService:
    @staticmethod
    def generate(request: CADAassemblyRequest) -> CADAassemblyResponse:
        start_time = time.time()
        parts = [
            {"id": "part-1", "name": "Base", "position": [0, 0, 0], "rotation": [0, 0, 0]},
            {"id": "part-2", "name": "Top Plate", "position": [0, 0, 10], "rotation": [0, 0, 0]},
        ]
        mates = [
            {"type": "coincident", "from": "part-1.Face1", "to": "part-2.Face2"},
        ]
        joints = [
            {"type": "fixed", "part": "part-1"},
        ]
        return CADAassemblyResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            assembly_name="Assembly_v1",
            parts=parts,
            mates=mates,
            joints=joints,
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow(),
        )
