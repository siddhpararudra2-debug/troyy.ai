"""
Troy — Calculation Engine
Core SymPy-based engine that produces step-by-step calculations
with LaTeX rendering at each stage.

Pipeline:
  1. Formula Lookup (Registry)
  2. Input Validation
  3. Symbolic Expression Build (SymPy)
  4. Value Substitution
  5. Step-by-Step Simplification
  6. Numerical Evaluation
  7. LaTeX Rendering
  8. Result Packaging
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

import sympy as sp
from sympy import latex, symbols, simplify, N

from app.calculations.registry import FormulaDefinition, registry
from app.core.logging import get_logger

logger = get_logger("engine")


# ── Step Data Structures ─────────────────────────────────────────
@dataclass
class CalculationStep:
    """A single step in a calculation trace."""
    order: int
    step_type: str       # symbolic | substitution | simplification | result | unit_conversion
    description: str
    latex_expression: str
    variables: dict[str, str] = field(default_factory=dict)


@dataclass
class CalculationResult:
    """Complete result of a calculation, including all steps."""
    id: str
    formula_id: str
    title: str
    steps: list[CalculationStep]
    results: dict[str, float]
    results_formatted: dict[str, str]
    latex_summary: str
    execution_time_ms: float
    warnings: list[str] = field(default_factory=list)
    error: str | None = None


# ── Calculation Engine ───────────────────────────────────────────
class CalculationEngine:
    """
    Core computation engine using SymPy for symbolic math.

    Produces transparent, step-by-step calculations that show:
    1. The symbolic formula
    2. Substitution of numerical values
    3. Simplification steps
    4. Final numerical result

    Every step is rendered in LaTeX for display.
    """

    def execute(
        self,
        formula_id: str,
        parameters: dict[str, float],
    ) -> CalculationResult:
        """
        Execute a calculation with full step-by-step tracing.

        Args:
            formula_id: Registry ID of the formula
            parameters: Parameter name → value mapping

        Returns:
            CalculationResult with all steps and final values
        """
        start_time = time.perf_counter()
        calc_id = str(uuid.uuid4())
        steps: list[CalculationStep] = []
        warnings: list[str] = []

        # ── Step 0: Look up formula ──────────────────────────────
        formula_def = registry.get(formula_id)
        if formula_def is None:
            return CalculationResult(
                id=calc_id,
                formula_id=formula_id,
                title="Unknown Formula",
                steps=[],
                results={},
                results_formatted={},
                latex_summary="",
                execution_time_ms=0,
                error=f"Formula '{formula_id}' not found in registry",
            )

        # ── Step 1: Validate inputs ─────────────────────────────
        validation_warnings = self._validate_inputs(formula_def, parameters)
        warnings.extend(validation_warnings)

        # ── Step 2: Execute the formula function ─────────────────
        try:
            result_data = formula_def.func(**parameters)
        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000
            return CalculationResult(
                id=calc_id,
                formula_id=formula_id,
                title=formula_def.name,
                steps=[],
                results={},
                results_formatted={},
                latex_summary="",
                execution_time_ms=elapsed,
                error=f"Calculation error: {str(e)}",
            )

        # Extract steps, results, and summary from the formula function
        calc_steps = result_data.get("steps", [])
        calc_results = result_data.get("results", {})
        latex_summary = result_data.get("latex_summary", "")

        # Convert raw steps into CalculationStep objects
        for i, step_data in enumerate(calc_steps):
            steps.append(CalculationStep(
                order=i + 1,
                step_type=step_data.get("type", "symbolic"),
                description=step_data.get("description", ""),
                latex_expression=step_data.get("latex", ""),
                variables=step_data.get("variables", {}),
            ))

        # Format results with units
        results_formatted = {}
        for output_def in formula_def.outputs:
            key = output_def.name
            if key in calc_results:
                value = calc_results[key]
                results_formatted[key] = f"{value:.6g} {output_def.unit}"

        elapsed = (time.perf_counter() - start_time) * 1000

        return CalculationResult(
            id=calc_id,
            formula_id=formula_id,
            title=formula_def.name,
            steps=steps,
            results=calc_results,
            results_formatted=results_formatted,
            latex_summary=latex_summary,
            execution_time_ms=elapsed,
            warnings=warnings,
        )

    def _validate_inputs(
        self,
        formula_def: FormulaDefinition,
        parameters: dict[str, float],
    ) -> list[str]:
        """Validate input parameters against formula constraints."""
        warnings = []

        for param_def in formula_def.parameters:
            value = parameters.get(param_def.name)

            if value is None:
                if param_def.default is not None:
                    parameters[param_def.name] = param_def.default
                else:
                    warnings.append(
                        f"Missing required parameter: {param_def.name} ({param_def.description})"
                    )
                continue

            # Range checks
            if param_def.min_value is not None and value < param_def.min_value:
                warnings.append(
                    f"{param_def.name}={value} is below minimum {param_def.min_value} {param_def.unit}"
                )
            if param_def.max_value is not None and value > param_def.max_value:
                warnings.append(
                    f"{param_def.name}={value} exceeds maximum {param_def.max_value} {param_def.unit}"
                )

        return warnings


# ── Helper Functions for Formula Implementations ─────────────────
def make_symbolic_step(
    description: str,
    expr: sp.Expr,
    variables: dict[str, str] | None = None,
) -> dict:
    """Create a symbolic step (showing the formula)."""
    return {
        "type": "symbolic",
        "description": description,
        "latex": latex(expr),
        "variables": variables or {},
    }


def make_substitution_step(
    description: str,
    latex_str: str,
    variables: dict[str, str],
) -> dict:
    """Create a substitution step (showing values plugged in)."""
    return {
        "type": "substitution",
        "description": description,
        "latex": latex_str,
        "variables": variables,
    }


def make_result_step(
    description: str,
    symbol: str,
    value: float,
    unit: str,
) -> dict:
    """Create a result step (showing final answer)."""
    return {
        "type": "result",
        "description": description,
        "latex": f"{symbol} = {value:.6g} \\; \\text{{{unit}}}",
        "variables": {symbol: f"{value:.6g} {unit}"},
    }


# ── Singleton Engine ─────────────────────────────────────────────
calc_engine = CalculationEngine()
