"""
Lesson Extractor for Learning Module
Extracts useful lessons and best practices from stored experiences.
"""
import logging
from typing import Dict, Any, List
from app.learning.experience_store import ExperienceStore

logger = logging.getLogger(__name__)


class LessonExtractor:
    """
    Extracts lessons learned and best practices from stored experiences.
    """
    def __init__(self, experience_store: ExperienceStore = None):
        self.experience_store = experience_store or ExperienceStore()

    async def extract_lessons(
        self,
        project_id: str = None,
        experience_type: str = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract lessons from stored experiences.
        """
        experiences = await self.experience_store.get_experiences(
            experience_type=experience_type,
            project_id=project_id,
        )

        lessons = []
        for exp in experiences:
            lesson = self._extract_single_lesson(exp)
            if lesson:
                lessons.append(lesson)

        return lessons

    def _extract_single_lesson(self, experience: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract a single lesson from one experience (simplified for now).
        """
        data = experience.get("data", {})
        if "success" in data:
            if data["success"]:
                return {
                    "lesson": "Successful approach",
                    "details": f"Technique worked: {data.get('details', '')}",
                    "experience_id": experience["id"],
                }
            else:
                return {
                    "lesson": "What not to do",
                    "details": f"Failed: {data.get('error', '')}",
                    "experience_id": experience["id"],
                }
        return {}
