"""Lessons Learned Manager - Knowledge Base for Sprint 17."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


class LessonsLearnedManager:
    """Manage lessons learned knowledge base."""

    def __init__(self):
        self.lessons: Dict[str, Dict[str, Any]] = {}

    def add_lesson(
        self,
        project_id: str,
        title: str,
        lesson: str,
        tags: Optional[List[str]] = None,
        impact: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a lesson learned."""
        lesson_id = str(uuid.uuid4())
        lesson_record = {
            "id": lesson_id,
            "project_id": project_id,
            "title": title,
            "lesson": lesson,
            "tags": tags or [],
            "impact": impact,
            "created_at": datetime.utcnow().isoformat()
        }
        self.lessons[lesson_id] = lesson_record
        return lesson_record

    def search_lessons(
        self,
        query: str,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Search lessons learned."""
        results = list(self.lessons.values())
        if query:
            query_lower = query.lower()
            results = [
                l for l in results
                if query_lower in l["title"].lower() or query_lower in l["lesson"].lower()
            ]
        if tags:
            results = [l for l in results if any(t in l["tags"] for t in tags)]
        return results
