"""
Troy — Calculation API Router
REST endpoints for calculations, formulas, and unit conversions.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.calculations import service
from app.calculations.schemas import (
    CalculationRequest,
    CalculationResponse,
    FormulaListResponse,
    FormulaResponse,
    UnitConversionRequest,
    UnitConversionResponse,
    UnitSystemResponse,
    ValidateRequest,
    ReasonRequest,
    DimensionalCheckRequest,
    PhysicsSolveRequest,
    MathSolveRequest,
    ValidationResponse,
    ReasoningResponse,
    DimensionalCheckResponse,
    PhysicsSolveResponse,
    ValidationIssueResponse,
)
from app.calculations.units import convert_unit, get_unit_systems
from app.units.dimensional_checker import DimensionalChecker
from app.validation.services.formula_validator import FormulaValidator
from app.validation.services.engineering_review import EngineeringReview, DesignOption
from app.physics_engine.mechanics import MechanicsEngine
from app.physics_engine.fluids import FluidEngine
from app.physics_engine.thermodynamics import ThermodynamicsEngine
from app.physics_engine.electromagnetics import ElectromagneticsEngine
from app.math_engine.symbolic_solver import SymbolicSolver
from app.math_engine.numerical_solver import NumericalSolver
from app.math_engine.matrix_engine import MatrixEngine
from app.math_engine.calculus_engine import CalculusEngine
from app.core.dependencies import DbSession

router = APIRouter(tags=["calculations", "sprint2"])

# Initialize engines
formula_validator = FormulaValidator()
dimensional_checker = DimensionalChecker()
engineering_review = EngineeringReview()

physics_engines = {
    "mechanics": MechanicsEngine(),
    "fluids": FluidEngine(),
    "thermodynamics": ThermodynamicsEngine(),
    "electromagnetics": ElectromagneticsEngine(),
}

math_engines = {
    "symbolic": SymbolicSolver(),
    "numerical": NumericalSolver(),
    "matrix": MatrixEngine(),
    "calculus": CalculusEngine(),
}


# ── Calculations ─────────────────────────────────────────────────
@router.post("/calculate", response_model=CalculationResponse)
async def execute_calculation(
    request: CalculationRequest,
    db: DbSession,
):
    """
    Execute an engineering calculation with step-by-step results.

    Provide a formula_id from the registry and parameter values.
    Returns symbolic → substitution → result steps with LaTeX rendering.
    """
    result = await service.execute_calculation(request, db)
    return result


# ── Formula Discovery ────────────────────────────────────────────
@router.get("/formulas", response_model=FormulaListResponse)
async def list_formulas(
    domain: str | None = Query(None, description="Filter by domain"),
    category: str | None = Query(None, description="Filter by category"),
    search: str | None = Query(None, description="Search query"),
):
    """
    List available engineering formulas.

    Optionally filter by domain (aerospace, drones, robotics, electronics)
    or search by name/description.
    """
    return await service.get_formulas(domain=domain, category=category, search=search)


@router.get("/formulas/{formula_id:path}", response_model=FormulaResponse)
async def get_formula(formula_id: str):
    """
    Get detailed information about a specific formula.

    Returns parameter definitions, valid ranges, LaTeX representation,
    and reference information.
    """
    result = await service.get_formula_detail(formula_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Formula '{formula_id}' not found")
    return result


# ── Unit Conversion ──────────────────────────────────────────────
@router.post("/units/convert", response_model=UnitConversionResponse)
async def convert_units(request: UnitConversionRequest):
    """
    Convert a value from one unit to another.

    Supports all standard engineering units via the Pint library.
    """
    try:
        result = convert_unit(request.value, request.from_unit, request.to_unit)
        return UnitConversionResponse(
            original_value=result.original_value,
            original_unit=result.original_unit,
            converted_value=result.converted_value,
            target_unit=result.target_unit,
            formula=result.formula,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/units/systems", response_model=UnitSystemResponse)
async def list_unit_systems():
    """List available unit systems (SI, Imperial) and their unit mappings."""
    return UnitSystemResponse(systems=get_unit_systems())


# ── Validation ───────────────────────────────────────────────────
@router.post("/validate", response_model=ValidationResponse)
async def validate_calculation(request: ValidateRequest):
    """Validate an engineering calculation"""
    val_result = formula_validator.validate_calculation(
        request.formula_id, request.parameters
    )
    return ValidationResponse(
        valid=val_result.valid,
        issues=[
            ValidationIssueResponse(
                severity=i.severity, message=i.message, field=i.field
            )
            for i in val_result.issues
        ],
        warnings=val_result.warnings,
    )


@router.post("/dimensional-check", response_model=DimensionalCheckResponse)
async def check_dimensions(request: DimensionalCheckRequest):
    """Check dimensional consistency"""
    check = dimensional_checker.check_dimensions(
        request.left_expr, request.right_expr, request.variables
    )
    return DimensionalCheckResponse(
        valid=check.valid,
        left_dimension=check.left_dimension,
        right_dimension=check.right_dimension,
        message=check.message,
    )


# ── Physics Engine ───────────────────────────────────────────────
@router.post("/physics/solve", response_model=PhysicsSolveResponse)
async def solve_physics(request: PhysicsSolveRequest):
    """Solve physics equations"""
    engine = physics_engines.get(request.domain)
    if engine is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown physics domain: {request.domain}",
        )
    method = getattr(engine, request.formula_name, None)
    if method is None or not callable(method):
        raise HTTPException(
            status_code=400,
            detail=f"Unknown formula: {request.formula_name}",
        )
    result = method(**request.parameters)
    return PhysicsSolveResponse(
        result=result,
        formula=result.get("formula", ""),
        units={k: v for k, v in result.items() if k == "units"},
    )


# ── Reasoning & Review ───────────────────────────────────────────
@router.post("/reason", response_model=ReasoningResponse)
async def reason(request: ReasonRequest):
    """Perform engineering trade-off analysis"""
    options = [
        DesignOption(
            name=opt["name"],
            description=opt.get("description", ""),
            metrics=opt.get("metrics", {}),
            risks=opt.get("risks", []),
            assumptions=opt.get("assumptions", []),
        )
        for opt in request.options
    ]
    recommendation = engineering_review.evaluate_options(options, request.criteria)
    return ReasoningResponse(
        recommended=recommendation.recommended.__dict__,
        alternatives=[alt.__dict__ for alt in recommendation.alternatives],
        rationale=recommendation.rationale,
        trade_offs=recommendation.trade_offs,
    )
