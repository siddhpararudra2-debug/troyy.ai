"""
Engineering OS Routes
"""
from fastapi import APIRouter
from app.engineering_os.schemas.schemas import (
    EngineeringProjectRequest,
    EngineeringProjectResponse,
    WorkflowExecutionRequest,
    WorkflowExecutionResponse,
)
from app.engineering_os.services.engineering_assistant import EngineeringAssistant
from app.engineering_os.services.project_workspace import ProjectWorkspace
from app.engineering_os.services.workflow_orchestrator import WorkflowOrchestrator


router = APIRouter(prefix="/engineering-os", tags=["Engineering OS"])
assistant = EngineeringAssistant()
workspace = ProjectWorkspace()
orchestrator = WorkflowOrchestrator()


@router.post("/projects", response_model=EngineeringProjectResponse)
async def create_engineering_project(request: EngineeringProjectRequest):
    result = workspace.create_project(request.name, request.description, request.domain)
    return EngineeringProjectResponse(**result)


@router.post("/workflows", response_model=WorkflowExecutionResponse)
async def execute_workflow(request: WorkflowExecutionRequest):
    result = orchestrator.execute_workflow(
        request.project_id,
        request.requirement,
        request.workflow
    )
    return WorkflowExecutionResponse(**result)
