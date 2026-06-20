"""
Lessons Learned Service
"""
import uuid
import time
from datetime import datetime
from app.knowledge.schemas.schemas import (
    LessonLearnedRequest,
    LessonLearnedResponse
)


class LessonsLearnedService:
    @staticmethod
    def record(request: LessonLearnedRequest) -> LessonLearnedResponse:
        return LessonLearnedResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            title=request.title,
            description=request.description,
            impact=request.impact,
            tags=request.tags,
            created_at=datetime.utcnow()
        )

    @staticmethod
    def query(tags: list = None):
        return []
