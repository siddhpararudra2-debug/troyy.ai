"""Revision Controller - Configuration Management for Sprint 17."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


class RevisionController:
    """Control and track revisions to all engineering artifacts."""

    def __init__(self):
        self.revisions: Dict[str, List[Dict[str, Any]]] = {}

    def create_revision(
        self,
        artifact_id: str,
        artifact_type: str,
        version: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new revision for an artifact."""
        revision = {
            "id": str(uuid.uuid4()),
            "artifact_id": artifact_id,
            "artifact_type": artifact_type,
            "version": version,
            "description": description,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat()
        }
        if artifact_id not in self.revisions:
            self.revisions[artifact_id] = []
        self.revisions[artifact_id].append(revision)
        return revision

    def get_revision_history(self, artifact_id: str) -> List[Dict[str, Any]]:
        """Get revision history for an artifact."""
        return self.revisions.get(artifact_id, [])

    def get_latest_revision(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """Get latest revision for an artifact."""
        history = self.get_revision_history(artifact_id)
        return history[-1] if history else None
