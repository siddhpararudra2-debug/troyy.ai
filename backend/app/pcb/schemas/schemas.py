"""
PCB Intelligence Module Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


# ================ BASE REQUEST & RESPONSE ================
class PCBBaseRequest(BaseModel):
    project_id: str
    schematic_id: Optional[str] = None
    requirements: Dict[str, Any] = Field(default_factory=dict)


# ================ PCB ARCHITECTURE ================
class PCBArchitectureRequest(PCBBaseRequest):
    board_width_mm: Optional[float] = 100.0
    board_height_mm: Optional[float] = 80.0


class SubsystemRegion(BaseModel):
    name: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    description: str


class PCBArchitectureResponse(BaseModel):
    id: str
    project_id: str
    board_width_mm: float
    board_height_mm: float
    subsystem_regions: List[SubsystemRegion] = Field(default_factory=list)
    power_domains: List[Dict[str, Any]] = Field(default_factory=list)
    signal_domains: List[Dict[str, Any]] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# ================ STACKUP ================
class StackupLayer(BaseModel):
    name: str
    layer_type: str  # "signal", "ground", "power", "dielectric"
    material: Optional[str] = None
    thickness_mm: Optional[float] = None
    copper_weight_oz: Optional[float] = None
    impedance_ohms: Optional[float] = None


class PCBStackupRequest(PCBBaseRequest):
    layer_count: int = 4  # 2, 4, 6, 8, 10+


class PCBStackupResponse(BaseModel):
    id: str
    project_id: str
    layer_count: int
    layers: List[StackupLayer] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# ================ PLACEMENT ================
class PlacedComponent(BaseModel):
    component_id: str
    part_number: str
    x_mm: float
    y_mm: float
    rotation_deg: float = 0.0
    side: str = "top"  # "top", "bottom"
    priority: int = 1


class PCBPlacementRequest(PCBBaseRequest):
    pass


class PCBPlacementResponse(BaseModel):
    id: str
    project_id: str
    components: List[PlacedComponent] = Field(default_factory=list)
    placement_regions: List[Dict[str, Any]] = Field(default_factory=list)
    optimization_score: Optional[float] = None
    execution_time_ms: Optional[float] = None
    created_at: datetime


# ================ ROUTING ================
class RoutingRule(BaseModel):
    signal_name: str
    trace_width_mm: Optional[float] = None
    trace_spacing_mm: Optional[float] = None
    priority: int = 1
    is_differential: bool = False
    is_high_speed: bool = False


class PCBRoutingRequest(PCBBaseRequest):
    pass


class PCBRoutingResponse(BaseModel):
    id: str
    project_id: str
    routing_rules: List[RoutingRule] = Field(default_factory=list)
    routing_priorities: List[Dict[str, Any]] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# ================ POWER DISTRIBUTION ================
class PowerDomain(BaseModel):
    voltage: float
    current_max_a: float
    component_ids: List[str] = Field(default_factory=list)
    decoupling_strategy: Optional[str] = None


class PCBPowerRequest(PCBBaseRequest):
    pass


class PCBPowerResponse(BaseModel):
    id: str
    project_id: str
    power_domains: List[PowerDomain] = Field(default_factory=list)
    power_planes: List[Dict[str, Any]] = Field(default_factory=list)
    regulator_placement: List[Dict[str, Any]] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# ================ GROUNDING ================
class GroundStrategy(BaseModel):
    strategy_type: str  # "single_plane", "split", "mixed_signal", "high_current"
    description: str
    ground_paths: List[Dict[str, Any]] = Field(default_factory=list)


class PCBGroundingRequest(PCBBaseRequest):
    pass


class PCBGroundingResponse(BaseModel):
    id: str
    project_id: str
    ground_strategy: GroundStrategy
    return_current_analysis: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# ================ THERMAL ================
class HotSpot(BaseModel):
    x_mm: float
    y_mm: float
    temperature_c: float
    component_id: Optional[str] = None


class PCBThermalRequest(PCBBaseRequest):
    pass


class PCBThermalResponse(BaseModel):
    id: str
    project_id: str
    power_dissipation_w: Optional[float] = None
    hot_spots: List[HotSpot] = Field(default_factory=list)
    thermal_density_map: Dict[str, Any] = Field(default_factory=dict)
    cooling_recommendations: List[str] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# ================ EMI/EMC ================
class EMIRisk(BaseModel):
    severity: str  # "low", "medium", "high", "critical"
    category: str
    description: str
    recommendation: str


class PCBEMIRequest(PCBBaseRequest):
    pass


class PCBEMIResponse(BaseModel):
    id: str
    project_id: str
    emi_risks: List[EMIRisk] = Field(default_factory=list)
    emc_recommendations: List[str] = Field(default_factory=list)
    loop_area_analysis: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# ================ DRC ================
class DRCViolation(BaseModel):
    severity: str  # "error", "warning", "info"
    rule: str
    description: str
    location: Optional[Dict[str, float]] = None
    affected_elements: List[str] = Field(default_factory=list)


class PCBDRCRequest(PCBBaseRequest):
    pass


class PCBDRCResponse(BaseModel):
    id: str
    project_id: str
    violations: List[DRCViolation] = Field(default_factory=list)
    total_errors: int = 0
    total_warnings: int = 0
    is_drc_passed: bool = True
    execution_time_ms: Optional[float] = None
    created_at: datetime


# ================ MANUFACTURING ================
class ManufacturingConstraint(BaseModel):
    category: str
    constraint: str
    value: Any
    description: str


class PCBManufacturingRequest(PCBBaseRequest):
    pass


class PCBManufacturingResponse(BaseModel):
    id: str
    project_id: str
    fabrication_constraints: List[ManufacturingConstraint] = Field(default_factory=list)
    assembly_constraints: List[ManufacturingConstraint] = Field(default_factory=list)
    dfm_review: List[str] = Field(default_factory=list)
    dfa_review: List[str] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# ================ REVIEW ================
class ReviewIssue(BaseModel):
    category: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    recommendation: str


class PCBReviewRequest(PCBBaseRequest):
    pass


class PCBReviewResponse(BaseModel):
    id: str
    project_id: str
    placement_review: List[ReviewIssue] = Field(default_factory=list)
    routing_review: List[ReviewIssue] = Field(default_factory=list)
    power_review: List[ReviewIssue] = Field(default_factory=list)
    grounding_review: List[ReviewIssue] = Field(default_factory=list)
    thermal_review: List[ReviewIssue] = Field(default_factory=list)
    emi_review: List[ReviewIssue] = Field(default_factory=list)
    manufacturability_review: List[ReviewIssue] = Field(default_factory=list)
    approval_status: str = "pending"  # "approved", "rejected", "needs_revision", "pending"
    overall_score: Optional[float] = None
    execution_time_ms: Optional[float] = None
    created_at: datetime
