"""Release Manager - Configuration Management for Sprint 17."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


class ReleaseManager:
    """Manage releases of engineering configurations."""

    def __init__(self):
        self.releases: Dict[str, Dict[str, Any]] = {}

    def create_release(
        self,
        project_id: str,
        name: str,
        version: str,
        artifacts: Optional[List[str]] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new release."""
        release_id = str(uuid.uuid4())
        release = {
            "id": release_id,
            "project_id": project_id,
            "name": name,
            "version": version,
            "artifacts": artifacts or [],
            "description": description,
            "metadata": metadata or {},
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        self.releases[release_id] = release
        return release

    def approve_release(self, release_id: str) -> Optional[Dict[str, Any]]:
        """Approve and finalize a release."""
        if release_id in self.releases:
            self.releases[release_id]["status"] = "released"
            return self.releases[release_id]
        return None

    def list_releases(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all releases, optionally filtered by project."""
        releases = list(self.releases.values())
        if project_id:
            releases = [r for r in releases if r["project_id"] == project_id]
        return releases
