from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from simulation_execution.schemas.enums import SolverType, MeshType, SimulationDomain, JobStatus

class SolverConfig(BaseModel):
    solver_type: SolverType
    version: str = "latest"
    cores: int = 4
    memory_gb: float = 8.0
    timeout_seconds: int = 3600
    working_dir: Optional[str] = None

class MeshConfig(BaseModel):
    mesh_type: MeshType = MeshType.TETRA
    element_size_m: float = 0.01
    max_aspect_ratio: float = 5.0
    growth_rate: float = 1.2
    boundary_layers: int = 5
    first_layer_height_m: float = 0.001

class BoundaryCondition(BaseModel):
    name: str
    bc_type: str  # "FIXED", "FORCE", "PRESSURE", "VELOCITY", "TEMPERATURE", "VOLTAGE"
    region: str
    values: Dict[str, float] = Field(default_factory=dict)

class Material(BaseModel):
    name: str
    density_kg_m3: float
    youngs_modulus_pa: float
    poisson_ratio: float
    yield_strength_pa: float
    thermal_conductivity_w_mk: float = 0.0
    specific_heat_j_kgk: float = 0.0

class SimulationJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    domain: SimulationDomain
    solver_config: SolverConfig
    mesh_config: Optional[MeshConfig] = None
    materials: List[Material] = Field(default_factory=list)
    boundary_conditions: List[BoundaryCondition] = Field(default_factory=list)
    status: JobStatus = JobStatus.QUEUED
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_ref: Optional[str] = None
    error_message: Optional[str] = None

class SimulationResult(BaseModel):
    job_id: str
    status: JobStatus
    solver_output: str = ""
    convergence_data: List[float] = Field(default_factory=list)
    max_stress_pa: Optional[float] = None
    max_displacement_m: Optional[float] = None
    max_temp_k: Optional[float] = None
    lift_n: Optional[float] = None
    drag_n: Optional[float] = None
    result_files: List[str] = Field(default_factory=list)
    execution_time_s: float = 0.0
    peak_memory_mb: float = 0.0
