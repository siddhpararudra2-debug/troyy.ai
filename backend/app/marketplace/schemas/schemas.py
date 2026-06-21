"""
Marketplace Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class Plugin(BaseModel):
    id: str
    name: str
    description: str
    category: str
    version: str
    author: str
    price: float
    rating: float
    installs: int
    created_at: datetime
    execution_time_ms: float


class PluginListResponse(BaseModel):
    plugins: List[Plugin]


class InstallPluginRequest(BaseModel):
    plugin_id: str
    tenant_id: str


class InstallPluginResponse(BaseModel):
    id: str
    plugin_id: str
    tenant_id: str
    status: str
    installed_at: datetime
    execution_time_ms: float


class ExecutePluginRequest(BaseModel):
    plugin_id: str
    payload: Dict[str, Any]


class ExecutePluginResponse(BaseModel):
    plugin_id: str
    status: str
    result: Dict[str, Any]
    execution_time_ms: float
