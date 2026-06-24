"""
CAD Generation & Engineering Geometry Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class BaseCADRequest(BaseModel):
    project_id: str
    requirements: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CADGenerateRequest(BaseCADRequest):
    requirements: Dict[str, Any]
    export_formats: Optional[List[str]] = ["step", "stl"]


class CADGenerateResponse(BaseModel):
    id: str
    project_id: str
    cad_project: Dict[str, Any]
    geometry: Dict[str, Any]
    parametric_model: Dict[str, Any]
    feature_model: Dict[str, Any]
    exports: Dict[str, str]
    created_at: datetime


class CADPartRequest(BaseCADRequest):
    part_type: str = "bracket"
    name: Optional[str] = None
    parameters: Optional[Dict[str, float]] = Field(default_factory=dict)
    features: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


class CADPartResponse(BaseModel):
    id: str
    project_id: str
    name: str
    part_type: str
    features: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]
    parametric_dimensions: Dict[str, float]
    created_at: datetime


class CADAssemblyRequest(BaseCADRequest):
    name: str
    parts: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    mates: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


class CADAssemblyResponse(BaseModel):
    id: str
    project_id: str
    name: str
    parts: List[Dict[str, Any]]
    mates: List[Dict[str, Any]]
    joints: List[Dict[str, Any]]
    created_at: datetime


class CADDrawingRequest(BaseCADRequest):
    part_id: Optional[str] = None
    assembly_id: Optional[str] = None
    views: Optional[List[str]] = ["front", "top", "right", "isometric"]
    title: Optional[str] = None


class CADDrawingResponse(BaseModel):
    id: str
    project_id: str
    title: str
    part_or_assembly_id: Optional[str]
    views: List[Dict[str, Any]]
    dimensions: List[Dict[str, Any]]
    annotations: List[Dict[str, Any]]
    gd_and_t: List[Dict[str, Any]]
    created_at: datetime


class BOMGenerateRequest(BaseCADRequest):
    assembly_id: str
    include_subassemblies: Optional[bool] = True


class BOMGenerateResponse(BaseModel):
    id: str
    assembly_id: str
    assembly_name: str
    items: List[Dict[str, Any]]
    total_cost: float
    created_at: datetime


class MaterialResponse(BaseModel):
    id: str
    name: str
    density_kgm3: float
    youngs_modulus_pa: Optional[float]
    yield_strength_pa: Optional[float]
    ultimate_strength_pa: Optional[float]
    cost_per_kg: Optional[float]
    categories: List[str]


class ComponentSearchRequest(BaseModel):
    category: Optional[str] = None
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ComponentSearchResponse(BaseModel):
    results: List[Dict[str, Any]]


class MechanicalAnalysisRequest(BaseCADRequest):
    requirements: Dict[str, Any]


class MechanicalAnalysisResponse(BaseModel):
    material_recommendations: List[MaterialResponse]
    fastener_recommendations: List[Dict[str, Any]]
    tolerance_recommendations: List[Dict[str, Any]]
    structural_recommendations: List[str]


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


class ManufacturingPackageRequest(BaseCADRequest):
    assembly_id: str
    bom_id: str
    name: Optional[str] = None


class ManufacturingPackageResponse(BaseModel):
    id: str
    project_id: str
    cad_project_id: str
    assembly_id: str
    bom_id: str
    name: str
    files: List[Dict[str, Any]]
    drawings: List[Dict[str, Any]]
    created_at: datetime
