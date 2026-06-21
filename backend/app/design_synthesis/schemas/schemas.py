"""
Design Synthesis Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class DesignSynthesisRequest(BaseModel):
    project_id: str
    name: str
    requirements: Dict[str, Any] = Field(default_factory=dict)
    domain: str = "aerospace"  # aerospace, robotics, mechanical


class DesignSynthesisResponse(BaseModel):
    id: str
    project_id: str
    name: str
    requirements: Dict[str, Any]
    status: str
    current_iteration: int
    created_at: datetime
    updated_at: datetime


class GeometrySynthesisRequest(BaseModel):
    design_synthesis_project_id: str
    requirements: Dict[str, Any] = Field(default_factory=dict)


class GeometrySynthesisResponse(BaseModel):
    id: str
    design_synthesis_project_id: str
    geometry: Dict[str, Any]
    parameters: Dict[str, float]
    performance: Dict[str, Any]
    status: str
    created_at: datetime


class StructuralSizingRequest(BaseModel):
    design_synthesis_project_id: str
    loads: Dict[str, Any] = Field(default_factory=dict)
    material: str = "aluminum"


class StructuralSizingResponse(BaseModel):
    id: str
    design_synthesis_project_id: str
    dimensions: Dict[str, float]
    stress_analysis: Dict[str, Any]
    safety_factor: float
    mass_estimate: float
    created_at: datetime


class SynthesisValidationRequest(BaseModel):
    design_synthesis_project_id: str
    iteration_id: Optional[str] = None


class SynthesisValidationResponse(BaseModel):
    id: str
    design_synthesis_project_id: str
    is_valid: bool
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    created_at: datetime
