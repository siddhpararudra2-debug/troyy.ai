"""
Experience Store for Learning Module
Stores past design, simulation, and manufacturing outcomes.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ExperienceStore:
    """
    Stores experiences (design outcomes, simulation results, manufacturing data) for learning.
    """
    def __init__(self):
        self._experiences: List[Dict[str, Any]] = []

    async def add_experience(
        self,
        experience_type: str,
        data: Dict[str, Any],
        project_id: str = None,
    ) -> Dict[str, Any]:
        """
        Add a new experience to the store.
        """
        experience = {
            "id": str(uuid.uuid4()),
            "type": experience_type,
            "project_id": project_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._experiences.append(experience)
        logger.info(f"Added {experience_type} experience: {experience['id']}")
        return experience

    async def get_experiences(
        self,
        experience_type: str = None,
        project_id: str = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve experiences from the store, optionally filtered.
        """
        filtered = self._experiences
        if experience_type:
            filtered = [e for e in filtered if e["type"] == experience_type]
        if project_id:
            filtered = [e for e in filtered if e["project_id"] == project_id]
        return filtered[-limit:]  # Return most recent first
