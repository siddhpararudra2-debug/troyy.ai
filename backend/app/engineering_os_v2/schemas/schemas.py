"""
Engineering OS V2 Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class EnterpriseProjectRequest(BaseModel):
    name: str
    mission_requirements: Dict[str, Any] = Field(default_factory=dict)


class EnterpriseProjectResponse(BaseModel):
    id: str
    name: str
    status: str
    created_at: datetime
    execution_time_ms: float


class EnterpriseDashboardResponse(BaseModel):
    portfolio_health: float
    active_projects: int
    mission_readiness: float
    manufacturing_readiness: float
    compliance_readiness: float
    verification_readiness: float
    certification_readiness: float
    last_updated: datetime
    execution_time_ms: float


class PortfolioProject(BaseModel):
    id: str
    name: str
    health: float


class PortfolioResponse(BaseModel):
    projects: List[PortfolioProject]
    execution_time_ms: float


class Agent(BaseModel):
    id: str
    type: str
    status: str


class AgentsResponse(BaseModel):
    agents: List[Agent]
    execution_time_ms: float


class CommandCenterStatus(BaseModel):
    active_agents: int
    active_tasks: int
    system_status: str
    execution_time_ms: float


class ExecutiveReportRequest(BaseModel):
    report_type: str = "monthly"


class ExecutiveReportResponse(BaseModel):
    id: str
    type: str
    status: str
    created_at: datetime
    execution_time_ms: float


class WorkspaceRequest(BaseModel):
    project_id: str


class WorkspaceResponse(BaseModel):
    project_id: str
    modules: List[str]
    status: str
    execution_time_ms: float


class RuntimeExecutionRequest(BaseModel):
    project_id: str
    workflow: str


class RuntimeExecutionResponse(BaseModel):
    id: str
    project_id: str
    workflow: str
    status: str
    execution_time_ms: float
