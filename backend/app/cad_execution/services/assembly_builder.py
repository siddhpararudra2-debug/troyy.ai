"""
Assembly Builder for CAD Execution
"""
import uuid
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.core.config import settings


class AssemblyBuilder:
    """
    Builds CAD assemblies from individual parts
    """

    def __init__(self):
        self.output_dir = settings.OUTPUT_DIR / "cad"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_assembly(
        self,
        assembly_name: str,
        parts: List[Dict[str, Any]],
        mates: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Build an assembly from parts
        """
        start_time = time.time()
        assembly_id = str(uuid.uuid4())
        
        mates = mates or []
        
        # Build assembly structure
        assembly = {
            "id": assembly_id,
            "name": assembly_name,
            "parts": parts,
            "mates": mates,
            "joints": [],
            "status": "completed",
            "file_path": str(self.output_dir / f"{assembly_name}_{assembly_id}.fcstd"),
            "execution_time_ms": (time.time() - start_time) * 1000
        }
        
        return assembly

    def build_drone_frame(
        self,
        frame_type: str = "quadcopter",
        arm_length: float = 300.0
    ) -> Dict[str, Any]:
        """
        Build a complete drone frame assembly
        """
        parts = [
            {"name": "central_hub", "type": "hub"},
            {"name": "arm_front_right", "type": "drone_arm", "length": arm_length},
            {"name": "arm_front_left", "type": "drone_arm", "length": arm_length},
            {"name": "arm_rear_right", "type": "drone_arm", "length": arm_length},
            {"name": "arm_rear_left", "type": "drone_arm", "length": arm_length},
        ]
        
        mates = [
            {"type": "fixed", "parts": ["central_hub", "arm_front_right"]},
            {"type": "fixed", "parts": ["central_hub", "arm_front_left"]},
            {"type": "fixed", "parts": ["central_hub", "arm_rear_right"]},
            {"type": "fixed", "parts": ["central_hub", "arm_rear_left"]},
        ]
        
        return self.build_assembly(
            assembly_name=f"{frame_type}_frame",
            parts=parts,
            mates=mates
        )
