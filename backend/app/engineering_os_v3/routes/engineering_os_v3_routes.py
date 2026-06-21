"""
Engineering OS V3 Routes
"""
from fastapi import APIRouter
from app.engineering_os_v3.schemas.schemas import (
    ExecutionRequest,
    ExecutionResponse,
    ProjectStatusResponse,
    GlobalDashboardResponse
)
from app.engineering_os_v3.services.autonomous_execution_engine import AutonomousExecutionEngine
from app.engineering_os_v3.services.engineering_supervisor import EngineeringSupervisor
from app.engineering_os_v3.services.enterprise_control_center import EnterpriseControlCenter

router = APIRouter(prefix="/engineering-os", tags=["Engineering OS V3"])

execution_engine = AutonomousExecutionEngine()
supervisor = EngineeringSupervisor()
control_center = EnterpriseControlCenter()


@router.post("/execute", response_model=ExecutionResponse)
async def execute_project(request: ExecutionRequest):
    result = execution_engine.execute_project(request.requirement)
    return ExecutionResponse(**result)


@router.get("/project/{project_id}", response_model=ProjectStatusResponse)
async def get_project_status(project_id: str):
    result = supervisor.monitor_project(project_id)
    return ProjectStatusResponse(**result)


@router.get("/dashboard", response_model=GlobalDashboardResponse)
async def get_global_dashboard():
    result = control_center.get_control_center_status()
    return GlobalDashboardResponse(**result)
