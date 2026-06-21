"""
Subscription Service
"""
import uuid
import time
from typing import Dict, Any
from datetime import datetime, timedelta


class SubscriptionService:
    def __init__(self):
        pass

    def create_subscription(self, tenant_id: str, plan: str = "enterprise") -> Dict[str, Any]:
        start_time = time.time()
        subscription_id = str(uuid.uuid4())
        return {
            "id": subscription_id,
            "tenant_id": tenant_id,
            "plan": plan,
            "status": "active",
            "start_date": datetime.utcnow().isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=365)).isoformat(),
            "execution_time_ms": (time.time() - start_time) * 1000
        }

    def update_subscription(self, subscription_id: str, plan: str) -> Dict[str, Any]:
        start_time = time.time()
        return {
            "id": subscription_id,
            "plan": plan,
            "status": "updated",
            "execution_time_ms": (time.time() - start_time) * 1000
        }
