"""
Partner Portal Service
"""
import uuid
import time
from typing import Dict, Any, List
from datetime import datetime


class PartnerPortal:
    def __init__(self):
        pass

    def register_partner(self, partner_data: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        partner_id = str(uuid.uuid4())
        return {
            "id": partner_id,
            **partner_data,
            "registered_at": datetime.utcnow().isoformat(),
            "status": "active",
            "execution_time_ms": (time.time() - start_time) * 1000
        }

    def list_partners(self) -> List[Dict[str, Any]]:
        start_time = time.time()
        return [
            {
                "id": str(uuid.uuid4()),
                "name": "TechCorp Inc.",
                "plugins_count": 5,
                "revenue": 12500.00,
                "rating": 4.8,
                "execution_time_ms": (time.time() - start_time) * 1000
            }
        ]
