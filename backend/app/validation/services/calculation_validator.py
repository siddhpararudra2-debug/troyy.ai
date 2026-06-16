"""
Troy — Calculation Validator
Independently verifies calculations by executing formula functions and matching outputs.
"""

from __future__ import annotations

import math
from typing import List, Any, Dict
from app.calculations.registry import registry
from app.solver.models.domain_models import SolverState
from app.validation.schemas.validation_schemas import ValidationIssueSchema
from app.validation.services.base import AsyncBaseValidator


class CalculationValidator(AsyncBaseValidator):
    """Recomputes formula results to check for mathematical accuracy, overflow, and division by zero."""

    name = "CalculationValidator"

    async def validate(self, state: SolverState) -> List[ValidationIssueSchema]:
        issues: List[ValidationIssueSchema] = []

        # Pool of all variables to use as inputs
        variable_pool: Dict[str, float] = {}

        # Fill the pool
        for name, data in state.variables.known.items():
            if "value" in data and data["value"] is not None:
                try:
                    variable_pool[name] = float(data["value"])
                except ValueError:
                    pass

        for name, data in state.variables.derived.items():
            if "value" in data and data["value"] is not None:
                try:
                    variable_pool[name] = float(data["value"])
                except ValueError:
                    pass

        for name, data in state.variables.constants.items():
            if "value" in data and data["value"] is not None:
                try:
                    variable_pool[name] = float(data["value"])
                except ValueError:
                    pass

        # Also pull from calculation results
        for name, val in state.calculation_results.items():
            if val is not None:
                try:
                    variable_pool[name] = float(val)
                except ValueError:
                    pass

        # Common alias map matching OrchestrationService
        alias_map = {
            "T": "T_total",
            "m": "m_total",
            "P_hover": "P",
        }

        def find_value_in_pool(param_name: str) -> float | None:
            if param_name in variable_pool:
                return variable_pool[param_name]
            if param_name in alias_map and alias_map[param_name] in variable_pool:
                return variable_pool[alias_map[param_name]]
            # Reverse alias search
            for k, v in alias_map.items():
                if v == param_name and k in variable_pool:
                    return variable_pool[k]
            # Domain-specific fallbacks
            if param_name == "m":
                if "m_total" in variable_pool:
                    return variable_pool["m_total"]
                if "m_payload" in variable_pool:
                    return variable_pool["m_payload"]
            if param_name == "T":
                if "T_total" in variable_pool:
                    return variable_pool["T_total"]
            return None

        # Loop through selected formulas
        for select_def in state.selected_formulas:
            formula_id = select_def.formula_id
            formula_def = registry.get(formula_id)

            if not formula_def:
                issues.append(
                    ValidationIssueSchema(
                        severity="warning",
                        category="Calculations",
                        message=f"Formula registry lookup failed for: '{formula_id}'",
                        validator_name=self.name,
                        engineering_reasoning="The selected formula ID was not found in the global formula registry.",
                        recommendation="Register the formula definition using @register_formula or check formula ID spelling.",
                    )
                )
                continue

            if not formula_def.func:
                continue

            # Build inputs dictionary
            inputs = {}
            missing_inputs = []
            for param in formula_def.parameters:
                val = find_value_in_pool(param.name)
                if val is not None:
                    inputs[param.name] = val
                else:
                    if param.default is not None:
                        inputs[param.name] = param.default
                    else:
                        missing_inputs.append(param.name)

            if missing_inputs:
                # Already handled by FormulaValidator, but skip recompute
                continue

            # ── 1. Check for potential numerical instability before running ──
            # E.g. check for near-zero denominators
            for name, val in inputs.items():
                # If we're dividing by a parameter (heuristic checking)
                if "efficiency" in name.lower() and val <= 0:
                    issues.append(
                        ValidationIssueSchema(
                            severity="error",
                            category="Calculations",
                            message=f"Numerical instability: Parameter '{name}' for formula '{formula_def.name}' is non-positive ({val})",
                            validator_name=self.name,
                            engineering_reasoning="Efficiency and scale parameters must be positive to prevent division by zero or negative energy results.",
                            recommendation="Check input values and set a positive non-zero efficiency factor.",
                        )
                    )

            # ── 2. Recompute formula ──
            try:
                computed_outputs = formula_def.func(**inputs)
                if not isinstance(computed_outputs, dict):
                    # If single output, map to first expected output
                    if len(formula_def.outputs) == 1:
                        computed_outputs = {formula_def.outputs[0].name: computed_outputs}
                    else:
                        # Cannot map, skip
                        continue

                # ── 3. Validate computed outputs vs actual results ──
                for out_def in formula_def.outputs:
                    out_name = out_def.name
                    expected_val = float(computed_outputs.get(out_name, 0.0))

                    # Find actual value stored in results or derived variables
                    actual_val = find_value_in_pool(out_name)

                    if actual_val is not None:
                        # Float comparison with relative tolerance
                        if not math.isclose(actual_val, expected_val, rel_tol=1e-4, abs_tol=1e-6):
                            issues.append(
                                ValidationIssueSchema(
                                    severity="error",
                                    category="Calculations",
                                    message=f"Calculation discrepancy in output '{out_name}' of formula '{formula_def.name}'",
                                    validator_name=self.name,
                                    engineering_reasoning=f"Re-computed value of {expected_val:.5g} does not match the actual result of {actual_val:.5g}.",
                                    recommendation="Verify calculation steps or check for parameter rounding errors during intermediate states.",
                                )
                            )

                    # ── 4. Check for unphysical/unrealistic outputs ──
                    if "temperature" in out_name.lower() and expected_val < -273.15:
                        issues.append(
                            ValidationIssueSchema(
                                severity="error",
                                category="Calculations",
                                message=f"Unphysical temperature result: {expected_val:.2f} C",
                                validator_name=self.name,
                                engineering_reasoning="Result falls below absolute zero (-273.15 C), which is physically impossible.",
                                recommendation="Review input parameters and thermal dissipation formulas.",
                            )
                        )
                    elif "speed" in out_name.lower() and expected_val > 299792458:
                        issues.append(
                            ValidationIssueSchema(
                                severity="error",
                                category="Calculations",
                                message=f"Unphysical velocity result: {expected_val:.2e} m/s",
                                validator_name=self.name,
                                engineering_reasoning="Calculated velocity exceeds the speed of light (2.998e8 m/s).",
                                recommendation="Check scaling factors, energy inputs, and physical equations.",
                            )
                        )
                    elif "efficiency" in out_name.lower() and expected_val > 1.0:
                        issues.append(
                            ValidationIssueSchema(
                                severity="error",
                                category="Calculations",
                                message=f"Unphysical efficiency result: {expected_val * 100:.1f}%",
                                validator_name=self.name,
                                engineering_reasoning="Calculated system efficiency exceeds 100%, violating the First Law of Thermodynamics.",
                                recommendation="Check formula term ordering (inputs vs outputs comparison).",
                            )
                        )

            except ZeroDivisionError as e:
                issues.append(
                    ValidationIssueSchema(
                        severity="error",
                        category="Calculations",
                        message=f"Mathematical error: Division by Zero in formula '{formula_def.name}'",
                        validator_name=self.name,
                        engineering_reasoning=f"Executing formula with inputs {inputs} caused a ZeroDivisionError: {str(e)}",
                        recommendation="Ensure that denominators (like efficiency, velocity, or joint coordinates) are non-zero.",
                    )
                )
            except ValueError as e:
                issues.append(
                    ValidationIssueSchema(
                        severity="error",
                        category="Calculations",
                        message=f"Mathematical error: Value Error in formula '{formula_def.name}'",
                        validator_name=self.name,
                        engineering_reasoning=f"Executing formula with inputs {inputs} caused a ValueError: {str(e)}",
                        recommendation="Check for negative arguments in square roots or non-positive arguments in logarithms.",
                    )
                )
            except Exception as e:
                issues.append(
                    ValidationIssueSchema(
                        severity="error",
                        category="Calculations",
                        message=f"Calculation failure: Error in formula '{formula_def.name}'",
                        validator_name=self.name,
                        engineering_reasoning=f"Executing formula with inputs {inputs} raised an unexpected exception: {str(e)}",
                        recommendation="Review the formula implementation for programming bugs or invalid numeric casts.",
                    )
                )

        return issues
