"""
Drawing Generation Service
"""
import uuid
import time
from datetime import datetime
from app.cad.schemas.schemas import CADDrawingRequest, CADDrawingResponse


class DrawingGenerationService:
    @staticmethod
    def generate(request: CADDrawingRequest) -> CADDrawingResponse:
        start_time = time.time()
        views = [
            {"type": "front", "scale": 1.0, "position": [0, 0]},
            {"type": "top", "scale": 1.0, "position": [100, 0]},
            {"type": "right", "scale": 1.0, "position": [0, 100]},
        ]
        dimensions = [
            {"name": "Overall Width", "value": 50, "type": "linear"},
            {"name": "Hole Diameter", "value": 5, "type": "diameter"},
        ]
        notes = ["Material: Aluminum 6061", "Finish: Anodized"]
        return CADDrawingResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            drawing_name="Drawing_v1",
            views=views,
            dimensions=dimensions,
            notes=notes,
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow(),
        )
