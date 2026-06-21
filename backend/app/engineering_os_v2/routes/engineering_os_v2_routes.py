"""
Engineering OS V2 Routes
"""
from fastapi import APIRouter
from app.engineering_os_v2.schemas.schemas import (
    EnterpriseProjectRequest,
    EnterpriseProjectResponse,
    EnterpriseDashboardResponse,
    PortfolioResponse,
    AgentsResponse,
    CommandCenterStatus,
    ExecutiveReportRequest,
    ExecutiveReportResponse,
    WorkspaceRequest,
    WorkspaceResponse,
    RuntimeExecutionRequest,
    RuntimeExecutionResponse,
)
from app.engineering_os_v2.services.enterprise_orchestrator import EnterpriseOrchestrator
from app.engineering_os_v2.services.enterprise_dashboard import EnterpriseDashboard
from app.engineering_os_v2.services.portfolio_manager import PortfolioManager
from app.engineering_os_v2.services.global_agent_manager import GlobalAgentManager
from app.engineering_os_v2.services.engineering_command_center import EngineeringCommandCenter
from app.engineering_os_v2.services.executive_reporting_service import ExecutiveReportingService
from app.engineering_os_v2.services.engineering_workspace import EngineeringWorkspace
from app.engineering_os_v2.services.engineering_runtime import EngineeringRuntime

router = APIRouter(prefix="/engineering-os-v2", tags=["Engineering OS V2"])
orchestrator = EnterpriseOrchestrator()
dashboard = EnterpriseDashboard()
portfolio_manager = PortfolioManager()
agent_manager = GlobalAgentManager()
command_center = EngineeringCommandCenter()
reporting_service = ExecutiveReportingService()
workspace = EngineeringWorkspace()
runtime = EngineeringRuntime()


@router.post("/projects", response_model=EnterpriseProjectResponse)
async def create_enterprise_project(request: EnterpriseProjectRequest):
    result = orchestrator.create_project(
        name=request.name,
        mission_requirements=request.mission_requirements
    )
    return EnterpriseProjectResponse(**result)


@router.get("/dashboard", response_model=EnterpriseDashboardResponse)
async def get_dashboard():
    result = dashboard.get_dashboard()
    return EnterpriseDashboardResponse(**result)


@router.get("/portfolio", response_model=PortfolioResponse)
async def get_portfolio():
    result = portfolio_manager.get_portfolio()
    return PortfolioResponse(**result)


@router.get("/agents", response_model=AgentsResponse)
async def get_agents():
    result = agent_manager.get_agents()
    return AgentsResponse(**result)


@router.get("/command-center", response_model=CommandCenterStatus)
async def get_command_center_status():
    result = command_center.get_command_status()
    return CommandCenterStatus(**result)


@router.post("/reports", response_model=ExecutiveReportResponse)
async def generate_executive_report(request: ExecutiveReportRequest):
    result = reporting_service.generate_report(report_type=request.report_type)
    return ExecutiveReportResponse(**result)


@router.post("/workspace", response_model=WorkspaceResponse)
async def get_workspace(request: WorkspaceRequest):
    result = workspace.get_workspace(project_id=request.project_id)
    return WorkspaceResponse(**result)


@router.post("/runtime/execute", response_model=RuntimeExecutionResponse)
async def execute_runtime_workflow(request: RuntimeExecutionRequest):
    result = runtime.execute(project_id=request.project_id, workflow=request.workflow)
    return RuntimeExecutionResponse(**result)
