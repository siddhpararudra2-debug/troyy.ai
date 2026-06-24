"""Change Request Manager - Change Management for Sprint 17."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


class ChangeRequestManager:
    """Manage engineering change requests."""

    def __init__(self):
        self.requests: Dict[str, Dict[str, Any]] = {}

    def create_request(
        self,
        project_id: str,
        title: str,
        description: Optional[str] = None,
        affected_artifacts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a new change request."""
        request_id = str(uuid.uuid4())
        request = {
            "id": request_id,
            "project_id": project_id,
            "title": title,
            "description": description,
            "affected_artifacts": affected_artifacts or [],
            "status": "draft",
            "created_at": datetime.utcnow().isoformat()
        }
        self.requests[request_id] = request
        return request

    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get a change request by ID."""
        return self.requests.get(request_id)

    def update_status(self, request_id: str, status: str) -> Optional[Dict[str, Any]]:
        """Update change request status."""
        if request_id in self.requests:
            self.requests[request_id]["status"] = status
            return self.requests[request_id]
        return None
