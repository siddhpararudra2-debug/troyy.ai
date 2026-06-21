"""
Geometry Builder for CAD Execution
"""
import uuid
import time
from typing import Dict, Any, List, Optional
from app.core.config import settings


class GeometryBuilder:
    """
    Builds parametric geometry using various engines
    """

    @staticmethod
    def build_box(
        length: float = 50.0,
        width: float = 30.0,
        height: float = 10.0,
        origin: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Build a simple box geometry
        """
        origin = origin or [0, 0, 0]
        return {
            "type": "box",
            "parameters": {
                "length": length,
                "width": width,
                "height": height,
                "origin": origin
            },
            "volume": length * width * height,
            "surface_area": 2 * (length*width + length*height + width*height)
        }

    @staticmethod
    def build_cylinder(
        radius: float = 10.0,
        height: float = 50.0,
        origin: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Build a cylinder geometry
        """
        import math
        origin = origin or [0, 0, 0]
        return {
            "type": "cylinder",
            "parameters": {
                "radius": radius,
                "height": height,
                "origin": origin
            },
            "volume": math.pi * radius**2 * height,
            "surface_area": 2 * math.pi * radius * (radius + height)
        }

    @staticmethod
    def build_bracket(
        width: float = 50.0,
        height: float = 30.0,
        depth: float = 10.0,
        hole_radius: float = 2.5,
        hole_spacing: float = 30.0
    ) -> Dict[str, Any]:
        """
        Build a bracket geometry (common drone part)
        """
        return {
            "type": "bracket",
            "parameters": {
                "width": width,
                "height": height,
                "depth": depth,
                "hole_radius": hole_radius,
                "hole_spacing": hole_spacing
            },
            "features": [
                {"type": "base_plate", "dimensions": [width, depth, 5]},
                {"type": "vertical_plate", "dimensions": [width, height - 5, depth]},
                {"type": "mount_holes", "count": 2, "radius": hole_radius}
            ]
        }

    @staticmethod
    def build_drone_arm(
        length: float = 300.0,
        width: float = 20.0,
        height: float = 15.0,
        wall_thickness: float = 2.0
    ) -> Dict[str, Any]:
        """
        Build a drone arm geometry
        """
        return {
            "type": "drone_arm",
            "parameters": {
                "length": length,
                "width": width,
                "height": height,
                "wall_thickness": wall_thickness
            },
            "features": [
                {"type": "main_beam", "profile": "rectangular_tube"},
                {"type": "motor_mount", "position": "end"},
                {"type": "frame_mount", "position": "base"}
            ]
        }

    @staticmethod
    def build_from_requirements(requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build geometry from engineering requirements
        """
        part_type = requirements.get("part_type", "bracket")
        
        if part_type == "bracket":
            return GeometryBuilder.build_bracket(
                width=requirements.get("width", 50.0),
                height=requirements.get("height", 30.0),
                depth=requirements.get("depth", 10.0)
            )
        elif part_type == "drone_arm":
            return GeometryBuilder.build_drone_arm(
                length=requirements.get("length", 300.0),
                width=requirements.get("width", 20.0),
                height=requirements.get("height", 15.0)
            )
        elif part_type == "box":
            return GeometryBuilder.build_box(
                length=requirements.get("length", 50.0),
                width=requirements.get("width", 30.0),
                height=requirements.get("height", 10.0)
            )
        else:
            # Default to box
            return GeometryBuilder.build_box()
