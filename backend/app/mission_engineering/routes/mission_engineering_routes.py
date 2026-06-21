"""
Mission Engineering Routes
"""
from fastapi import APIRouter
from app.mission_engineering.schemas.schemas import (
    MissionProjectRequest,
    MissionProjectResponse,
    MissionPlanRequest,
    MissionPlanResponse,
    MissionValidationRequest,
    MissionValidationResponse,
    MissionRiskRequest,
    MissionRiskResponse,
)
from app.mission_engineering.services.mission_orchestrator import MissionOrchestrator
from app.mission_engineering.services.mission_planner import MissionPlanner
from app.mission_engineering.services.mission_validator import MissionValidator
from app.mission_engineering.services.mission_risk_engine import MissionRiskEngine

router = APIRouter(prefix="/mission-engineering", tags=["Mission Engineering"])
orchestrator = MissionOrchestrator()
planner = MissionPlanner()
validator = MissionValidator()
risk_engine = MissionRiskEngine()


@router.post("/projects", response_model=MissionProjectResponse)
async def create_mission_project(request: MissionProjectRequest):
    result = orchestrator.create_mission_project(
        project_id=request.project_id,
        name=request.name,
        mission_type=request.mission_type,
        requirements=request.requirements
    )
    return MissionProjectResponse(**result)


@router.post("/plans", response_model=MissionPlanResponse)
async def create_mission_plan(request: MissionPlanRequest):
    result = planner.plan_mission(request.mission_project_id)
    return MissionPlanResponse(**result)


@router.post("/validate", response_model=MissionValidationResponse)
async def validate_mission(request: MissionValidationRequest):
    result = validator.validate_mission(request.mission_project_id)
    return MissionValidationResponse(**result)


@router.post("/risks", response_model=MissionRiskResponse)
async def analyze_mission_risks(request: MissionRiskRequest):
    result = risk_engine.analyze_risks(request.mission_project_id)
    return MissionRiskResponse(**result)
