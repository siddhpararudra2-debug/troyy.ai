"""
Troy — Unit Validator
Performs Pint-based dimensional analysis to verify unit validity and consistency.
"""

from __future__ import annotations

import pint
from typing import List
from app.calculations.units import ureg
from app.solver.models.domain_models import SolverState
from app.validation.schemas.validation_schemas import ValidationIssueSchema
from app.validation.services.base import AsyncBaseValidator


class UnitValidator(AsyncBaseValidator):
    """Checks for invalid units, missing units, and dimensional mismatches in parameters and results."""

    name = "UnitValidator"

    async def validate(self, state: SolverState) -> List[ValidationIssueSchema]:
        issues: List[ValidationIssueSchema] = []

        # List of variables to check
        all_vars = []
        for name, data in state.variables.known.items():
            all_vars.append((name, data, "known"))
        for name, data in state.variables.derived.items():
            all_vars.append((name, data, "derived"))
        for name, data in state.variables.constants.items():
            all_vars.append((name, data, "constant"))

        # Define dimension groups to check compatibility
        dimension_map = {
            "voltage": "volt",
            "v_in": "volt",
            "v_out": "volt",
            "current": "ampere",
            "i_max": "ampere",
            "i_continuous": "ampere",
            "power": "watt",
            "p_hover": "watt",
            "p_max": "watt",
            "thrust": "newton",
            "t_total": "newton",
            "force": "newton",
            "mass": "kilogram",
            "m_payload": "kilogram",
            "m_total": "kilogram",
            "m_empty": "kilogram",
            "weight": "kilogram",  # mass-equivalent or force
            "length": "meter",
            "reach": "meter",
            "radius": "meter",
            "diameter": "meter",
            "torque": "newton * meter",
            "pressure": "pascal",
            "p_ambient": "pascal",
        }

        # Helper to check if a unit string is valid in Pint
        def is_valid_unit(unit_str: str) -> bool:
            try:
                ureg(unit_str)
                return True
            except Exception:
                return False

        # Helper to check if dimensions match
        def check_dimensions(unit_str: str, expected_base: str) -> bool:
            try:
                q = ureg.Quantity(1, unit_str)
                return q.check(expected_base)
            except Exception:
                # Fallback: check if they can convert
                try:
                    ureg.Quantity(1, unit_str).to(expected_base)
                    return True
                except Exception:
                    return False

        for name, var_data, var_type in all_vars:
            unit = var_data.get("unit")
            value = var_data.get("value")

            # Ignore variables with no value and no unit if they are just placeholders
            if value is None and not unit:
                continue

            # ── 1. Check for missing units on physical quantities ──
            name_lower = name.lower()
            matching_key = None
            for key in dimension_map:
                if key in name_lower:
                    matching_key = key
                    break

            if not unit:
                # If it's a known physical quantity but lacks unit
                if matching_key:
                    issues.append(
                        ValidationIssueSchema(
                            severity="warning",
                            category="Units",
                            message=f"Missing unit for variable '{name}' ({var_type})",
                            validator_name=self.name,
                            engineering_reasoning=f"Variable '{name}' appears to represent {matching_key}, which requires a physical unit.",
                            recommendation=f"Define a valid unit string (e.g. '{dimension_map[matching_key]}') for '{name}'.",
                        )
                    )
                continue

            # ── 2. Check for invalid unit strings ──
            if not is_valid_unit(unit):
                issues.append(
                    ValidationIssueSchema(
                        severity="error",
                        category="Units",
                        message=f"Invalid unit symbol '{unit}' in variable '{name}'",
                        validator_name=self.name,
                        engineering_reasoning=f"The unit string '{unit}' is not recognized by the dimensional system database.",
                        recommendation="Use standard SI or Imperial symbols (e.g., 'm' instead of 'meters', 'V' instead of 'volts', 'N*m' for torque).",
                    )
                )
                continue

            # ── 3. Check for dimensional mismatch ──
            if matching_key:
                expected_unit = dimension_map[matching_key]
                # If we have a weight term, it might be force (N) or mass (kg), check both
                if matching_key == "weight":
                    is_ok = check_dimensions(unit, "kilogram") or check_dimensions(unit, "newton")
                elif matching_key == "torque":
                    is_ok = check_dimensions(unit, "newton * meter")
                elif matching_key == "pressure":
                    is_ok = check_dimensions(unit, "pascal") or check_dimensions(unit, "psi")
                else:
                    is_ok = check_dimensions(unit, expected_unit)

                if not is_ok:
                    issues.append(
                        ValidationIssueSchema(
                            severity="error",
                            category="Units",
                            message=f"Dimensional mismatch: variable '{name}' has unit '{unit}' but expected type {matching_key}.",
                            validator_name=self.name,
                            engineering_reasoning=f"Variable '{name}' is expected to represent a {matching_key} dimension (compatible with '{expected_unit}'), but '{unit}' represents a different dimensionality.",
                            recommendation=f"Change unit of '{name}' to a compatible dimension (e.g. {expected_unit}).",
                        )
                    )

        return issues
