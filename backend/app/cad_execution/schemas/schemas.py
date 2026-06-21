"""
CAD Execution Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class CADExecutionProjectRequest(BaseModel):
    project_id: str
    name: str
    engine: str = "cadquery"  # cadquery, freecad
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CADExecutionProjectResponse(BaseModel):
    id: str
    project_id: str
    name: str
    status: str
    engine: str
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class CADPartExecutionRequest(BaseModel):
    cad_execution_project_id: str
    part_name: str
    part_type: str = "bracket"
    parametric_dimensions: Optional[Dict[str, float]] = Field(default_factory=dict)
    material: str = "aluminum"


class CADPartExecutionResponse(BaseModel):
    id: str
    cad_execution_project_id: str
    part_name: str
    part_type: str
    geometry: Dict[str, Any]
    parametric_dimensions: Dict[str, float]
    material: str
    status: str
    file_path: Optional[str] = None
    created_at: datetime


class CADAssemblyExecutionRequest(BaseModel):
    cad_execution_project_id: str
    assembly_name: str
    parts: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    mates: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


class CADAssemblyExecutionResponse(BaseModel):
    id: str
    cad_execution_project_id: str
    assembly_name: str
    parts: List[Dict[str, Any]]
    mates: List[Dict[str, Any]]
    status: str
    file_path: Optional[str] = None
    created_at: datetime


class CADExportRequest(BaseModel):
    cad_execution_project_id: str
    part_or_assembly_id: str
    export_format: str = "step"  # step, stl, iges, obj, gltf, fcstd


class CADExportResponse(BaseModel):
    id: str
    cad_execution_project_id: str
    part_or_assembly_id: str
    export_format: str
    file_path: str
    status: str
    created_at: datetime


class CADValidationRequest(BaseModel):
    cad_execution_project_id: str
    part_or_assembly_id: str
    validation_type: str = "geometry"  # geometry, mass_properties, gdnt, manufacturability


class CADValidationResponse(BaseModel):
    id: str
    cad_execution_project_id: str
    part_or_assembly_id: str
    validation_type: str
    is_valid: bool
    issues: List[Dict[str, Any]]
    mass_properties: Optional[Dict[str, Any]] = None
    execution_time_ms: Optional[float] = None
    created_at: datetime
