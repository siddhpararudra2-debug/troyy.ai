"""
Hardware Integration Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class HardwareConnectRequest(BaseModel):
    device_type: str
    connection_params: Dict[str, Any]


class HardwareConnectResponse(BaseModel):
    id: str
    device_type: str
    status: str
    created_at: datetime
    execution_time_ms: float


class HardwareTestRequest(BaseModel):
    device_id: str
    test_type: str
