"""
PCB Component Placement Service
"""
import uuid
import time
from datetime import datetime
from app.pcb.schemas.schemas import (
    PCBPlacementRequest,
    PCBPlacementResponse,
    PlacedComponent,
)
from app.electronics_intelligence.services.component_library import get_predefined_components


class PlacementService:
    @staticmethod
    def generate(request: PCBPlacementRequest) -> PCBPlacementResponse:
        start_time = time.time()
        components = get_predefined_components()

        placed = []
        grid_x = 20
        grid_y = 20
        spacing = 25

        for i, comp in enumerate(components[:8]):  # limit to first 8 components for demo
            x = grid_x + (i % 3) * spacing
            y = grid_y + (i // 3) * spacing
            placed.append(PlacedComponent(
                component_id=comp["id"],
                part_number=comp["part_number"],
                x_mm=x,
                y_mm=y,
                rotation_deg=0,
                side="top",
                priority=1
            ))

        return PCBPlacementResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            components=placed,
            placement_regions=[],
            optimization_score=0.85,
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow(),
        )
