"""
Engineering OS Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class EngineeringProjectRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    domain: str = "multi"


class EngineeringProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    domain: str
    status: str
    created_at: datetime


class WorkflowExecutionRequest(BaseModel):
    project_id: str
    requirement: str
    workflow: Optional[List[str]] = Field(default_factory=list)


class WorkflowExecutionResponse(BaseModel):
    id: str
    project_id: str
    status: str
    requirement: str
    steps: List[Dict[str, Any]]
    created_at: datetime
