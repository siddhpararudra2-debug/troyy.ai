"""
Standards Intelligence Service
"""
import uuid
from datetime import datetime
from app.compliance.schemas.schemas import (
    StandardRequest,
    StandardResponse
)


class StandardsService:
    @staticmethod
    def create_standard(request: StandardRequest) -> StandardResponse:
        return StandardResponse(
            id=str(uuid.uuid4()),
            standard_type=request.standard_type,
            name=request.name,
            code=request.code,
            description=request.description,
            requirements_json="{}",
            created_at=datetime.utcnow()
        )

    @staticmethod
    def get_applicable_standards(project_id: str, domain: str) -> list:
        # Mock response
        return [
            StandardResponse(
                id=str(uuid.uuid4()),
                standard_type="ISO",
                name="ISO 12100:2010",
                code="ISO 12100:2010",
                description="Safety of machinery — General principles for design — Risk assessment and risk reduction",
                created_at=datetime.utcnow()
            )
        ]
