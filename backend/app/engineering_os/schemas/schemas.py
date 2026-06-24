"""
Schemas for Sprint 8 & 9 Engineering OS
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


# Sprint 8 Schemas
class ExecuteAgentRequest(BaseModel):
    project_id: str
    agent_type: str
    title: str
    description: Optional[str] = None
    input_data: Dict[str, Any] = Field(default_factory=dict)


class DesignGenerateRequest(BaseModel):
    requirements: str
    project_id: Optional[str] = None
    max_iterations: int = 5


class CopilotChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ProjectCreateRequest(BaseModel):
    name: str
    requirements: Optional[str] = ""


class KnowledgeQueryRequest(BaseModel):
    query: str
    node_type: Optional[str] = None


# Sprint 9 Schemas
class CreateOrganizationRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    org_type: str = "startup"
    tenant_id: Optional[str] = None


class CreateTeamRequest(BaseModel):
    org_id: str
    name: str
    description: Optional[str] = ""
    department_id: Optional[str] = None


class CreateRoleRequest(BaseModel):
    name: str
    description: str
    permissions: Optional[List[str]] = None


class AssignRoleRequest(BaseModel):
    user_id: str
    role_name: str


class TrackEventRequest(BaseModel):
    event_type: str
    user_id: str
    data: Dict[str, Any]
    resource_id: Optional[str] = None
    tenant_id: Optional[str] = None


class StartReviewRequest(BaseModel):
    resource_id: str
    review_type: str
    title: str
    user_id: str
    reviewer_ids: List[str]


class RequestApprovalRequest(BaseModel):
    resource_id: str
    user_id: str
    approver_ids: List[str]
    notes: Optional[str] = ""


class UploadDocumentRequest(BaseModel):
    name: str
    doc_type: str
    content: str
    project_id: Optional[str] = None
    tenant_id: Optional[str] = None


class CreateKnowledgeArticleRequest(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = None
    tenant_id: Optional[str] = None


class CreatePortfolioRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    tenant_id: Optional[str] = None


class CreateTenantRequest(BaseModel):
    name: str
    domain: str
    plan: str = "basic"


class LoginWithProviderRequest(BaseModel):
    provider: str  # google/microsoft/github/saml
    code: str
    state: str


class VerifySessionRequest(BaseModel):
    session_id: str
