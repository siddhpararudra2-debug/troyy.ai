"""
Mechanical Reasoner - Handles mechanical design logic and recommendations
"""
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class MechanicalReasoner:
    """Reasoning engine for mechanical design decisions."""
    
    def __init__(self):
        self.material_selector = MaterialSelector()
        self.fastener_selector = FastenerSelector()
        self.tolerance_engine = ToleranceEngine()
    
    def analyze_requirements(
        self, 
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze requirements and provide design recommendations."""
        analysis = {
            "material_recommendations": self.material_selector.recommend_materials(requirements),
            "fastener_recommendations": self.fastener_selector.recommend_fasteners(requirements),
            "tolerance_recommendations": self.tolerance_engine.recommend_tolerances(requirements),
            "structural_recommendations": self._get_structural_recommendations(requirements),
        }
        return analysis
    
    def _get_structural_recommendations(
        self, 
        requirements: Dict[str, Any]
    ) -> List[str]:
        """Get structural design recommendations."""
        recommendations = []
        load = requirements.get("load_kg", 0)
        
        if load > 100:
            recommendations.append("Consider using rib structures for stiffness")
            recommendations.append("Evaluate composite materials for weight savings")
        
        if requirements.get("vibration", False):
            recommendations.append("Add damping features or materials")
        
        if requirements.get("temperature_range", [0, 25])[1] > 100:
            recommendations.append("Use high-temperature resistant materials")
            recommendations.append("Consider thermal expansion in tolerances")
        
        return recommendations


class MaterialSelector:
    """Selects appropriate materials based on requirements."""
    
    MATERIALS = {
        "aluminum_6061": {
            "name": "Aluminum 6061",
            "density": 2700,  # kg/m³
            "youngs_modulus": 69e9,  # Pa
            "yield_strength": 276e6,  # Pa
            "ultimate_strength": 310e6,  # Pa
            "cost_per_kg": 3.0,  # USD
            "categories": ["metal", "lightweight", "structural"],
        },
        "steel_1018": {
            "name": "Steel 1018",
            "density": 7870,
            "youngs_modulus": 200e9,
            "yield_strength": 220e6,
            "ultimate_strength": 400e6,
            "cost_per_kg": 1.0,
            "categories": ["metal", "structural", "low_cost"],
        },
        "stainless_steel_304": {
            "name": "Stainless Steel 304",
            "density": 8000,
            "youngs_modulus": 193e9,
            "yield_strength": 215e6,
            "ultimate_strength": 505e6,
            "cost_per_kg": 6.0,
            "categories": ["metal", "corrosion_resistant", "food_safe"],
        },
        "titanium_grade5": {
            "name": "Titanium Grade 5",
            "density": 4430,
            "youngs_modulus": 114e9,
            "yield_strength": 880e6,
            "ultimate_strength": 950e6,
            "cost_per_kg": 60.0,
            "categories": ["metal", "lightweight", "high_strength", "biocompatible"],
        },
        "carbon_fiber": {
            "name": "Carbon Fiber Composite",
            "density": 1600,
            "youngs_modulus": 150e9,
            "yield_strength": 600e6,
            "ultimate_strength": 700e6,
            "cost_per_kg": 50.0,
            "categories": ["composite", "lightweight", "high_strength"],
        },
        "abs": {
            "name": "ABS Plastic",
            "density": 1050,
            "youngs_modulus": 2.3e9,
            "yield_strength": 40e6,
            "ultimate_strength": 43e6,
            "cost_per_kg": 2.5,
            "categories": ["plastic", "3d_printable", "low_cost"],
        },
        "nylon": {
            "name": "Nylon (PA6)",
            "density": 1140,
            "youngs_modulus": 3.0e9,
            "yield_strength": 45e6,
            "ultimate_strength": 75e6,
            "cost_per_kg": 3.0,
            "categories": ["plastic", "wear_resistant", "low_friction"],
        },
    }
    
    def recommend_materials(
        self, 
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Recommend materials based on requirements."""
        candidates = []
        weight_priority = requirements.get("weight_priority", "medium")
        strength_priority = requirements.get("strength_priority", "medium")
        cost_priority = requirements.get("cost_priority", "medium")
        
        for material_id, material in self.MATERIALS.items():
            score = self._score_material(material, requirements)
            candidates.append({
                "id": material_id,
                **material,
                "score": score,
            })
        
        # Sort by score descending
        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:5]
    
    def _score_material(
        self, 
        material: Dict[str, Any], 
        requirements: Dict[str, Any]
    ) -> float:
        """Score a material based on requirements."""
        score = 0.0
        
        # Weight score (lower density is better for lightweight)
        weight_priority = requirements.get("weight_priority", "medium")
        if weight_priority == "high":
            score += (10000 - material["density"]) / 10000 * 40
        elif weight_priority == "medium":
            score += (10000 - material["density"]) / 10000 * 20
        
        # Strength score
        strength_priority = requirements.get("strength_priority", "medium")
        normalized_strength = material["ultimate_strength"] / 1e9
        if strength_priority == "high":
            score += normalized_strength * 40
        elif strength_priority == "medium":
            score += normalized_strength * 20
        
        # Cost score (lower cost is better)
        cost_priority = requirements.get("cost_priority", "medium")
        normalized_cost = max(0, 100 - material["cost_per_kg"]) / 100
        if cost_priority == "high":
            score += normalized_cost * 40
        elif cost_priority == "medium":
            score += normalized_cost * 20
        
        return score
    
    def get_material(self, material_id: str) -> Optional[Dict[str, Any]]:
        """Get material by ID."""
        return self.MATERIALS.get(material_id)


