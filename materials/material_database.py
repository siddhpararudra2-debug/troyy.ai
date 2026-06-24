"""Material Database - Stores and retrieves material data in Sprint 16."""
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime


class MaterialDatabase:
    """Database of engineering materials."""

    def __init__(self):
        self.materials: Dict[str, Dict[str, Any]] = {}

    def add_material(
        self,
        name: str,
        material_type: str,
        properties: Dict[str, Any],
        cost_per_unit: Optional[float] = None,
        supplier: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a new material to the database."""
        material_id = str(uuid.uuid4())
        material = {
            "id": material_id,
            "name": name,
            "type": material_type,
            "properties": properties,
            "cost_per_unit": cost_per_unit,
            "supplier": supplier,
            "created_at": datetime.utcnow().isoformat(),
        }
        self.materials[material_id] = material
        return material

    def get_material(self, material_id: str) -> Optional[Dict[str, Any]]:
        """Get a material by ID."""
        return self.materials.get(material_id)

    def search_materials(
        self,
        material_type: Optional[str] = None,
        min_property: Optional[Dict[str, float]] = None,
    ) -> List[Dict[str, Any]]:
        """Search materials by type and properties."""
        results = list(self.materials.values())
        if material_type:
            results = [m for m in results if m["type"] == material_type]
        if min_property:
            for prop, min_val in min_property.items():
                results = [
                    m for m in results
                    if prop in m["properties"] and m["properties"][prop] >= min_val
                ]
        return results
