"""
Tenant Manager Service
"""
import uuid
import time
from typing import Dict, Any, List
from datetime import datetime


class TenantManager:
    def __init__(self):
        self.tenants: Dict[str, Dict[str, Any]] = {}

    def create_tenant(self, tenant_data: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        tenant_id = str(uuid.uuid4())
        tenant = {
            "id": tenant_id,
            **tenant_data,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "execution_time_ms": (time.time() - start_time) * 1000
        }
        self.tenants[tenant_id] = tenant
        return tenant

    def get_tenant(self, tenant_id: str) -> Dict[str, Any]:
        start_time = time.time()
        return self.tenants.get(tenant_id, {})

    def list_tenants(self) -> List[Dict[str, Any]]:
        start_time = time.time()
        return list(self.tenants.values())