class FastenerSelector:
    """Selects appropriate fasteners based on requirements."""
    
    FASTENER_TYPES = {
        "socket_cap_screw": {
            "name": "Socket Cap Screw",
            "categories": ["high_strength", "precision"],
            "materials": ["steel", "stainless_steel", "titanium"],
        },
        "hex_bolt": {
            "name": "Hex Bolt",
            "categories": ["general_purpose", "low_cost"],
            "materials": ["steel", "stainless_steel"],
        },
        "set_screw": {
            "name": "Set Screw",
            "categories": ["positioning", "low_profile"],
            "materials": ["steel", "stainless_steel"],
        },
        "washer": {
            "name": "Washer",
            "categories": ["load_distribution"],
            "materials": ["steel", "stainless_steel", "aluminum"],
        },
        "lock_nut": {
            "name": "Lock Nut",
            "categories": ["vibration_resistant"],
            "materials": ["steel", "stainless_steel"],
        },
    }
    
    SIZES = ["M2", "M2.5", "M3", "M4", "M5", "M6", "M8", "M10", "M12"]
    
    def recommend_fasteners(
        self, 
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Recommend fasteners based on requirements."""
        recommendations = []
        
        load = requirements.get("load_kg", 10)
        vibration = requirements.get("vibration", False)
        
        # Calculate required size
        size_index = min(int(load / 10), len(self.SIZES) - 1)
        recommended_size = self.SIZES[size_index]
        
        # Recommend fastener types
        if vibration:
            types = ["socket_cap_screw", "lock_nut", "washer"]
        else:
            types = ["hex_bolt", "washer"]
        
        for fastener_type in types:
            if fastener_type in self.FASTENER_TYPES:
                recommendations.append({
                    "type": fastener_type,
                    **self.FASTENER_TYPES[fastener_type],
                    "recommended_size": recommended_size,
                })
        
        return recommendations


class ToleranceEngine:
    """Engine for tolerance analysis and recommendations."""
    
    FIT_TYPES = {
        "clearance": {"description": "Clearance fit - parts can move", "h_tolerance": "H7", "s_tolerance": "g6"},
        "transition": {"description": "Transition fit - slight interference", "h_tolerance": "H7", "s_tolerance": "k6"},
        "interference": {"description": "Interference fit - press fit", "h_tolerance": "H7", "s_tolerance": "p6"},
    }
    
    def recommend_tolerances(
        self, 
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Recommend tolerances based on requirements."""
        recommendations = []
        
        fit_type = requirements.get("fit_type", "clearance")
        nominal_size = requirements.get("nominal_size", 10)
        
        if fit_type in self.FIT_TYPES:
            fit = self.FIT_TYPES[fit_type]
            recommendations.append({
                "fit_type": fit_type,
                "description": fit["description"],
                "hole_tolerance": fit["h_tolerance"],
                "shaft_tolerance": fit["s_tolerance"],
                "nominal_size": nominal_size,
            })
        
        # General tolerance recommendations
        recommendations.append({
            "type": "general",
            "recommendation": "Use ISO 2768 medium for general tolerances",
        })
        
        return recommendations
    
    def calculate_tolerance_stackup(
        self, 
        dimensions: List[Dict[str, float]]
    ) -> Dict[str, float]:
        """Calculate tolerance stack-up."""
        nominal_total = sum(d["nominal"] for d in dimensions)
        min_total = sum(d["min"] for d in dimensions)
        max_total = sum(d["max"] for d in dimensions)
        
        return {
            "nominal": nominal_total,
            "min": min_total,
            "max": max_total,
            "total_tolerance": max_total - min_total,
        }
