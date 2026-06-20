"""
Engineering Memory Service
"""
import uuid
import time
from datetime import datetime
from app.knowledge.schemas.schemas import (
    EngineeringMemoryRequest,
    EngineeringMemoryResponse
)


class EngineeringMemoryService:
    @staticmethod
    def store(request: EngineeringMemoryRequest) -> EngineeringMemoryResponse:
        return EngineeringMemoryResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            memory_type=request.memory_type,
            title=request.title,
            content=request.content,
            tags=request.tags,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    @staticmethod
    def retrieve(project_id: str, memory_type: str = None):
        return []
