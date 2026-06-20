"""
CAD Generation Service
"""
import uuid
import time
from datetime import datetime
from app.cad.schemas.schemas import CADPartRequest, CADPartResponse


class CADGenerationService:
    @staticmethod
    def generate_part(request: CADPartRequest) -> CADPartResponse:
        start_time = time.time()
        features = [
            {"type": "sketch", "name": "Base Sketch"},
            {"type": "extrusion", "name": "Body", "distance": 10},
            {"type": "hole", "name": "Mount Hole"},
        ]
        constraints = [
            {"type": "coincident", "entities": ["Line1", "Line2"]},
            {"type": "dimension", "value": 50, "name": "Width"},
        ]
        parametric_dimensions = {"width": 50, "height": 30, "depth": 10}
        return CADPartResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            part_name=f"{request.part_type}_v1",
            features=features,
            constraints=constraints,
            parametric_dimensions=parametric_dimensions,
            export_formats=["step", "stl", "iges"],
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow(),
        )
