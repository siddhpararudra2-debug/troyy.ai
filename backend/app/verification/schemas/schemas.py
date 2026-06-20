"""
Verification Platform Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class BaseVerificationRequest(BaseModel):
    project_id: Optional[str] = None


class VerificationPlanRequest(BaseVerificationRequest):
    verification_type: str
    objectives: List[str] = Field(default_factory=list)


class VerificationActivity(BaseModel):
    id: str
    name: str
    description: str
    method: str


class VerificationPlanResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    verification_type: str
    activities: List[VerificationActivity]
    created_at: datetime


class TestCaseRequest(BaseVerificationRequest):
    __test__ = False
    test_type: str
    name: str
    description: Optional[str] = None


class TestCaseResponse(BaseModel):
    __test__ = False
    id: str
    project_id: Optional[str] = None
    test_type: str
    name: str
    description: Optional[str] = None
    steps: List[str] = Field(default_factory=list)
    created_at: datetime


class TestExecutionRequest(BaseVerificationRequest):
    __test__ = False
    test_case_ids: List[str]


class TestExecutionResult(BaseModel):
    __test__ = False
    test_case_id: str
    status: str  # pass/fail/blocked/in_progress
    duration_sec: Optional[float] = None
    notes: Optional[str] = None


class TestExecutionResponse(BaseModel):
    __test__ = False
    id: str
    project_id: Optional[str] = None
    results: List[TestExecutionResult]
    created_at: datetime


class SILRequest(BaseVerificationRequest):
    firmware_id: str
    simulation_model_id: str


class SILResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    status: str
    results: Dict[str, Any]
    execution_time_sec: Optional[float] = None
    created_at: datetime


class HILRequest(BaseVerificationRequest):
    hardware_id: str
    simulation_model_id: str


class HILResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    status: str
    results: Dict[str, Any]
    created_at: datetime


class CoverageRequest(BaseVerificationRequest):
    coverage_type: str


class CoverageMetric(BaseModel):
    metric_name: str
    percentage: float


class CoverageResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    coverage_type: str
    metrics: List[CoverageMetric]
    gaps: List[str] = Field(default_factory=list)
    created_at: datetime


class AcceptanceCriteriaRequest(BaseVerificationRequest):
    system_type: str


class AcceptanceCriterion(BaseModel):
    id: str
    name: str
    description: str
    target_value: Optional[str] = None


class AcceptanceCriteriaResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    system_type: str
    criteria: List[AcceptanceCriterion]
    created_at: datetime


class VerificationMatrixRequest(BaseVerificationRequest):
    pass


class MatrixRow(BaseModel):
    requirement_id: str
    test_case_ids: List[str]
    execution_result: Optional[str] = None
    evidence_id: Optional[str] = None
    approval_status: Optional[str] = None


class VerificationMatrixResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    rows: List[MatrixRow]
    created_at: datetime


class VerificationReportRequest(BaseVerificationRequest):
    report_type: str


class VerificationReportResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    report_type: str
    content: str
    sections: List[str] = Field(default_factory=list)
    created_at: datetime
