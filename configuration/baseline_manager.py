"""Baseline Manager - Configuration Management for Sprint 17."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


class BaselineManager:
    """Manage engineering design baselines."""

    def __init__(self):
        self.baselines: Dict[str, Dict[str, Any]] = {}

    def create_baseline(
        self,
        project_id: str,
        name: str,
        description: Optional[str] = None,
        artifacts: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new configuration baseline."""
        baseline_id = str(uuid.uuid4())
        baseline = {
            "id": baseline_id,
            "project_id": project_id,
            "name": name,
            "description": description,
            "artifacts": artifacts or [],
            "metadata": metadata or {},
            "status": "draft",
            "created_at": datetime.utcnow().isoformat()
        }
        self.baselines[baseline_id] = baseline
        return baseline

    def get_baseline(self, baseline_id: str) -> Optional[Dict[str, Any]]:
        """Get a baseline by ID."""
        return self.baselines.get(baseline_id)

    def list_baselines(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all baselines, optionally filtered by project."""
        baselines = list(self.baselines.values())
        if project_id:
            baselines = [b for b in baselines if b["project_id"] == project_id]
        return baselines

    def approve_baseline(self, baseline_id: str) -> Optional[Dict[str, Any]]:
        """Approve a baseline."""
        if baseline_id in self.baselines:
            self.baselines[baseline_id]["status"] = "approved"
            return self.baselines[baseline_id]
        return None

    def archive_baseline(self, baseline_id: str) -> Optional[Dict[str, Any]]:
        """Archive a baseline."""
        if baseline_id in self.baselines:
            self.baselines[baseline_id]["status"] = "archived"
            return self.baselines[baseline_id]
        return None
