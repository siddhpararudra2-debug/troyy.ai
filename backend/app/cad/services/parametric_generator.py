"""
Parametric Generator - Handles parametric design and constraints
"""
from typing import Dict, Any, List, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class ParametricGenerator:
    """Generates and manages parametric CAD models."""
    
    def __init__(self):
        self.parameters = {}
        self.constraints = []
        self.design_rules = []
    
    def define_parameter(
        self, 
        name: str, 
        value: float, 
        min_val: Optional[float] = None, 
        max_val: Optional[float] = None,
        units: str = "mm"
    ) -> Dict[str, Any]:
        """Define a parametric parameter."""
        param = {
            "name": name,
            "value": value,
            "min": min_val,
            "max": max_val,
            "units": units,
        }
        self.parameters[name] = param
        return param
    
    def apply_parameters(
        self, 
        base_geometry: Dict[str, Any], 
        parameters: Dict[str, float]
    ) -> Dict[str, Any]:
        """Apply parameters to base geometry."""
        parametric_model = {
            **base_geometry,
            "parametric": True,
            "parameters": parameters,
            "constraints": [],
        }
        
        for name, value in parameters.items():
            self.define_parameter(name, value)
        
        return parametric_model
    
    def add_constraint(
        self, 
        constraint_type: str, 
        entities: List[str], 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a geometric constraint."""
        constraint = {
            "type": constraint_type,
            "entities": entities,
            "parameters": parameters,
        }
        self.constraints.append(constraint)
        return constraint
    
    def add_dimension_constraint(
        self, 
        entity1: str, 
        entity2: str, 
        dimension: float,
        dimension_type: str = "distance"
    ) -> Dict[str, Any]:
        """Add a dimensional constraint."""
        return self.add_constraint(
            "dimension",
            [entity1, entity2],
            {"value": dimension, "type": dimension_type}
        )
    
    def add_coincident_constraint(
        self, 
        entity1: str, 
        entity2: str
    ) -> Dict[str, Any]:
        """Add a coincident constraint."""
        return self.add_constraint("coincident", [entity1, entity2], {})
    
    def add_parallel_constraint(
        self, 
        entity1: str, 
        entity2: str
    ) -> Dict[str, Any]:
        """Add a parallel constraint."""
        return self.add_constraint("parallel", [entity1, entity2], {})
    
    def add_perpendicular_constraint(
        self, 
        entity1: str, 
        entity2: str
    ) -> Dict[str, Any]:
        """Add a perpendicular constraint."""
        return self.add_constraint("perpendicular", [entity1, entity2], {})
    
    def add_horizontal_constraint(
        self, 
        entity: str
    ) -> Dict[str, Any]:
        """Add a horizontal constraint."""
        return self.add_constraint("horizontal", [entity], {})
    
    def add_vertical_constraint(
        self, 
        entity: str
    ) -> Dict[str, Any]:
        """Add a vertical constraint."""
        return self.add_constraint("vertical", [entity], {})
    
    def add_design_rule(
        self, 
        name: str, 
        rule_func: Callable[[Dict[str, Any]], bool],
        description: str = ""
    ) -> None:
        """Add a design rule for validation."""
        self.design_rules.append({
            "name": name,
            "rule": rule_func,
            "description": description,
        })
    
    def validate_design(
        self, 
        model: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate design against all rules."""
        errors = []
        for rule in self.design_rules:
            if not rule["rule"](model):
                errors.append(f"Rule failed: {rule['name']} - {rule['description']}")
        return len(errors) == 0, errors
    
    def regenerate(
        self, 
        model: Dict[str, Any], 
        new_parameters: Dict[str, float]
    ) -> Dict[str, Any]:
        """Regenerate model with new parameters."""
        updated_model = {**model}
        
        if "parameters" in updated_model:
            updated_model["parameters"].update(new_parameters)
        else:
            updated_model["parameters"] = new_parameters
        
        # Validate new parameters
        for name, value in new_parameters.items():
            if name in self.parameters:
                param = self.parameters[name]
                if param["min"] is not None and value < param["min"]:
                    logger.warning(f"Parameter {name} below minimum: {value} < {param['min']}")
                if param["max"] is not None and value > param["max"]:
                    logger.warning(f"Parameter {name} above maximum: {value} > {param['max']}")
        
        return updated_model
    
    def create_parameter_table(
        self, 
        model: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create a parameter table from model."""
        params = model.get("parameters", {})
        table = []
        for name, value in params.items():
            param_def = self.parameters.get(name, {})
            table.append({
                "name": name,
                "value": value,
                "min": param_def.get("min"),
                "max": param_def.get("max"),
                "units": param_def.get("units", "mm"),
            })
        return table
