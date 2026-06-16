"""
Troy — Calculation API Schemas
Pydantic models for calculation requests and responses.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Request Schemas ──────────────────────────────────────────────
class CalculationRequest(BaseModel):
    """Request to execute an engineering calculation."""
    project_id: str | None = Field(None, description="Optional project to associate with")
    formula_id: str = Field(..., description="Formula registry ID (e.g., 'aerospace.aerodynamics.lift_force')")
    parameters: dict[str, float] = Field(..., description="Parameter name → value mapping")
    unit_system: str = Field("SI", description="Unit system: SI | Imperial")


class UnitConversionRequest(BaseModel):
    """Request to convert between units."""
    value: float = Field(..., description="Numerical value to convert")
    from_unit: str = Field(..., description="Source unit (e.g., 'm/s', 'psi')")
    to_unit: str = Field(..., description="Target unit")


# ── Response Schemas ─────────────────────────────────────────────
class StepResponse(BaseModel):
    """A single calculation step."""
    order: int
    step_type: str
    description: str
    latex: str
    variables: dict[str, str] = {}


class ParameterInfo(BaseModel):
    """Parameter definition for formula discovery."""
    name: str
    symbol: str
    unit: str
    description: str
    min_value: float | None = None
    max_value: float | None = None
    default: float | None = None


class OutputInfo(BaseModel):
    """Output definition for formula discovery."""
    name: str
    symbol: str
    unit: str
    description: str


class FormulaResponse(BaseModel):
    """Formula definition for API responses."""
    id: str
    domain: str
    category: str
    name: str
    description: str
    formula_latex: str
    parameters: list[ParameterInfo]
    outputs: list[OutputInfo]
    reference: str = ""
    tags: list[str] = []


class CalculationResponse(BaseModel):
    """Complete calculation result with step-by-step breakdown."""
    id: str
    formula_id: str
    title: str
    formula: FormulaResponse | None = None
    steps: list[StepResponse]
    results: dict[str, float]
    results_formatted: dict[str, str]
    latex_summary: str
    execution_time_ms: float
    warnings: list[str] = []
    error: str | None = None


class UnitConversionResponse(BaseModel):
    """Unit conversion result."""
    original_value: float
    original_unit: str
    converted_value: float
    target_unit: str
    formula: str


class UnitSystemResponse(BaseModel):
    """Available unit systems."""
    systems: dict[str, dict[str, str]]


class FormulaListResponse(BaseModel):
    """List of formulas with metadata."""
    formulas: list[FormulaResponse]
    total: int
    domains: list[str]
