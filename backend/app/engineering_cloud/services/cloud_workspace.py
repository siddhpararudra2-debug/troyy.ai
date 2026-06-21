"""
Cloud Workspace Service
"""
import uuid
import time
from typing import Dict, Any, List
from datetime import datetime


class CloudWorkspace:
    def __init__(self):
        pass

    def create_workspace(self, tenant_id: str, workspace_name: str) -> Dict[str, Any]:
        start_time = time.time()
        workspace_id = str(uuid.uuid4())
        return {
            "id": workspace_id,
            "tenant_id": tenant_id,
            "name": workspace_name,
            "status": "ready",
            "created_at": datetime.utcnow().isoformat(),
            "execution_time_ms": (time.time() - start_time) * 1000
        }

    def list_workspaces(self, tenant_id: str) -> List[Dict[str, Any]]:
        start_time = time.time()
        return [
            {
                "id": str(uuid.uuid4()),
                "name": "Main Workspace",
                "status": "active",
                "execution_time_ms": (time.time() - start_time) * 1000
            }
        ]
