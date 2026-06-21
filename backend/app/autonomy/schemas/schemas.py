"""
Autonomy Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class ControlRequest(BaseModel):
    type: str = "pid"
    parameters: Dict[str, Any] = None


class MissionRequest(BaseModel):
    waypoints: List[Dict[str, Any]]
