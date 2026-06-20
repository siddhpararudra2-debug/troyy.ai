"""
Compliance Platform API Routes
"""
from fastapi import APIRouter
from app.compliance.schemas.schemas import (
    StandardRequest,
    StandardResponse,
    RegulationRequest,
    RegulationResponse,
    ComplianceCheckRequest,
    ComplianceCheckResponse,
    CertificationPlanRequest,
    CertificationPlanResponse,
    SafetyAnalysisRequest,
    SafetyAnalysisResponse,
    AuditRequest,
    AuditResponse,
    EvidenceRequest,
    EvidenceResponse,
    ComplianceReportRequest,
    ComplianceReportResponse
)
from app.compliance.services.standards_service import StandardsService
from app.compliance.services.regulations_service import RegulationsService
from app.compliance.services.compliance_engine import ComplianceEngineService
from app.compliance.services.certification_service import CertificationService
from app.compliance.services.safety_analysis_service import SafetyAnalysisService
from app.compliance.services.audit_service import AuditService
from app.compliance.services.evidence_tracking_service import EvidenceTrackingService
from app.compliance.services.compliance_report_service import ComplianceReportService


router = APIRouter(prefix="/compliance", tags=["Standards, Regulations & Compliance Platform"])


@router.post("/standards", response_model=StandardResponse)
async def create_standard(request: StandardRequest):
    return StandardsService.create_standard(request)


@router.post("/regulations", response_model=RegulationResponse)
async def create_regulation(request: RegulationRequest):
    return RegulationsService.create_regulation(request)


@router.post("/check", response_model=ComplianceCheckResponse)
async def check_compliance(request: ComplianceCheckRequest):
    return ComplianceEngineService.check_compliance(request)


@router.post("/certification", response_model=CertificationPlanResponse)
async def create_certification_plan(request: CertificationPlanRequest):
    return CertificationService.create_certification_plan(request)


@router.post("/safety", response_model=SafetyAnalysisResponse)
async def perform_safety_analysis(request: SafetyAnalysisRequest):
    return SafetyAnalysisService.analyze(request)


@router.post("/audit", response_model=AuditResponse)
async def create_audit(request: AuditRequest):
    return AuditService.create_audit(request)


@router.post("/evidence", response_model=EvidenceResponse)
async def add_evidence(request: EvidenceRequest):
    return EvidenceTrackingService.add_evidence(request)


@router.post("/report", response_model=ComplianceReportResponse)
async def generate_report(request: ComplianceReportRequest):
    return ComplianceReportService.generate_report(request)
