"""
Troy — Calculation Service
Business logic layer that orchestrates the calculation engine,
formula registry, validation, and persistence.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.calculations.engine import calc_engine, CalculationResult
from app.calculations.registry import registry, FormulaDefinition
from app.calculations.validator import validate_calculation_inputs
from app.calculations.schemas import (
    CalculationRequest,
    CalculationResponse,
    FormulaResponse,
    FormulaListResponse,
    ParameterInfo,
    OutputInfo,
    StepResponse,
)
from app.core.logging import get_logger

logger = get_logger("calc_service")


# ── Formula Conversion ───────────────────────────────────────────
def formula_def_to_response(f: FormulaDefinition) -> FormulaResponse:
    """Convert a FormulaDefinition to an API response model."""
    return FormulaResponse(
        id=f.id,
        domain=f.domain,
        category=f.category,
        name=f.name,
        description=f.description,
        formula_latex=f.formula_latex,
        parameters=[
            ParameterInfo(
                name=p.name,
                symbol=p.symbol,
                unit=p.unit,
                description=p.description,
                min_value=p.min_value,
                max_value=p.max_value,
                default=p.default,
            )
            for p in f.parameters
        ],
        outputs=[
            OutputInfo(
                name=o.name,
                symbol=o.symbol,
                unit=o.unit,
                description=o.description,
            )
            for o in f.outputs
        ],
        reference=f.reference,
        tags=f.tags,
    )


# ── Service Functions ────────────────────────────────────────────
async def execute_calculation(
    request: CalculationRequest,
    db: AsyncSession,
) -> CalculationResponse:
    """
    Execute a calculation and persist the result.

    Flow:
    1. Look up formula definition
    2. Validate inputs
    3. Run calculation engine
    4. Persist to database
    5. Return response
    """
    # Look up formula
    formula_def = registry.get(request.formula_id)
    if formula_def is None:
        return CalculationResponse(
            id=str(uuid.uuid4()),
            formula_id=request.formula_id,
            title="Unknown Formula",
            steps=[],
            results={},
            results_formatted={},
            latex_summary="",
            execution_time_ms=0,
            error=f"Formula '{request.formula_id}' not found. "
                  f"Available: {', '.join(f.id for f in registry.list_all()[:10])}",
        )

    # Validate inputs
    validation = validate_calculation_inputs(formula_def, request.parameters)
    if not validation.is_valid:
        return CalculationResponse(
            id=str(uuid.uuid4()),
            formula_id=request.formula_id,
            title=formula_def.name,
            formula=formula_def_to_response(formula_def),
            steps=[],
            results={},
            results_formatted={},
            latex_summary="",
            execution_time_ms=0,
            warnings=validation.warnings,
            error="Validation failed: " + "; ".join(validation.errors),
        )

    # Execute calculation
    result: CalculationResult = calc_engine.execute(
        formula_id=request.formula_id,
        parameters=validation.sanitized_params,
    )

    # Convert steps
    steps = [
        StepResponse(
            order=s.order,
            step_type=s.step_type,
            description=s.description,
            latex=s.latex_expression,
            variables=s.variables,
        )
        for s in result.steps
    ]

    # Persist to database
    calc_id = result.id
    try:
        await db.execute(
            text("""
                INSERT INTO calculations (id, project_id, domain, formula_id, title,
                    inputs_json, outputs_json, units_json, execution_time_ms, status, error_message)
                VALUES (:id, :project_id, :domain, :formula_id, :title,
                    :inputs, :outputs, :units, :exec_time, :status, :error)
            """),
            {
                "id": calc_id,
                "project_id": request.project_id or "default",
                "domain": formula_def.domain,
                "formula_id": request.formula_id,
                "title": result.title,
                "inputs": json.dumps(request.parameters),
                "outputs": json.dumps(result.results),
                "units": json.dumps({"system": request.unit_system}),
                "exec_time": result.execution_time_ms,
                "status": "error" if result.error else "completed",
                "error": result.error,
            },
        )

        # Persist steps
        for step in result.steps:
            await db.execute(
                text("""
                    INSERT INTO calculation_steps (id, calculation_id, step_order,
                        step_type, description, latex_expression, variables_json)
                    VALUES (:id, :calc_id, :order, :type, :desc, :latex, :vars)
                """),
                {
                    "id": str(uuid.uuid4()),
                    "calc_id": calc_id,
                    "order": step.order,
                    "type": step.step_type,
                    "desc": step.description,
                    "latex": step.latex_expression,
                    "vars": json.dumps(step.variables),
                },
            )

        await db.commit()
    except Exception as e:
        logger.warning(f"Failed to persist calculation: {e}")
        # Don't fail the calculation if persistence fails

    # Combine validation + engine warnings
    all_warnings = validation.warnings + result.warnings

    return CalculationResponse(
        id=calc_id,
        formula_id=request.formula_id,
        title=result.title,
        formula=formula_def_to_response(formula_def),
        steps=steps,
        results=result.results,
        results_formatted=result.results_formatted,
        latex_summary=result.latex_summary,
        execution_time_ms=result.execution_time_ms,
        warnings=all_warnings,
        error=result.error,
    )


async def get_formulas(
    domain: str | None = None,
    category: str | None = None,
    search: str | None = None,
) -> FormulaListResponse:
    """List formulas with optional filtering."""
    if search:
        formulas = registry.search(search)
    elif domain and category:
        formulas = registry.list_by_category(domain, category)
    elif domain:
        formulas = registry.list_by_domain(domain)
    else:
        formulas = registry.list_all()

    return FormulaListResponse(
        formulas=[formula_def_to_response(f) for f in formulas],
        total=len(formulas),
        domains=registry.get_domains(),
    )


async def get_formula_detail(formula_id: str) -> FormulaResponse | None:
    """Get detailed formula information."""
    formula_def = registry.get(formula_id)
    if formula_def is None:
        return None
    return formula_def_to_response(formula_def)
