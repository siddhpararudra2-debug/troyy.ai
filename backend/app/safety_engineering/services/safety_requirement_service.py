"""
Safety Requirement Service
"""
import uuid
import time
from typing import Dict, Any, List
from datetime import datetime


class SafetyRequirementService:
    def __init__(self):
        pass

    def create_safety_requirement(self, text: str, sil_level: int = 2) -> Dict[str, Any]:
        start_time = time.time()
        sreq_id = str(uuid.uuid4())
        return {
            "id": sreq_id,
            "text": text,
            "sil_level": sil_level,
            "status": "proposed",
            "created_at": datetime.utcnow().isoformat(),
            "execution_time_ms": (time.time() - start_time) * 1000
        }

    def list_safety_requirements(self) -> List[Dict[str, Any]]:
        start_time = time.time()
        return [
            {
                "id": str(uuid.uuid4()),
                "text": "System shall shut down on overvoltage > 15V",
                "sil_level": 3,
                "execution_time_ms": (time.time() - start_time) * 1000
            }
        ]
