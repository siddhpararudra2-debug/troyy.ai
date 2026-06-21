"""
Engineering OS V3 Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class ExecutionRequest(BaseModel):
    requirement: str


class ExecutionResponse(BaseModel):
    id: str
    status: str
    current_step: str
    created_at: datetime
    execution_time_ms: float


class ProjectStatusResponse(BaseModel):
    project_id: str
    status: str
    progress: float
    issues: List[Dict[str, Any]]
    last_updated: datetime
    execution_time_ms: float


class GlobalDashboardResponse(BaseModel):
    system_status: str
    active_workflows: int
    alerts: List[Dict[str, Any]]
    last_updated: datetime
    execution_time_ms: float
