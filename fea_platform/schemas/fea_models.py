from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid

class LoadCase(BaseModel):
    name: str
    load_type: str  # "FORCE", "PRESSURE", "GRAVITY", "THERMAL"
    magnitude: float
    direction: List[float] = Field(default_factory=lambda: [0.0, 0.0, -1.0])
    region: str = "ALL"

class Constraint(BaseModel):
    name: str
    constraint_type: str  # "FIXED", "PINNED", "ROLLER", "SYMMETRY"
    region: str
    dofs: List[int] = Field(default_factory=lambda: [1, 2, 3, 4, 5, 6])

class MeshResult(BaseModel):
    node_count: int
    element_count: int
    nodes: List[tuple] = Field(default_factory=list)
    elements: List[tuple] = Field(default_factory=list)
    quality_metrics: Dict[str, float] = Field(default_factory=dict)

class FEAResult(BaseModel):
    job_id: str
    analysis_type: str
    max_von_mises_pa: float = 0.0
    max_principal_stress_pa: float = 0.0
    max_displacement_m: float = 0.0
    factor_of_safety: float = 0.0
    fatigue_life_cycles: Optional[float] = None
    buckling_load_factor: Optional[float] = None
    natural_frequencies_hz: List[float] = Field(default_factory=list)
    stress_field: Optional[List[float]] = None
    displacement_field: Optional[List[float]] = None
