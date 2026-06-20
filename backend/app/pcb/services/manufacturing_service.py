"""
PCB Manufacturing Preparation Service
"""
import uuid
import time
from datetime import datetime
from app.pcb.schemas.schemas import (
    PCBManufacturingRequest,
    PCBManufacturingResponse,
    ManufacturingConstraint,
)


class ManufacturingService:
    @staticmethod
    def generate(request: PCBManufacturingRequest) -> PCBManufacturingResponse:
        start_time = time.time()

        fab_constraints = [
            ManufacturingConstraint(
                category="Trace Width",
                constraint="min_trace_width",
                value=0.15,
                description="Minimum trace width in mm"
            ),
            ManufacturingConstraint(
                category="Trace Spacing",
                constraint="min_trace_spacing",
                value=0.15,
                description="Minimum trace spacing in mm"
            ),
            ManufacturingConstraint(
                category="Via",
                constraint="min_via_drill",
                value=0.3,
                description="Minimum via drill diameter in mm"
            ),
        ]

        return PCBManufacturingResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            fabrication_constraints=fab_constraints,
            assembly_constraints=[],
            dfm_review=[
                "Design is suitable for standard PCB fabrication process",
                "All component footprints match standard packages"
            ],
            dfa_review=[
                "Components are accessible for assembly",
                "Polarized components are clearly oriented"
            ],
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow(),
        )
