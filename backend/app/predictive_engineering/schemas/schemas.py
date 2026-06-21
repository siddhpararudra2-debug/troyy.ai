"""
Predictive Engineering Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class PredictiveAnalysisRequest(BaseModel):
    project_id: str
    analysis_type: str = "failure_prediction"
    data: Dict[str, Any] = Field(default_factory=dict)


class PredictiveAnalysisResponse(BaseModel):
    id: str
    project_id: str
    analysis_type: str
    results: Dict[str, Any]
    created_at: datetime


class AnomalyRequest(BaseModel):
    predictive_analysis_id: str
    sensor_data: Dict[str, Any] = Field(default_factory=dict)


class AnomalyResponse(BaseModel):
    id: str
    predictive_analysis_id: str
    anomalies: List[Dict[str, Any]]
    created_at: datetime


class MaintenanceRequest(BaseModel):
    predictive_analysis_id: str


class MaintenanceResponse(BaseModel):
    id: str
    predictive_analysis_id: str
    tasks: List[Dict[str, Any]]
    created_at: datetime
