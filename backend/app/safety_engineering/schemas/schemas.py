"""
Safety Engineering Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class SafetyAnalysisRequest(BaseModel):
    project_id: str
    analysis_type: str = "hazard_analysis"


class SafetyAnalysisResponse(BaseModel):
    id: str
    project_id: str
    type: str
    status: str
    created_at: datetime
    execution_time_ms: float
