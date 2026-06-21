"""
Safety Engineering Routes
"""
from fastapi import APIRouter
from app.safety_engineering.schemas.schemas import SafetyAnalysisRequest, SafetyAnalysisResponse
from app.safety_engineering.services.safety_orchestrator import SafetyOrchestrator

router = APIRouter(prefix="/safety", tags=["Safety Engineering"])
safety_orchestrator = SafetyOrchestrator()


@router.post("/analysis", response_model=SafetyAnalysisResponse)
async def run_analysis(request: SafetyAnalysisRequest):
    result = safety_orchestrator.run_safety_workflow(request.project_id, request.analysis_type)
    return SafetyAnalysisResponse(**result)
