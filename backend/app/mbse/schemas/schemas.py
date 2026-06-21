"""
MBSE Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class CreateModelRequest(BaseModel):
    name: str
    type: str = "logical_architecture"


class ModelResponse(BaseModel):
    id: str
    name: str
    type: str
    status: str
    created_at: datetime
    execution_time_ms: float


class GetModelRequest(BaseModel):
    id: str
