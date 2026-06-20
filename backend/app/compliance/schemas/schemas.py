"""
Compliance Platform Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class BaseComplianceRequest(BaseModel):
    project_id: Optional[str] = None


class StandardRequest(BaseComplianceRequest):
    standard_type: str
    name: str
    code: str
    description: Optional[str] = None


class StandardResponse(BaseModel):
    id: str
    standard_type: str
    name: str
    code: str
    description: Optional[str] = None
    requirements_json: Optional[str] = None
    created_at: datetime


class RegulationRequest(BaseComplianceRequest):
    regulation_type: str
    name: str
    jurisdiction: str
    description: Optional[str] = None


class RegulationResponse(BaseModel):
    id: str
    regulation_type: str
    name: str
    jurisdiction: str
    description: Optional[str] = None
    created_at: datetime


class ComplianceCheckRequest(BaseComplianceRequest):
    check_type: str
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ComplianceIssue(BaseModel):
    severity: str
    description: str
    requirement: str
    evidence: Optional[str] = None


class ComplianceCheckResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    overall_status: str
    compliance_score: float
    issues: List[ComplianceIssue]
    execution_time_ms: Optional[float] = None
    created_at: datetime


class CertificationPlanRequest(BaseComplianceRequest):
    certification_type: str
    requirements: List[str] = Field(default_factory=list)


class CertificationTask(BaseModel):
    id: str
    title: str
    description: str
    required_evidence: List[str] = Field(default_factory=list)


class CertificationPlanResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    certification_type: str
    tasks: List[CertificationTask]
    timeline: Optional[Dict[str, Any]] = None
    created_at: datetime


class SafetyAnalysisRequest(BaseComplianceRequest):
    analysis_type: str
    system_name: Optional[str] = None


class SafetyHazard(BaseModel):
    id: str
    name: str
    description: str
    severity: str
    likelihood: str
    risk_level: str
    mitigation: str


class SafetyAnalysisResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    analysis_type: str
    hazards: List[SafetyHazard]
    risk_register_json: Optional[str] = None
    execution_time_ms: Optional[float] = None
    created_at: datetime


class AuditRequest(BaseComplianceRequest):
    audit_type: str
    auditor: Optional[str] = None


class AuditFinding(BaseModel):
    finding_id: str
    severity: str
    description: str
    status: str
    corrective_action: Optional[str] = None


class AuditResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    audit_type: str
    auditor: Optional[str] = None
    findings: List[AuditFinding]
    overall_result: str
    created_at: datetime


class EvidenceRequest(BaseComplianceRequest):
    requirement_id: str
    evidence_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class EvidenceResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    requirement_id: str
    evidence_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime


class ComplianceReportRequest(BaseComplianceRequest):
    report_type: str


class ComplianceReportResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    report_type: str
    content: str
    sections: List[str] = Field(default_factory=list)
    created_at: datetime
