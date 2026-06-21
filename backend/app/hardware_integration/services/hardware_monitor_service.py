"""
Hardware Monitor Service
"""
import time
from typing import Dict, Any
from datetime import datetime


class HardwareMonitorService:
    def __init__(self):
        pass

    def get_hardware_health(self, device_id: str) -> Dict[str, Any]:
        start_time = time.time()
        return {
            "device_id": device_id,
            "health": "good",
            "temperature": 45.0,
            "voltage": 12.4,
            "uptime": 3600,
            "last_updated": datetime.utcnow().isoformat(),
            "execution_time_ms": (time.time() - start_time) * 1000
        }

    def get_alert_history(self, device_id: str) -> Dict[str, Any]:
        start_time = time.time()
        return {
            "device_id": device_id,
            "alerts": [{"type": "warning", "message": "Temperature rising", "time": datetime.utcnow().isoformat()}],
            "execution_time_ms": (time.time() - start_time) * 1000
        }
