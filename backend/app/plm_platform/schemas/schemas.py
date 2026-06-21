"""
PLM Platform Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class PLMProjectRequest(BaseModel):
    project_id: str
    name: str


class PLMProjectResponse(BaseModel):
    id: str
    project_id: str
    name: str
    status: str
    created_at: datetime
    updated_at: datetime


class ChangeRequestRequest(BaseModel):
    plm_project_id: str
    title: str
    description: Optional[str] = None


class ChangeRequestResponse(BaseModel):
    id: str
    plm_project_id: str
    title: str
    description: Optional[str]
    status: str
    created_at: datetime


class ReleaseRequest(BaseModel):
    plm_project_id: str
    version: str


class ReleaseResponse(BaseModel):
    id: str
    plm_project_id: str
    version: str
    status: str
    created_at: datetime
