"""
CAD Generation & Engineering Geometry Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class BaseCADRequest(BaseModel):
    project_id: str
    requirements: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CADPartRequest(BaseCADRequest):
    part_type: str = "bracket"


class CADPartResponse(BaseModel):
    id: str
    project_id: str
    part_name: str
    features: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]
    parametric_dimensions: Dict[str, float]
    export_formats: List[str] = ["step", "stl"]
    execution_time_ms: Optional[float] = None
    created_at: datetime


class CADAassemblyRequest(BaseCADRequest):
    part_ids: List[str] = Field(default_factory=list)


class CADAassemblyResponse(BaseModel):
    id: str
    project_id: str
    assembly_name: str
    parts: List[Dict[str, Any]]
    mates: List[Dict[str, Any]]
    joints: List[Dict[str, Any]]
    execution_time_ms: Optional[float] = None
    created_at: datetime


class CADDrawingRequest(BaseCADRequest):
    part_id: Optional[str] = None
    assembly_id: Optional[str] = None


class CADDrawingResponse(BaseModel):
    id: str
    project_id: str
    drawing_name: str
    views: List[Dict[str, Any]]
    dimensions: List[Dict[str, Any]]
    notes: List[str]
    execution_time_ms: Optional[float] = None
    created_at: datetime


class CADToleranceRequest(BaseCADRequest):
    part_id: str


class CADToleranceResponse(BaseModel):
    id: str
    project_id: str
    tolerances: List[Dict[str, Any]]
    gdt_recommendations: List[str]
    tolerance_stackups: List[Dict[str, Any]]
    execution_time_ms: Optional[float] = None
    created_at: datetime


class CADManufacturingRequest(BaseCADRequest):
    manufacturing_process: str = "cnc"


class CADManufacturingResponse(BaseModel):
    id: str
    project_id: str
    constraints: List[str]
    dfm_review: List[str]
    recommendations: List[str]
    execution_time_ms: Optional[float] = None
    created_at: datetime


class CADReviewRequest(BaseCADRequest):
    pass


class CADReviewResponse(BaseModel):
    id: str
    project_id: str
    warnings: List[str]
    recommendations: List[str]
    approval_status: str = "pending"
    execution_time_ms: Optional[float] = None
    created_at: datetime
