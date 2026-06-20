"""
Verification Platform API Routes
"""
from fastapi import APIRouter
from app.verification.schemas.schemas import (
    VerificationPlanRequest,
    VerificationPlanResponse,
    TestCaseRequest,
    TestCaseResponse,
    TestExecutionRequest,
    TestExecutionResponse,
    SILRequest,
    SILResponse,
    HILRequest,
    HILResponse,
    CoverageRequest,
    CoverageResponse,
    AcceptanceCriteriaRequest,
    AcceptanceCriteriaResponse,
    VerificationMatrixRequest,
    VerificationMatrixResponse,
    VerificationReportRequest,
    VerificationReportResponse
)
from app.verification.services.verification_planning_service import VerificationPlanningService
from app.verification.services.test_generation_service import TestGenerationService
from app.verification.services.test_execution_service import TestExecutionService
from app.verification.services.sil_service import SILService
from app.verification.services.hil_service import HILService
from app.verification.services.coverage_analysis_service import CoverageAnalysisService
from app.verification.services.verification_matrix_service import VerificationMatrixService
from app.verification.services.verification_report_service import VerificationReportService
from app.verification.services.acceptance_criteria_service import AcceptanceCriteriaService


router = APIRouter(prefix="/verification", tags=["Testing, Verification & Hardware-In-The-Loop Platform"])


@router.post("/plan", response_model=VerificationPlanResponse)
async def create_verification_plan(request: VerificationPlanRequest):
    return VerificationPlanningService.create_plan(request)


@router.post("/tests", response_model=TestCaseResponse)
async def generate_test_case(request: TestCaseRequest):
    return TestGenerationService.generate_test_case(request)


@router.post("/execute", response_model=TestExecutionResponse)
async def execute_tests(request: TestExecutionRequest):
    return TestExecutionService.execute_tests(request)


@router.post("/sil", response_model=SILResponse)
async def run_sil(request: SILRequest):
    return SILService.run_sil(request)


@router.post("/hil", response_model=HILResponse)
async def run_hil(request: HILRequest):
    return HILService.run_hil(request)


@router.post("/coverage", response_model=CoverageResponse)
async def analyze_coverage(request: CoverageRequest):
    return CoverageAnalysisService.analyze_coverage(request)


@router.post("/matrix", response_model=VerificationMatrixResponse)
async def generate_verification_matrix(request: VerificationMatrixRequest):
    return VerificationMatrixService.generate_matrix(request)


@router.post("/report", response_model=VerificationReportResponse)
async def generate_verification_report(request: VerificationReportRequest):
    return VerificationReportService.generate_report(request)


@router.post("/acceptance", response_model=AcceptanceCriteriaResponse)
async def generate_acceptance_criteria(request: AcceptanceCriteriaRequest):
    return AcceptanceCriteriaService.generate_criteria(request)
