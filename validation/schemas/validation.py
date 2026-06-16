from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from validation.models.database import Severity, ApprovalStatus

class ValidationRequest(BaseModel):
    project_id: str
    solver_run_id: str
    domain: str = Field(..., description="AEROSPACE, UAV, ROBOTICS, ELECTRONICS")
    design_data: Dict[str, Any]
    assumptions: List[str]
    formulas_used: List[str]
    calculations: List[Dict[str, Any]]

class ValidationIssueSchema(BaseModel):
    module: str
    severity: Severity
    description: str
    engineering_reasoning: str
    recommendation: str

class ValidationResponse(BaseModel):
    run_id: int
    status: str
    issues: List[ValidationIssueSchema]
    execution_time_ms: float

class RiskAssessmentResponse(BaseModel):
    overall_risk_level: Severity
    risk_matrix: List[Dict[str, Any]]

class ApprovalResponse(BaseModel):
    status: ApprovalStatus
    engineering_reasoning: str
    risk_summary: str
    validation_summary: str

class AuditReportResponse(BaseModel):
    report_id: int
    format: str
    content: str
    generated_at: datetime
