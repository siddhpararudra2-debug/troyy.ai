"""
Milestone Tracker for Program Management Module
Tracks project milestones.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class MilestoneTracker:
    """
    Tracks milestones and progress.
    """

    def __init__(self):
        self._milestones: Dict[str, List[Dict]] = {}  # project_id → list of milestones

    async def add_milestone(
        self,
        project_id: str,
        name: str,
        due_date: datetime,
        description: str = "",
    ) -> Dict:
        milestone_id = str(uuid.uuid4())
        milestone = {
            "milestone_id": milestone_id,
            "name": name,
            "description": description,
            "due_date": due_date.isoformat(),
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }
        if project_id not in self._milestones:
            self._milestones[project_id] = []
        self._milestones[project_id].append(milestone)
        logger.info(f"Added milestone {name} to project {project_id}")
        return milestone

    async def get_milestones(self, project_id: str) -> List[Dict]:
        return self._milestones.get(project_id, [])
