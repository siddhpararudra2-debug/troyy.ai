"""
Mission Engineering Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class MissionProjectRequest(BaseModel):
    project_id: str
    name: str
    mission_type: str = "surveillance"
    requirements: Dict[str, Any] = Field(default_factory=dict)


class MissionProjectResponse(BaseModel):
    id: str
    project_id: str
    name: str
    mission_type: str
    status: str
    requirements: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class MissionPlanRequest(BaseModel):
    mission_project_id: str


class MissionPlanResponse(BaseModel):
    id: str
    mission_project_id: str
    airframe: Optional[str] = None
    propulsion: Optional[str] = None
    battery: Optional[str] = None
    payload: Optional[str] = None
    navigation: Optional[str] = None
    communications: Optional[str] = None
    control_systems: Optional[str] = None
    status: str
    created_at: datetime


class MissionValidationRequest(BaseModel):
    mission_project_id: str


class MissionValidationResponse(BaseModel):
    id: str
    mission_project_id: str
    readiness_score: float
    issues: List[Dict[str, Any]]
    status: str
    created_at: datetime


class MissionRiskRequest(BaseModel):
    mission_project_id: str


class MissionRiskResponse(BaseModel):
    id: str
    mission_project_id: str
    risk_level: str
    risks: List[Dict[str, Any]]
    created_at: datetime
