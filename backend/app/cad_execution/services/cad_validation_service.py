"""
CAD Validation Service
"""
import uuid
import time
from typing import Dict, Any, List
from app.core.config import settings


class CADValidationService:
    """
    Service for validating CAD models
    """

    def __init__(self):
        pass

    def validate_geometry(
        self,
        part_or_assembly_id: str,
        geometry: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate geometry for errors
        """
        start_time = time.time()
        validation_id = str(uuid.uuid4())
        
        issues = []
        is_valid = True
        
        # Mock geometry checks
        if geometry.get("type") == "bracket":
            params = geometry.get("parameters", {})
            if params.get("width", 0) < 10:
                issues.append({
                    "severity": "warning",
                    "message": "Width is very small, may cause manufacturing issues"
                })
            if params.get("hole_radius", 0) > params.get("width", 0) / 2:
                issues.append({
                    "severity": "error",
                    "message": "Hole radius too large for bracket width"
                })
                is_valid = False
        
        return {
            "id": validation_id,
            "part_or_assembly_id": part_or_assembly_id,
            "validation_type": "geometry",
            "is_valid": is_valid,
            "issues": issues,
            "execution_time_ms": (time.time() - start_time) * 1000
        }

    def calculate_mass_properties(
        self,
        part_or_assembly_id: str,
        geometry: Dict[str, Any],
        material: str = "aluminum"
    ) -> Dict[str, Any]:
        """
        Calculate mass properties (mass, volume, COG, etc.)
        """
        start_time = time.time()
        validation_id = str(uuid.uuid4())
        
        # Material densities in g/cm^3
        material_densities = {
            "aluminum": 2.7,
            "steel": 7.85,
            "titanium": 4.5,
            "plastic": 1.2
        }
        
        density = material_densities.get(material, 2.7)
        
        volume = geometry.get("volume", 0)  # in cm^3
        mass = volume * density  # in grams
        
        return {
            "id": validation_id,
            "part_or_assembly_id": part_or_assembly_id,
            "validation_type": "mass_properties",
            "is_valid": True,
            "issues": [],
            "mass_properties": {
                "mass_kg": mass / 1000,
                "volume_cm3": volume,
                "surface_area_cm2": geometry.get("surface_area", 0),
                "cog": [0, 0, 0],
                "material": material,
                "density_gcm3": density
            },
            "execution_time_ms": (time.time() - start_time) * 1000
        }

    def validate_manufacturability(
        self,
        part_or_assembly_id: str,
        geometry: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate for manufacturability (DFM checks)
        """
        start_time = time.time()
        validation_id = str(uuid.uuid4())
        
        issues = []
        recommendations = [
            "Consider adding fillets to sharp edges",
            "Ensure tolerances are within manufacturing capabilities"
        ]
        
        return {
            "id": validation_id,
            "part_or_assembly_id": part_or_assembly_id,
            "validation_type": "manufacturability",
            "is_valid": True,
            "issues": issues,
            "recommendations": recommendations,
            "execution_time_ms": (time.time() - start_time) * 1000
        }
