from fastapi import APIRouter
from verification.schemas.engineering_report import EngineeringReport
from verification.schemas.requests import VerificationPlanRequest, TestGenerationRequest, HILExecutionRequest
from verification.services.verification_planning_service import VerificationPlanningService
from verification.services.test_generation_service import TestGenerationService
from verification.services.sil_service import SILService
from verification.services.hil_service import HILService
from verification.services.coverage_analysis_service import CoverageAnalysisService
from verification.services.verification_matrix_service import VerificationMatrixService
from verification.services.verification_report_service import VerificationReportService

router = APIRouter(prefix="/verification", tags=["Testing, Verification & HIL Platform"])

plan_svc = VerificationPlanningService()
test_gen_svc = TestGenerationService()
sil_svc = SILService()
hil_svc = HILService()
cov_svc = CoverageAnalysisService()
matrix_svc = VerificationMatrixService()
report_svc = VerificationReportService()

@router.post("/plan", response_model=EngineeringReport)
async def generate_plan(req: VerificationPlanRequest):
    return plan_svc.generate_plan(req.requirements, req.target_dal)

@router.post("/generate-tests", response_model=EngineeringReport)
async def generate_tests(req: TestGenerationRequest):
    return test_gen_svc.generate_tests(req.requirements, req.coverage_target)

@router.post("/sil", response_model=EngineeringReport)
async def execute_sil(test_cases: list, model_ref: str, seed: int = 42):
    return sil_svc.execute_tests(test_cases, model_ref, seed)

@router.post("/hil", response_model=EngineeringReport)
async def execute_hil(req: HILExecutionRequest):
    return hil_svc.execute_hil(req.configuration, req.test_cases)

@router.post("/coverage", response_model=EngineeringReport)
async def analyze_coverage(test_results: list, target_dal: str):
    return cov_svc.analyze_coverage(test_results, target_dal)

@router.post("/matrix", response_model=EngineeringReport)
async def build_matrix(requirements: list, test_cases: list, test_results: list):
    return matrix_svc.build_matrix(requirements, test_cases, test_results)

@router.post("/certification-package", response_model=EngineeringReport)
async def generate_cert_package(plan: dict, matrix: dict, coverage: dict, test_results: list):
    return report_svc.generate_certification_package(plan, matrix, coverage, test_results)
