"""
Work Order Service
"""
import uuid
import time
from typing import Dict, Any, List
from datetime import datetime


class WorkOrderService:
    def __init__(self):
        pass

    def create_work_order(self, product_id: str, qty: int, due_date: str) -> Dict[str, Any]:
        start_time = time.time()
        wo_id = str(uuid.uuid4())
        return {
            "id": wo_id,
            "product_id": product_id,
            "quantity": qty,
            "due_date": due_date,
            "status": "open",
            "created_at": datetime.utcnow().isoformat(),
            "execution_time_ms": (time.time() - start_time) * 1000
        }

    def list_work_orders(self, status: str = None) -> List[Dict[str, Any]]:
        start_time = time.time()
        return [
            {
                "id": str(uuid.uuid4()),
                "product_id": "P123",
                "quantity": 100,
                "status": "in_progress",
                "execution_time_ms": (time.time() - start_time) * 1000
            }
        ]
