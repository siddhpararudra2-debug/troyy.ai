"""
Dimensional Checker — unit consistency validation
"""
from typing import Dict, Any, List, Optional
import pint
from dataclasses import dataclass


ureg = pint.UnitRegistry()


@dataclass
class DimensionalCheckResult:
    valid: bool
    left_dimension: Optional[str] = None
    right_dimension: Optional[str] = None
    message: str = ""


class DimensionalChecker:
    """Checks consistency of units in expressions"""

    def check_dimensions(
        self,
        left_expr: str,
        right_expr: str,
        variables: Optional[Dict[str, str]] = None,
    ) -> DimensionalCheckResult:
        """Check dimensions of two expressions"""
        try:
            # Replace variables with their units
            left = left_expr
            right = right_expr
            if variables:
                for name, unit in variables.items():
                    left = left.replace(name, unit)
                    right = right.replace(name, unit)

            q_left = ureg.parse_expression(left)
            q_right = ureg.parse_expression(right)

            dim_left = str(q_left.dimensionality)
            dim_right = str(q_right.dimensionality)

            valid = q_left.dimensionality == q_right.dimensionality

            if valid:
                return DimensionalCheckResult(
                    valid=True,
                    left_dimension=dim_left,
                    right_dimension=dim_right,
                    message="Dimensions are consistent",
                )
            else:
                return DimensionalCheckResult(
                    valid=False,
                    left_dimension=dim_left,
                    right_dimension=dim_right,
                    message=f"Inconsistent dimensions: left is {dim_left}, right is {dim_right}",
                )
        except Exception as e:
            return DimensionalCheckResult(
                valid=False,
                message=str(e),
            )

    def validate_formula_units(
        self,
        formula: str,
        expected_output_units: str,
        variables: Dict[str, str],
    ) -> DimensionalCheckResult:
        """Validate formula's output units match expected"""
        return self.check_dimensions(formula, expected_output_units, variables)


def check_force_mass_velocity() -> DimensionalCheckResult:
    """Check invalid formula F = m·v"""
    checker = DimensionalChecker()
    return checker.check_dimensions(
        "mass * velocity",
        "force",
        variables={"mass": "kg", "velocity": "m/s", "force": "N"},
    )


def check_force_mass_acceleration() -> DimensionalCheckResult:
    """Check valid formula F = m·a"""
    checker = DimensionalChecker()
    return checker.check_dimensions(
        "mass * acceleration",
        "force",
        variables={"mass": "kg", "acceleration": "m/s²", "force": "N"},
    )
