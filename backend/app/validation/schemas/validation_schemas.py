"""
Troy — Validation Pydantic Schemas
Defines request and response serialization schemas for the validation router.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ValidationIssueSchema(BaseModel):
    id: Optional[str] = None
    severity: str  # "error", "warning", "info"
    category: str  # "Requirements", "Assumptions", "Formulas", etc.
    message: str
    validator_name: str
    engineering_reasoning: Optional[str] = None
    recommendation: Optional[str] = None


class ValidationReportResponse(BaseModel):
    id: str
    project_id: str
    solver_run_id: Optional[str] = None
    domain: str
    total_errors: int
    total_warnings: int
    is_approved: bool
    execution_time_ms: Optional[float] = None
    created_at: str
    issues: List[ValidationIssueSchema] = Field(default_factory=list)


class EngineeringReviewResponse(BaseModel):
    id: str
    run_id: str
    design_decisions_check: str
    component_choices_check: str
    structural_choices_check: str
    electrical_choices_check: str
    weight_budgets_check: str
    power_budgets_check: str
    thermal_assumptions_check: str
    overall_assessment: str
    created_at: str


class RiskItem(BaseModel):
    description: str
    cause: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    probability: str  # LOW, MEDIUM, HIGH
    impact: str  # LOW, MEDIUM, HIGH, CATASTROPHIC
    recommended_fix: str


class RiskAssessmentResponse(BaseModel):
    id: str
    run_id: str
    overall_risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    risks: List[RiskItem] = Field(default_factory=list)
    created_at: str


class ApprovalDecisionResponse(BaseModel):
    id: str
    run_id: str
    status: str  # APPROVED, APPROVED WITH CONCERNS, REQUIRES REVISION, REJECTED
    engineering_reasoning: str
    risk_summary: str
    validation_summary: str
    created_at: str


class AuditReportResponse(BaseModel):
    id: str
    run_id: str
    report_type: str
    format: str  # "markdown", "html", "json", "pdf"
    content: str
    created_at: str


class AuditLogResponse(BaseModel):
    id: str
    project_id: str
    action: str
    user_id: Optional[str] = None
    details: Optional[str] = None
    created_at: str


class ValidateRequest(BaseModel):
    project_id: str
    solver_run_id: Optional[str] = None
    solver_state_dict: Optional[Dict[str, Any]] = None
