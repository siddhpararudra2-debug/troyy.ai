"""
CANBus Service
"""
import uuid
import time
from typing import Dict, Any
from datetime import datetime


class CANBusService:
    def __init__(self):
        pass

    def send_can_message(self, bus_id: str, msg_id: int, data: bytes) -> Dict[str, Any]:
        start_time = time.time()
        tx_id = str(uuid.uuid4())
        return {
            "id": tx_id,
            "bus_id": bus_id,
            "message_id": msg_id,
            "status": "sent",
            "created_at": datetime.utcnow().isoformat(),
            "execution_time_ms": (time.time() - start_time) * 1000
        }

    def receive_can_messages(self, bus_id: str, limit: int = 10) -> Dict[str, Any]:
        start_time = time.time()
        return {
            "bus_id": bus_id,
            "messages": [{"id": 0x123, "data": [0x01, 0x02]}],
            "execution_time_ms": (time.time() - start_time) * 1000
        }
