"""
Engineering Cloud Routes
"""
from fastapi import APIRouter
from app.engineering_cloud.schemas.schemas import (
    CreateTenantRequest,
    CreateTenantResponse,
    CreateWorkspaceRequest,
    CreateWorkspaceResponse,
    CreateSubscriptionRequest,
    CreateSubscriptionResponse
)
from app.engineering_cloud.services.tenant_manager import TenantManager
from app.engineering_cloud.services.cloud_workspace import CloudWorkspace
from app.engineering_cloud.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/cloud", tags=["Engineering Cloud"])

tenant_manager = TenantManager()
cloud_workspace = CloudWorkspace()
subscription_service = SubscriptionService()


@router.post("/tenant", response_model=CreateTenantResponse)
async def create_tenant(request: CreateTenantRequest):
    result = tenant_manager.create_tenant(request.dict())
    return CreateTenantResponse(**result)


@router.post("/workspace", response_model=CreateWorkspaceResponse)
async def create_workspace(request: CreateWorkspaceRequest):
    result = cloud_workspace.create_workspace(request.tenant_id, request.workspace_name)
    return CreateWorkspaceResponse(**result)


@router.post("/subscription", response_model=CreateSubscriptionResponse)
async def create_subscription(request: CreateSubscriptionRequest):
    result = subscription_service.create_subscription(request.tenant_id, request.plan)
    return CreateSubscriptionResponse(**result)
