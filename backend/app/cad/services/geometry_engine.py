"""
Geometry Engine - Core geometric operations
Handles sketch generation, solid modeling, surface modeling
"""
from typing import Dict, Any, List, Optional, Tuple
import math
import logging

logger = logging.getLogger(__name__)


class GeometryEngine:
    """Core geometry engine for CAD operations."""
    
    def __init__(self):
        self.sketches = {}
        self.solids = {}
        self.surfaces = {}
    
    def create_sketch(
        self, 
        plane: str = "XY", 
        origin: Tuple[float, float, float] = (0, 0, 0)
    ) -> Dict[str, Any]:
        """Create a 2D sketch on specified plane."""
        sketch_id = f"sketch_{len(self.sketches) + 1}"
        sketch = {
            "id": sketch_id,
            "plane": plane,
            "origin": origin,
            "entities": [],
            "constraints": [],
        }
        self.sketches[sketch_id] = sketch
        return sketch
    
    def add_line(
        self, 
        sketch: Dict[str, Any], 
        start: Tuple[float, float], 
        end: Tuple[float, float]
    ) -> Dict[str, Any]:
        """Add a line to sketch."""
        line = {
            "type": "line",
            "start": start,
            "end": end,
        }
        sketch["entities"].append(line)
        return sketch
    
    def add_circle(
        self, 
        sketch: Dict[str, Any], 
        center: Tuple[float, float], 
        radius: float
    ) -> Dict[str, Any]:
        """Add a circle to sketch."""
        circle = {
            "type": "circle",
            "center": center,
            "radius": radius,
        }
        sketch["entities"].append(circle)
        return sketch
    
    def add_rectangle(
        self, 
        sketch: Dict[str, Any], 
        center: Tuple[float, float], 
        width: float, 
        height: float
    ) -> Dict[str, Any]:
        """Add a rectangle to sketch."""
        half_w = width / 2
        half_h = height / 2
        rectangle = {
            "type": "rectangle",
            "center": center,
            "width": width,
            "height": height,
            "vertices": [
                (center[0] - half_w, center[1] - half_h),
                (center[0] + half_w, center[1] - half_h),
                (center[0] + half_w, center[1] + half_h),
                (center[0] - half_w, center[1] + half_h),
            ],
        }
        sketch["entities"].append(rectangle)
        return sketch
    
    def extrude(
        self, 
        sketch: Dict[str, Any], 
        distance: float, 
        direction: Optional[Tuple[float, float, float]] = None
    ) -> Dict[str, Any]:
        """Extrude a sketch into a solid."""
        solid_id = f"solid_{len(self.solids) + 1}"
        solid = {
            "id": solid_id,
            "type": "extrude",
            "sketch": sketch,
            "distance": distance,
            "direction": direction or (0, 0, 1),
        }
        self.solids[solid_id] = solid
        return solid
    
    def revolve(
        self, 
        sketch: Dict[str, Any], 
        axis: Tuple[float, float, float], 
        angle: float = 360.0
    ) -> Dict[str, Any]:
        """Revolve a sketch around an axis."""
        solid_id = f"solid_{len(self.solids) + 1}"
        solid = {
            "id": solid_id,
            "type": "revolve",
            "sketch": sketch,
            "axis": axis,
            "angle": angle,
        }
        self.solids[solid_id] = solid
        return solid
    
    def loft(
        self, 
        sketches: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Loft between multiple sketches."""
        solid_id = f"solid_{len(self.solids) + 1}"
        solid = {
            "id": solid_id,
            "type": "loft",
            "sketches": sketches,
        }
        self.solids[solid_id] = solid
        return solid
    
    def sweep(
        self, 
        profile: Dict[str, Any], 
        path: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Sweep a profile along a path."""
        solid_id = f"solid_{len(self.solids) + 1}"
        solid = {
            "id": solid_id,
            "type": "sweep",
            "profile": profile,
            "path": path,
        }
        self.solids[solid_id] = solid
        return solid
    
    def boolean_union(
        self, 
        solid1: Dict[str, Any], 
        solid2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Boolean union of two solids."""
        return {
            "type": "boolean",
            "operation": "union",
            "solids": [solid1, solid2],
        }
    
    def boolean_difference(
        self, 
        solid1: Dict[str, Any], 
        solid2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Boolean difference of two solids."""
        return {
            "type": "boolean",
            "operation": "difference",
            "solids": [solid1, solid2],
        }
    
    def boolean_intersection(
        self, 
        solid1: Dict[str, Any], 
        solid2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Boolean intersection of two solids."""
        return {
            "type": "boolean",
            "operation": "intersection",
            "solids": [solid1, solid2],
        }
    
    def calculate_mass_properties(
        self, 
        solid: Dict[str, Any], 
        density: float = 7850.0  # kg/m³, steel default
    ) -> Dict[str, float]:
        """Calculate mass properties of a solid."""
        # Simplified calculation - in real implementation would use actual geometry
        volume = 0.001  # m³ (placeholder)
        mass = volume * density
        return {
            "mass_kg": mass,
            "volume_m3": volume,
            "cog_x": 0.0,
            "cog_y": 0.0,
            "cog_z": 0.0,
            "surface_area_m2": 0.1,
        }
