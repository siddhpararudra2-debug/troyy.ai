"""
PCB Stackup Service
"""
import uuid
import time
from datetime import datetime
from app.pcb.schemas.schemas import (
    PCBStackupRequest,
    PCBStackupResponse,
    StackupLayer,
)


class StackupService:
    @staticmethod
    def generate(request: PCBStackupRequest) -> PCBStackupResponse:
        start_time = time.time()
        layer_count = request.layer_count

        if layer_count == 2:
            layers = [
                StackupLayer(name="Top Layer", layer_type="signal", copper_weight_oz=1.0),
                StackupLayer(name="Dielectric", layer_type="dielectric", material="FR4", thickness_mm=1.5),
                StackupLayer(name="Bottom Layer", layer_type="signal", copper_weight_oz=1.0),
            ]
        elif layer_count == 4:
            layers = [
                StackupLayer(name="Top Layer", layer_type="signal", copper_weight_oz=1.0),
                StackupLayer(name="Dielectric 1-2", layer_type="dielectric", material="FR4", thickness_mm=0.2),
                StackupLayer(name="Ground Plane", layer_type="ground", copper_weight_oz=1.5),
                StackupLayer(name="Dielectric 2-3", layer_type="dielectric", material="FR4", thickness_mm=1.0),
                StackupLayer(name="Power Plane", layer_type="power", copper_weight_oz=1.5),
                StackupLayer(name="Dielectric 3-4", layer_type="dielectric", material="FR4", thickness_mm=0.2),
                StackupLayer(name="Bottom Layer", layer_type="signal", copper_weight_oz=1.0),
            ]
        elif layer_count == 6:
            layers = [
                StackupLayer(name="Top Layer", layer_type="signal", copper_weight_oz=1.0),
                StackupLayer(name="Dielectric 1-2", layer_type="dielectric", material="FR4", thickness_mm=0.15),
                StackupLayer(name="Ground Plane 1", layer_type="ground", copper_weight_oz=1.5),
                StackupLayer(name="Dielectric 2-3", layer_type="dielectric", material="FR4", thickness_mm=0.2),
                StackupLayer(name="Signal Layer 2", layer_type="signal", copper_weight_oz=1.0),
                StackupLayer(name="Dielectric 3-4", layer_type="dielectric", material="FR4", thickness_mm=0.5),
                StackupLayer(name="Signal Layer 3", layer_type="signal", copper_weight_oz=1.0),
                StackupLayer(name="Dielectric 4-5", layer_type="dielectric", material="FR4", thickness_mm=0.2),
                StackupLayer(name="Power Plane", layer_type="power", copper_weight_oz=1.5),
                StackupLayer(name="Dielectric 5-6", layer_type="dielectric", material="FR4", thickness_mm=0.15),
                StackupLayer(name="Bottom Layer", layer_type="signal", copper_weight_oz=1.0),
            ]
        else:
            layers = []  # default, handle more layers later

        return PCBStackupResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            layer_count=layer_count,
            layers=layers,
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow(),
        )
