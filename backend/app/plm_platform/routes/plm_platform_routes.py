"""
PLM Platform Routes
"""
from fastapi import APIRouter
from app.plm_platform.schemas.schemas import (
    PLMProjectRequest,
    PLMProjectResponse,
    ChangeRequestRequest,
    ChangeRequestResponse,
    ReleaseRequest,
    ReleaseResponse,
)
from app.plm_platform.services.plm_orchestrator import PLMOrchestrator
from app.plm_platform.services.change_management_service import ChangeManagementService
from app.plm_platform.services.release_management_service import ReleaseManagementService

router = APIRouter(prefix="/plm-platform", tags=["PLM Platform"])
orchestrator = PLMOrchestrator()
change_service = ChangeManagementService()
release_service = ReleaseManagementService()


@router.post("/projects", response_model=PLMProjectResponse)
async def create_plm_project(request: PLMProjectRequest):
    result = orchestrator.create_project(
        project_id=request.project_id,
        name=request.name
    )
    return PLMProjectResponse(**result)


@router.post("/change-requests", response_model=ChangeRequestResponse)
async def submit_change_request(request: ChangeRequestRequest):
    result = change_service.create_request(
        plm_project_id=request.plm_project_id,
        title=request.title,
        description=request.description or ""
    )
    return ChangeRequestResponse(**result)


@router.post("/releases", response_model=ReleaseResponse)
async def create_release(request: ReleaseRequest):
    result = release_service.create_release(
        plm_project_id=request.plm_project_id,
        version=request.version,
        artifacts=[]
    )
    return ReleaseResponse(**result)
