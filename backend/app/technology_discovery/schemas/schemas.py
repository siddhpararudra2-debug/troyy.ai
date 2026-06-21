"""
Technology Discovery Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class DiscoveryRequest(BaseModel):
    domain: str


class DiscoveryResponse(BaseModel):
    id: str
    domain: str
    status: str
    created_at: datetime
    execution_time_ms: float


class TrendForecastRequest(BaseModel):
    domain: str
    horizon: int = 12


class TrendForecastResponse(BaseModel):
    domain: str
    horizon_months: int
    trends: List[Dict[str, Any]]
    execution_time_ms: float


class TechDashboardResponse(BaseModel):
    active_research: int
    monitored_patents: int
    trending_technologies: int
    last_updated: datetime
    execution_time_ms: float
