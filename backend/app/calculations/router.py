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
)
from app.calculations.units import convert_unit, get_unit_systems
from app.core.dependencies import DbSession

router = APIRouter(tags=["calculations"])


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
