"""
Component Library - Reusable engineering components
"""
from typing import Dict, Any, List, Optional
import uuid
import logging

logger = logging.getLogger(__name__)


class ComponentLibrary:
    """Library of standard engineering components."""
    
    def __init__(self):
        self.components = self._init_standard_components()
        self.suppliers = self._init_suppliers()
    
    def _init_standard_components(self) -> Dict[str, Any]:
        """Initialize standard component library."""
        return {
            "bearings": self._get_bearings(),
            "fasteners": self._get_fasteners(),
            "shafts": self._get_shafts(),
            "couplings": self._get_couplings(),
            "motors": self._get_motors(),
            "gearboxes": self._get_gearboxes(),
        }
    
    def _init_suppliers(self) -> Dict[str, Any]:
        """Initialize supplier database."""
        return {
            "mcmaster": {"name": "McMaster-Carr", "url": "https://www.mcmaster.com"},
            "misumi": {"name": "Misumi", "url": "https://us.misumi-ec.com"},
            "grainger": {"name": "Grainger", "url": "https://www.grainger.com"},
            "digikey": {"name": "Digi-Key", "url": "https://www.digikey.com"},
        }
    
    def _get_bearings(self) -> List[Dict[str, Any]]:
        """Get standard bearings."""
        return [
            {
                "id": "bearing_608",
                "name": "608 Ball Bearing",
                "type": "deep_groove",
                "inner_diameter": 8,
                "outer_diameter": 22,
                "width": 7,
                "load_rating": 3300,  # N
                "cost": 2.5,
                "suppliers": ["mcmaster", "misumi"],
            },
            {
                "id": "bearing_6000",
                "name": "6000 Ball Bearing",
                "type": "deep_groove",
                "inner_diameter": 10,
                "outer_diameter": 26,
                "width": 8,
                "load_rating": 4550,
                "cost": 3.0,
                "suppliers": ["mcmaster", "misumi"],
            },
            {
                "id": "bearing_6001",
                "name": "6001 Ball Bearing",
                "type": "deep_groove",
                "inner_diameter": 12,
                "outer_diameter": 28,
                "width": 8,
                "load_rating": 5100,
                "cost": 3.5,
                "suppliers": ["mcmaster", "misumi"],
            },
        ]
    
    def _get_fasteners(self) -> List[Dict[str, Any]]:
        """Get standard fasteners."""
        sizes = ["M3", "M4", "M5", "M6", "M8"]
        fasteners = []
        
        for size in sizes:
            fasteners.append({
                "id": f"socket_cap_{size}",
                "name": f"Socket Cap Screw {size}",
                "type": "socket_cap",
                "size": size,
                "material": "steel_1018",
                "cost": 0.05,
                "suppliers": ["mcmaster", "grainger"],
            })
            fasteners.append({
                "id": f"nut_{size}",
                "name": f"Hex Nut {size}",
                "type": "hex_nut",
                "size": size,
                "material": "steel_1018",
                "cost": 0.03,
                "suppliers": ["mcmaster", "grainger"],
            })
        
        return fasteners
    
    def _get_shafts(self) -> List[Dict[str, Any]]:
        """Get standard shafts."""
        diameters = [6, 8, 10, 12, 16, 20]
        shafts = []
        
        for d in diameters:
            shafts.append({
                "id": f"shaft_{d}mm",
                "name": f"Steel Shaft {d}mm",
                "diameter": d,
                "material": "steel_1018",
                "length_options": [100, 200, 300, 500],
                "cost_per_mm": 0.1,
                "suppliers": ["misumi", "mcmaster"],
            })
        
        return shafts
    
    def _get_couplings(self) -> List[Dict[str, Any]]:
        """Get standard couplings."""
        return [
            {
                "id": "coupling_rigid_8mm",
                "name": "Rigid Coupling 8mm",
                "type": "rigid",
                "bore1": 8,
                "bore2": 8,
                "outer_diameter": 20,
                "length": 30,
                "cost": 8.0,
                "suppliers": ["misumi", "mcmaster"],
            },
            {
                "id": "coupling_jaw_10mm",
                "name": "Jaw Coupling 10mm",
                "type": "jaw",
                "bore1": 10,
                "bore2": 10,
                "outer_diameter": 25,
                "length": 35,
                "cost": 12.0,
                "suppliers": ["misumi", "mcmaster"],
            },
        ]
    
    def _get_motors(self) -> List[Dict[str, Any]]:
        """Get standard motors."""
        return [
            {
                "id": "motor_nema17",
                "name": "NEMA 17 Stepper Motor",
                "type": "stepper",
                "torque": 0.4,  # Nm
                "voltage": 12,
                "current": 1.5,
                "steps_per_rev": 200,
                "cost": 15.0,
                "suppliers": ["digikey", "mcmaster"],
            },
            {
                "id": "motor_nema23",
                "name": "NEMA 23 Stepper Motor",
                "type": "stepper",
                "torque": 1.2,
                "voltage": 24,
                "current": 2.8,
                "steps_per_rev": 200,
                "cost": 30.0,
                "suppliers": ["digikey", "mcmaster"],
            },
            {
                "id": "motor_dc_12v",
                "name": "12V DC Motor",
                "type": "dc",
                "voltage": 12,
                "rpm": 5000,
                "torque": 0.01,
                "cost": 8.0,
                "suppliers": ["digikey"],
            },
        ]
    
    def _get_gearboxes(self) -> List[Dict[str, Any]]:
        """Get standard gearboxes."""
        ratios = [10, 20, 50, 100]
        gearboxes = []
        
        for ratio in ratios:
            gearboxes.append({
                "id": f"gearbox_{ratio}:1",
                "name": f"Gearbox {ratio}:1",
                "type": "spur",
                "ratio": ratio,
                "max_torque": 5.0,
                "cost": 25.0 * (ratio / 10),
                "suppliers": ["mcmaster", "misumi"],
            })
        
        return gearboxes
    
    def search_components(
        self, 
        category: Optional[str] = None, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search components by category and filters."""
        results = []
        
        if category:
            categories = [category] if category in self.components else []
        else:
            categories = list(self.components.keys())
        
        for cat in categories:
            for component in self.components[cat]:
                if self._matches_filters(component, filters):
                    results.append({**component, "category": cat})
        
        return results
    
    def _matches_filters(
        self, 
        component: Dict[str, Any], 
        filters: Optional[Dict[str, Any]]
    ) -> bool:
        """Check if component matches filters."""
        if not filters:
            return True
        
        for key, value in filters.items():
            if key in component:
                if isinstance(value, (list, tuple)):
                    if component[key] not in value:
                        return False
                elif component[key] != value:
                    return False
        return True
    
    def get_component(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Get component by ID."""
        for category in self.components.values():
            for component in category:
                if component["id"] == component_id:
                    return component
        return None
    
    def get_supplier_info(self, supplier_id: str) -> Optional[Dict[str, Any]]:
        """Get supplier information."""
        return self.suppliers.get(supplier_id)
