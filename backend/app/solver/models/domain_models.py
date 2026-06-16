"""
Troy — Solver Domain Models
Pydantic schemas representing the state objects passed through the
Engineering Solver & Reasoning Engine pipeline.

These models are NOT database models — they are in-memory state
representations used by services and the orchestrator.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── Requirements ─────────────────────────────────────────────────
class RequirementData(BaseModel):
    """Structured engineering requirements extracted from natural language."""

    project_type: str = "general"
    mission_type: str = "general"
    payload: Optional[str] = None
    flight_time: Optional[str] = None
    environment: str = "Unknown"
    safety_factor: Optional[str] = None
    missing_requirements: List[str] = Field(default_factory=list)
    raw_extracted: Dict[str, Any] = Field(default_factory=dict)


# ── Assumptions ──────────────────────────────────────────────────
class AssumptionData(BaseModel):
    """A single engineering assumption with confidence and override capability."""

    missing_information: str
    assumption: str
    reasoning: str
    confidence_score: str = "Medium"
    editable: bool = True
    user_override: Optional[str] = None


# ── Constraints ──────────────────────────────────────────────────
class ConstraintData(BaseModel):
    """An engineering constraint identified for the problem domain."""

    category: str          # e.g., "Weight limits", "Thermal limits"
    limit: str             # e.g., "MTOW <= 7.00 kg"
    source: str            # e.g., "Derived from Payload-to-MTOW ratio"


# ── Variables ────────────────────────────────────────────────────
class VariableData(BaseModel):
    """Collection of known, unknown, derived, and constant variables."""

    known: Dict[str, Any] = Field(default_factory=dict)
    unknown: List[str] = Field(default_factory=list)
    dependent: List[str] = Field(default_factory=list)
    derived: Dict[str, Any] = Field(default_factory=dict)
    constants: Dict[str, Any] = Field(default_factory=dict)


# ── Formula Selection ────────────────────────────────────────────
class FormulaSelectionData(BaseModel):
    """A formula selected from the Day 5 registry with scoring metadata."""

    formula_id: str
    name: str = ""
    relevance_score: float = 0.0
    reasoning: str = ""
    required_inputs: List[str] = Field(default_factory=list)
    expected_outputs: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)


# ── Verification ─────────────────────────────────────────────────
class VerificationData(BaseModel):
    """Results of constraint verification against calculation outputs."""

    is_valid: bool = True
    warnings: List[str] = Field(default_factory=list)
    checks_passed: int = 0
    checks_failed: int = 0


# ── Interpretation ───────────────────────────────────────────────
class InterpretationData(BaseModel):
    """Human-readable engineering interpretation of calculation results."""

    interpretation: str


# ── Recommendations ──────────────────────────────────────────────
class RecommendationItem(BaseModel):
    """A single actionable engineering recommendation."""

    recommendation: str
    reasoning: str
    expected_benefits: Optional[str] = None
    potential_risks: Optional[str] = None


class RecommendationData(BaseModel):
    """Collection of recommendations with overall reasoning."""

    recommendations: List[RecommendationItem] = Field(default_factory=list)
    reasoning: str = ""


# ── Design Review ────────────────────────────────────────────────
class DesignReviewData(BaseModel):
    """Results of automated design review checks."""

    missing_requirements: List[str] = Field(default_factory=list)
    dangerous_assumptions: List[str] = Field(default_factory=list)
    low_safety_margins: List[str] = Field(default_factory=list)
    unrealistic_values: List[str] = Field(default_factory=list)
    design_weaknesses: List[str] = Field(default_factory=list)
    overall_assessment: str = ""


# ── Solver State (Pipeline Carrier) ──────────────────────────────
class SolverState(BaseModel):
    """
    Central state object threaded through the entire solver pipeline.

    Every service reads from and writes to this state, making the
    pipeline fully traceable and serialisable.
    """

    session_id: str
    project_id: str
    user_query: str
    domain: str = "multi"

    # Pipeline stages
    requirements: RequirementData = Field(default_factory=RequirementData)
    assumptions: List[AssumptionData] = Field(default_factory=list)
    constraints: List[ConstraintData] = Field(default_factory=list)
    variables: VariableData = Field(default_factory=VariableData)
    selected_formulas: List[FormulaSelectionData] = Field(default_factory=list)

    # Calculation Core results
    calculation_results: Dict[str, Any] = Field(default_factory=dict)

    # Post-calculation
    verification: VerificationData = Field(default_factory=VerificationData)
    interpretation: InterpretationData = Field(
        default_factory=lambda: InterpretationData(interpretation="")
    )
    recommendations: RecommendationData = Field(
        default_factory=lambda: RecommendationData(recommendations=[], reasoning="")
    )
    design_review: DesignReviewData = Field(default_factory=DesignReviewData)

    # Documentation
    generated_report_id: Optional[str] = None

    # Telemetry
    step_latencies_ms: Dict[str, float] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
