"""
Troy — Calculation Input Validator
Validates inputs against formula constraints before execution.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.calculations.registry import FormulaDefinition


@dataclass
class ValidationResult:
    """Result of input validation."""
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    sanitized_params: dict[str, float]


def validate_calculation_inputs(
    formula_def: FormulaDefinition,
    parameters: dict[str, float],
) -> ValidationResult:
    """
    Validate calculation inputs against formula parameter definitions.

    Checks:
    1. Required parameters are present
    2. Values are within defined ranges
    3. Values are physically meaningful (non-negative where required)
    4. No unexpected parameters provided

    Args:
        formula_def: The formula's definition from the registry
        parameters: User-provided parameter values

    Returns:
        ValidationResult with errors, warnings, and sanitized parameters
    """
    errors: list[str] = []
    warnings: list[str] = []
    sanitized = dict(parameters)

    # Get expected parameter names
    expected_names = {p.name for p in formula_def.parameters}
    provided_names = set(parameters.keys())

    # Check for unexpected parameters
    unexpected = provided_names - expected_names
    if unexpected:
        warnings.append(
            f"Unexpected parameters ignored: {', '.join(unexpected)}"
        )
        for name in unexpected:
            sanitized.pop(name, None)

    # Validate each expected parameter
    for param_def in formula_def.parameters:
        value = parameters.get(param_def.name)

        # Missing parameter check
        if value is None:
            if param_def.default is not None:
                sanitized[param_def.name] = param_def.default
                warnings.append(
                    f"Using default value for {param_def.name}: "
                    f"{param_def.default} {param_def.unit}"
                )
            else:
                errors.append(
                    f"Missing required parameter: {param_def.name} "
                    f"({param_def.description}) [{param_def.unit}]"
                )
            continue

        # Type check
        if not isinstance(value, (int, float)):
            errors.append(
                f"Parameter {param_def.name} must be a number, got {type(value).__name__}"
            )
            continue

        # NaN / Infinity check
        import math
        if math.isnan(value) or math.isinf(value):
            errors.append(f"Parameter {param_def.name} cannot be NaN or Infinity")
            continue

        # Range checks
        if param_def.min_value is not None and value < param_def.min_value:
            if value < param_def.min_value * 0.5:  # Way out of range = error
                errors.append(
                    f"{param_def.name}={value} is far below valid range "
                    f"[{param_def.min_value}, {param_def.max_value}] {param_def.unit}"
                )
            else:
                warnings.append(
                    f"{param_def.name}={value} is below recommended minimum "
                    f"{param_def.min_value} {param_def.unit}"
                )

        if param_def.max_value is not None and value > param_def.max_value:
            if value > param_def.max_value * 2.0:  # Way out of range = error
                errors.append(
                    f"{param_def.name}={value} far exceeds valid range "
                    f"[{param_def.min_value}, {param_def.max_value}] {param_def.unit}"
                )
            else:
                warnings.append(
                    f"{param_def.name}={value} exceeds recommended maximum "
                    f"{param_def.max_value} {param_def.unit}"
                )

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        sanitized_params=sanitized,
    )
