from fastapi import APIRouter
from review_council.services.design_review_service import DesignReviewService
from review_council.services.chief_engineer_agent import ChiefEngineerAgent
from review_council.schemas.review_models import ReviewCategory, ReviewReport

router = APIRouter(prefix="/review-council", tags=["Engineering Review Council"])

chief = ChiefEngineerAgent()

@router.post("/structural")
async def structural_review(project_id: str, design_data: dict):
    svc = DesignReviewService("Structural Reviewer", ReviewCategory.STRUCTURAL)
    return svc.review_design(project_id, design_data)

@router.post("/thermal")
async def thermal_review(project_id: str, design_data: dict):
    svc = DesignReviewService("Thermal Reviewer", ReviewCategory.THERMAL)
    return svc.review_design(project_id, design_data)

@router.post("/safety")
async def safety_review(project_id: str, design_data: dict):
    svc = DesignReviewService("Safety Reviewer", ReviewCategory.SAFETY)
    return svc.review_design(project_id, design_data)

@router.post("/arbitrate")
async def arbitrate(project_id: str, review_reports: list):
    reports = [ReviewReport(**r) for r in review_reports]
    decision = chief.arbitrate(project_id, reports)
    return decision.dict()
