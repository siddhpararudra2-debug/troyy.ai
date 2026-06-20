"""
Regulatory Intelligence Service
"""
import uuid
from datetime import datetime
from app.compliance.schemas.schemas import (
    RegulationRequest,
    RegulationResponse
)


class RegulationsService:
    @staticmethod
    def create_regulation(request: RegulationRequest) -> RegulationResponse:
        return RegulationResponse(
            id=str(uuid.uuid4()),
            regulation_type=request.regulation_type,
            name=request.name,
            jurisdiction=request.jurisdiction,
            description=request.description,
            created_at=datetime.utcnow()
        )

    @staticmethod
    def get_applicable_regulations(project_id: str, domain: str, jurisdiction: str) -> list:
        return [
            RegulationResponse(
                id=str(uuid.uuid4()),
                regulation_type="Aviation",
                name="14 CFR Part 107",
                jurisdiction="USA",
                description="Small Unmanned Aircraft Systems (sUAS) Operations",
                created_at=datetime.utcnow()
            )
        ]
