"""
MAVLink Service
"""
import uuid
import time
from typing import Dict, Any
from datetime import datetime


class MAVLinkService:
    def __init__(self):
        pass

    def send_command(self, conn_id: str, command: int, params: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        cmd_id = str(uuid.uuid4())
        return {
            "id": cmd_id,
            "connection_id": conn_id,
            "command": command,
            "status": "sent",
            "created_at": datetime.utcnow().isoformat(),
            "execution_time_ms": (time.time() - start_time) * 1000
        }

    def get_vehicle_status(self, conn_id: str) -> Dict[str, Any]:
        start_time = time.time()
        return {
            "connection_id": conn_id,
            "armed": False,
            "mode": "GUIDED",
            "battery": 12.6,
            "gps_fix": 3,
            "execution_time_ms": (time.time() - start_time) * 1000
        }
