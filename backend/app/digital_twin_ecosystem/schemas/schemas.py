"""
Digital Twin Ecosystem Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class DigitalTwinRequest(BaseModel):
    project_id: str
    name: str
    twin_type: str = "drone"
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DigitalTwinResponse(BaseModel):
    id: str
    project_id: str
    name: str
    twin_type: str
    status: str
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class TwinSyncRequest(BaseModel):
    digital_twin_id: str
    sensor_data: Dict[str, Any] = Field(default_factory=dict)


class TwinSyncResponse(BaseModel):
    id: str
    digital_twin_id: str
    sensor_data: Dict[str, Any]
    status: str
    created_at: datetime


class TwinPredictionRequest(BaseModel):
    digital_twin_id: str
    prediction_type: str = "performance"


class TwinPredictionResponse(BaseModel):
    id: str
    digital_twin_id: str
    prediction_type: str
    results: Dict[str, Any]
    created_at: datetime


class TwinHealthRequest(BaseModel):
    digital_twin_id: str


class TwinHealthResponse(BaseModel):
    id: str
    digital_twin_id: str
    health_score: float
    remaining_useful_life: Optional[float] = None
    recommendations: List[Dict[str, Any]]
    created_at: datetime
