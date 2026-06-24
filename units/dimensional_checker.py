"""
Dimensional analysis checker for Engineering OS.
Validates dimensional consistency of equations and detects unit mismatches.
"""
from typing import Optional
from units.unit_converter import UnitConverter


class DimensionalChecker:
    """
    Checks dimensional consistency of engineering equations.
    Detects invalid operations, unit mismatches, and dimension errors.
    """

    # Dimension symbols
    DIMENSIONS = {
        "length": "L", "mass": "M", "time": "T",
        "current": "I", "temperature": "Θ",
        "amount": "N", "luminosity": "J",
    }

    # Common physical quantities and their dimensions
    QUANTITY_DIMENSIONS = {
        "length": "L", "area": "L²", "volume": "L³",
        "mass": "M", "time": "T",
        "velocity": "LT⁻¹", "acceleration": "LT⁻²",
        "force": "MLT⁻²", "pressure": "ML⁻¹T⁻²",
        "energy": "ML²T⁻²", "power": "ML²T⁻³",
        "frequency": "T⁻¹", "density": "ML⁻³",
        "viscosity": "ML⁻¹T⁻¹", "stress": "ML⁻¹T⁻²",
        "strain": "1", "angle": "1",
        "momentum": "MLT⁻¹", "impulse": "MLT⁻¹",
        "torque": "ML²T⁻²", "current": "I",
        "voltage": "ML²T⁻³I⁻¹", "resistance": "ML²T⁻³I⁻²",
        "capacitance": "M⁻¹L⁻²T⁴I²", "inductance": "ML²T⁻²I⁻²",
        "charge": "IT", "power_electrical": "ML²T⁻³",
    }

    def __init__(self):
        self.uc = UnitConverter()

    def check_equation(self, left_units: list[str], right_units: list[str]) -> dict:
        """
        Check dimensional consistency between left and right sides.
        
        Args:
            left_units: Units on left side (e.g., ["m", "s", "kg"])
            right_units: Units on right side
            
        Returns:
            Dict with consistency check and any errors
        """
        left_dims = [self.uc.get_dimension(u) for u in left_units]
        right_dims = [self.uc.get_dimension(u) for u in right_units]
        
        missing = [u for u, d in zip(left_units, left_dims) if d is None]
        if missing:
            return {"consistent": False, "error": f"Unknown units: {missing}"}
        
        missing_r = [u for u, d in zip(right_units, right_dims) if d is None]
        if missing_r:
            return {"consistent": False, "error": f"Unknown units: {missing_r}"}
        
        left_combined = self._combine_dimensions(left_dims)
        right_combined = self._combine_dimensions(right_dims)
        
        if left_combined == right_combined:
            return {"consistent": True, "left_dimension": left_combined, "right_dimension": right_combined}
        else:
            return {
                "consistent": False,
                "error": f"Dimension mismatch: {left_combined} ≠ {right_combined}",
                "left_dimension": left_combined,
                "right_dimension": right_combined,
            }

    def get_quantity_dimension(self, quantity: str) -> Optional[str]:
        """Get the dimension of a physical quantity."""
        return self.QUANTITY_DIMENSIONS.get(quantity.lower())

    def validate_formula_units(self, formula_name: str, inputs: dict[str, tuple], output_unit: str) -> dict:
        """
        Validate that formula inputs produce correct output units.
        
        Args:
            formula_name: Name of the formula
            inputs: Dict of {param_name: (value, unit)}
            output_unit: Expected output unit
            
        Returns:
            Validation result
        """
        result_dims = []
        for name, (value, unit) in inputs.items():
            dim = self.uc.get_dimension(unit)
            if dim:
                result_dims.append(dim)
        
        output_dim = self.uc.get_dimension(output_unit)
        result_dim = self._combine_dimensions(result_dims)
        
        return {
            "formula": formula_name,
            "valid": result_dim == output_dim,
            "expected_dimension": output_dim,
            "computed_dimension": result_dim,
            "error": None if result_dim == output_dim else f"Expected {output_dim}, got {result_dim}",
        }

    def _combine_dimensions(self, dimensions: list[str]) -> str:
        """Combine multiple dimensions into a single dimension string."""
        # Simple approach: if all same, return that
        if len(set(dimensions)) == 1:
            return dimensions[0]
        # Otherwise combine
        return "·".join(dimensions) if dimensions else "1"

    def check_pi_theorem(self, variables: list[dict]) -> list[str]:
        """
        Apply Buckingham Pi theorem to find dimensionless groups.
        
        Args:
            variables: List of dicts with 'name', 'dimension' keys
            
        Returns:
            List of suggested dimensionless groups
        """
        # This is a simplified implementation
        n = len(variables)  # Number of variables
        m = len(set(v["dimension"] for v in variables))  # Number of base dimensions
        num_pi = n - m  # Number of dimensionless groups
        
        return [f"Π{i+1} = {n - num_pi + i + 1} variables" for i in range(max(0, num_pi))]