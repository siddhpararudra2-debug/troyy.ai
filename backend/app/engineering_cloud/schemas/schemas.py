"""
Engineering Cloud Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class Tenant(BaseModel):
    id: str
    name: str
    status: str
    created_at: datetime
    execution_time_ms: float


class CreateTenantRequest(BaseModel):
    name: str
    email: str


class CreateTenantResponse(Tenant):
    pass


class Workspace(BaseModel):
    id: str
    tenant_id: str
    name: str
    status: str
    created_at: datetime
    execution_time_ms: float


class CreateWorkspaceRequest(BaseModel):
    tenant_id: str
    workspace_name: str


class CreateWorkspaceResponse(Workspace):
    pass


class Subscription(BaseModel):
    id: str
    tenant_id: str
    plan: str
    status: str
    start_date: datetime
    end_date: datetime
    execution_time_ms: float


class CreateSubscriptionRequest(BaseModel):
    tenant_id: str
    plan: str = "enterprise"


class CreateSubscriptionResponse(Subscription):
    pass
