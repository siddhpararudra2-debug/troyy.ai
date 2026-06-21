"""
Business Operations Routes
"""
from fastapi import APIRouter
from app.business_operations.schemas.schemas import (
    OpportunityRequest,
    OpportunityResponse,
    ProposalRequest,
    ProposalResponse,
    ExecutiveDashboardResponse
)
from app.business_operations.services.opportunity_analysis_service import OpportunityAnalysisService
from app.business_operations.services.proposal_generator import ProposalGenerator
from app.business_operations.services.executive_dashboard import ExecutiveDashboard

router = APIRouter(prefix="/business", tags=["Business Operations"])

opportunity_service = OpportunityAnalysisService()
proposal_service = ProposalGenerator()
dashboard_service = ExecutiveDashboard()


@router.post("/opportunity", response_model=OpportunityResponse)
async def create_opportunity(request: OpportunityRequest):
    result = opportunity_service.analyze_opportunity(request.dict())
    return OpportunityResponse(**result)


@router.post("/proposal", response_model=ProposalResponse)
async def generate_proposal(request: ProposalRequest):
    result = proposal_service.generate_proposal(request.project_id, request.requirements)
    return ProposalResponse(**result)


@router.get("/dashboard", response_model=ExecutiveDashboardResponse)
async def get_executive_dashboard():
    result = dashboard_service.get_dashboard_metrics()
    return ExecutiveDashboardResponse(**result)
