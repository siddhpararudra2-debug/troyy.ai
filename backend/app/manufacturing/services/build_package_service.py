"""
Build Package Generation Service
"""
import uuid
import time
from datetime import datetime
from app.manufacturing.schemas.schemas import (
    BuildPackageRequest,
    BuildPackageResponse
)


class BuildPackageService:
    @staticmethod
    def generate(request: BuildPackageRequest) -> BuildPackageResponse:
        start_time = time.time()
        return BuildPackageResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            cad_files=["frame.step", "bracket.step"],
            drawings=["frame.dxf"],
            bom="bom.csv",
            assembly_instructions="assembly.md",
            manufacturing_plans="manufacturing.pdf",
            testing_plans="testing.pdf",
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
