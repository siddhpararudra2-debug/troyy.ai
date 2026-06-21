"""
Electronics Execution Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class ElectronicsArchitectureRequest(BaseModel):
    project_id: str
    name: str
    requirements: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ElectronicsArchitectureResponse(BaseModel):
    id: str
    project_id: str
    name: str
    status: str
    power_tree: Dict[str, Any]
    signal_chain: Dict[str, Any]
    created_at: datetime


class PowerSystemDesignRequest(BaseModel):
    electronics_architecture_id: str
    requirements: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PowerSystemDesignResponse(BaseModel):
    id: str
    electronics_architecture_id: str
    voltages: List[Dict[str, Any]]
    regulators: List[Dict[str, Any]]
    created_at: datetime


class SignalChainDesignRequest(BaseModel):
    electronics_architecture_id: str
    requirements: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SignalChainDesignResponse(BaseModel):
    id: str
    electronics_architecture_id: str
    sensors: List[Dict[str, Any]]
    interfaces: List[Dict[str, Any]]
    created_at: datetime
