"""
Feedback Engine for Learning Module
Collects and processes feedback from design, simulation, manufacturing, etc.
"""
import logging
from typing import Dict, Any
from app.learning.experience_store import ExperienceStore

logger = logging.getLogger(__name__)


class FeedbackEngine:
    """
    Collects feedback from various sources and stores it in the experience store.
    """
    def __init__(self, experience_store: ExperienceStore = None):
        self.experience_store = experience_store or ExperienceStore()

    async def record_feedback(
        self,
        source: str,
        feedback: Dict[str, Any],
        project_id: str = None,
    ) -> Dict[str, Any]:
        """
        Record feedback from a source (design review, manufacturing, etc.).
        """
        return await self.experience_store.add_experience(
            experience_type=f"feedback:{source}",
            data=feedback,
            project_id=project_id,
        )

    async def record_simulation_outcome(
        self,
        simulation_type: str,
        outcome: Dict[str, Any],
        project_id: str = None,
    ) -> Dict[str, Any]:
        """
        Record the outcome of a simulation.
        """
        return await self.experience_store.add_experience(
            experience_type=f"simulation:{simulation_type}",
            data=outcome,
            project_id=project_id,
        )

    async def record_manufacturing_outcome(
        self,
        outcome: Dict[str, Any],
        project_id: str = None,
    ) -> Dict[str, Any]:
        """
        Record the outcome of a manufacturing process.
        """
        return await self.experience_store.add_experience(
            experience_type="manufacturing",
            data=outcome,
            project_id=project_id,
        )
