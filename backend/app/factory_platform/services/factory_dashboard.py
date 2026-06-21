"""
Factory Dashboard
"""
import time
from typing import Dict, Any
from datetime import datetime


class FactoryDashboard:
    def __init__(self):
        pass

    def get_dashboard_data(self) -> Dict[str, Any]:
        start_time = time.time()
        return {
            "active_work_orders": 5,
            "production_today": 500,
            "yield_rate": 0.97,
            "oee_avg": 0.84,
            "machines_online": 10,
            "last_updated": datetime.utcnow().isoformat(),
            "execution_time_ms": (time.time() - start_time) * 1000
        }
