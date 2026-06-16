"""
Troy — Solver API Schemas
Pydantic models for requests and responses of the Engineering Solver endpoints.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.solver.models.domain_models import (
    AssumptionData,
    ConstraintData,
    InterpretationData,
    RecommendationData,
    RequirementData,
    VariableData,
)


class SolverRequest(BaseModel):
    """Request to solve an engineering problem."""
    project_id: str = Field(..., description="Project ID to associate with this session")
    user_query: str = Field(..., description="Unstructured engineering query in natural language")


class SolverResponse(BaseModel):
    """Response of the full solver pipeline execution."""
    session_id: str
    project_id: str
    status: str
    state: Dict[str, Any]


# ── Requirements Endpoints ───────────────────────────────────────
class RequirementsRequest(BaseModel):
    user_query: str


# ── Assumptions Endpoints ────────────────────────────────────────
class AssumptionsRequest(BaseModel):
    domain: str
    requirements: RequirementData


# ── Constraints Endpoints ────────────────────────────────────────
class ConstraintsRequest(BaseModel):
    domain: str
    requirements: RequirementData
    assumptions: List[AssumptionData]


# ── Variables Endpoints ──────────────────────────────────────────
class VariablesRequest(BaseModel):
    domain: str
    requirements: RequirementData
    assumptions: List[AssumptionData]


# ── Recommendations Endpoints ────────────────────────────────────
class RecommendationsRequest(BaseModel):
    domain: str
    calculation_results: Dict[str, Any]
    constraints: List[ConstraintData]


# ── Interpretation Endpoints ─────────────────────────────────────
class InterpretationRequest(BaseModel):
    domain: str
    calculation_results: Dict[str, Any]
    constraints: List[ConstraintData]
