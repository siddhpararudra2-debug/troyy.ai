"""
Lesson Repository for Enterprise Knowledge Hub
Stores lessons learned.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class LessonRepository:
    """
    Repository for lessons learned from projects and operations.
    """

    def __init__(self):
        self._lessons: List[Dict[str, Any]] = []

    async def add_lesson(
        self,
        title: str,
        description: str,
        tags: List[str] = None,
        project_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        lesson = {
            "id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "tags": tags or [],
            "project_id": project_id,
            "tenant_id": tenant_id,
            "created_at": datetime.utcnow().isoformat(),
        }
        self._lessons.append(lesson)
        return lesson

    async def get_lessons(
        self,
        project_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        filtered = self._lessons
        if project_id:
            filtered = [l for l in filtered if l["project_id"] == project_id]
        if tenant_id:
            filtered = [l for l in filtered if l["tenant_id"] == tenant_id]
        return filtered
