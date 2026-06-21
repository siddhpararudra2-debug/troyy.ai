"""
Business Operations Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class OpportunityRequest(BaseModel):
    title: str
    description: str
    domain: str


class OpportunityResponse(BaseModel):
    id: str
    title: str
    description: str
    domain: str
    priority: str
    feasibility_score: float
    created_at: datetime
    execution_time_ms: float


class ProposalRequest(BaseModel):
    project_id: str
    requirements: Dict[str, Any]


class ProposalResponse(BaseModel):
    id: str
    project_id: str
    requirements: Dict[str, Any]
    status: str
    created_at: datetime
    execution_time_ms: float


class ExecutiveDashboardResponse(BaseModel):
    active_projects: int
    revenue_ytd: float
    pipeline_value: float
    customer_satisfaction: float
    last_updated: datetime
    execution_time_ms: float
