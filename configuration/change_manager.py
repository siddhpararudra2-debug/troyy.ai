"""Change Manager - Configuration Management for Sprint 17."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


class ChangeManager:
    """Manage changes to configurations."""

    def __init__(self):
        self.changes: Dict[str, Dict[str, Any]] = {}

    def create_change(
        self,
        project_id: str,
        title: str,
        description: Optional[str] = None,
        affected_artifacts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a new change request."""
        change_id = str(uuid.uuid4())
        change = {
            "id": change_id,
            "project_id": project_id,
            "title": title,
            "description": description,
            "affected_artifacts": affected_artifacts or [],
            "status": "draft",
            "created_at": datetime.utcnow().isoformat()
        }
        self.changes[change_id] = change
        return change

    def update_change_status(self, change_id: str, status: str) -> Optional[Dict[str, Any]]:
        """Update change status (draft -> in_review -> approved -> implemented)."""
        if change_id in self.changes:
            self.changes[change_id]["status"] = status
            return self.changes[change_id]
        return None

    def get_change(self, change_id: str) -> Optional[Dict[str, Any]]:
        """Get a change by ID."""
        return self.changes.get(change_id)
