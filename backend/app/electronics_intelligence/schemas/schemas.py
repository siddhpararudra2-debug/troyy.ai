"""
Electronics Intelligence Pydantic Schemas
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any, Optional, List, Dict


class ComponentBase(BaseModel):
    """Base component schema."""
    component_type: str = Field(..., description="Component type (mcu, sensor, regulator, mosfet, communication)")
    manufacturer: str = Field(..., description="Manufacturer name")
    part_number: str = Field(..., description="Part number")
    description: Optional[str] = None
    specifications: Dict[str, Any] = Field(default_factory=dict, description="Component specifications")
    package: Optional[str] = None
    operating_voltage_min: Optional[float] = None
    operating_voltage_max: Optional[float] = None
    operating_current_max: Optional[float] = None
    operating_temp_min: Optional[float] = None
    operating_temp_max: Optional[float] = None
    interfaces: List[str] = Field(default_factory=list, description="Supported interfaces")
    cost_usd: Optional[float] = None
    availability_score: float = 1.0
    datasheet_url: Optional[str] = None


class ComponentCreate(ComponentBase):
    """Schema for creating a component."""
    pass


class Component(ComponentBase):
    """Schema for returning a component."""
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}


class EngineeringJustification(BaseModel):
    """Engineering justification schema."""
    requirements: Dict[str, Any] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    selection_criteria: List[str] = Field(default_factory=list)
    reasoning: str = ""


class PerformanceAnalysis(BaseModel):
    """Performance analysis schema."""
    metrics: Dict[str, Any] = Field(default_factory=dict)
    compliance_notes: str = ""


class CostAnalysis(BaseModel):
    """Cost analysis schema."""
    unit_cost: Optional[float] = None
    total_estimated_cost: Optional[float] = None
    cost_comparison: Dict[str, float] = Field(default_factory=dict)


class AvailabilityAnalysis(BaseModel):
    """Availability analysis schema."""
    score: float = 1.0
    lead_time_weeks: Optional[int] = None
    alternatives: List[str] = Field(default_factory=list)
    notes: str = ""


class Tradeoff(BaseModel):
    """Tradeoff analysis schema."""
    factor: str
    description: str
    impact: str  # "positive", "negative", "neutral"


class ComponentRecommendationRequest(BaseModel):
    """Request schema for component recommendation."""
    project_id: str
    component_type: str
    requirements: Dict[str, Any] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)


class ComponentRecommendationResponse(BaseModel):
    """Response schema for component recommendation."""
    id: str
    project_id: str
    component_type: str
    selected_component: Optional[Component] = None
    alternatives: List[Component] = Field(default_factory=list)
    justification: EngineeringJustification = Field(default_factory=EngineeringJustification)
    tradeoffs: List[Tradeoff] = Field(default_factory=list)
    performance_analysis: PerformanceAnalysis = Field(default_factory=PerformanceAnalysis)
    cost_analysis: CostAnalysis = Field(default_factory=CostAnalysis)
    availability_analysis: AvailabilityAnalysis = Field(default_factory=AvailabilityAnalysis)
    validation_results: Dict[str, Any] = Field(default_factory=dict)
    documentation: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: Optional[float] = None
    created_at: datetime


class MicrocontrollerSelectionRequest(BaseModel):
    """Request schema for microcontroller selection."""
    project_id: str
    requirements: Dict[str, Any] = Field(default_factory=dict)
    gpio_requirements: Dict[str, int] = Field(default_factory=dict)
    adc_requirements: Dict[str, Any] = Field(default_factory=dict)
    pwm_requirements: Dict[str, Any] = Field(default_factory=dict)
    memory_requirements: Dict[str, int] = Field(default_factory=dict)
    communication_requirements: List[str] = Field(default_factory=list)


class MicrocontrollerSelectionResponse(BaseModel):
    """Response schema for microcontroller selection."""
    id: str
    project_id: str
    selected_mcu: Optional[Component] = None
    alternatives: List[Component] = Field(default_factory=list)
    gpio_analysis: Dict[str, Any] = Field(default_factory=dict)
    adc_analysis: Dict[str, Any] = Field(default_factory=dict)
    pwm_analysis: Dict[str, Any] = Field(default_factory=dict)
    memory_analysis: Dict[str, Any] = Field(default_factory=dict)
    communication_analysis: Dict[str, Any] = Field(default_factory=dict)
    justification: EngineeringJustification = Field(default_factory=EngineeringJustification)
    tradeoffs: List[Tradeoff] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


class SensorSelectionRequest(BaseModel):
    """Request schema for sensor selection."""
    project_id: str
    sensor_type: str
    requirements: Dict[str, Any] = Field(default_factory=dict)


class SensorSelectionResponse(BaseModel):
    """Response schema for sensor selection."""
    id: str
    project_id: str
    sensor_type: str
    selected_sensor: Optional[Component] = None
    alternatives: List[Component] = Field(default_factory=list)
    justification: EngineeringJustification = Field(default_factory=EngineeringJustification)
    tradeoffs: List[Tradeoff] = Field(default_factory=list)
    performance_analysis: PerformanceAnalysis = Field(default_factory=PerformanceAnalysis)
    execution_time_ms: Optional[float] = None
    created_at: datetime


class RegulatorSelectionRequest(BaseModel):
    """Request schema for regulator selection."""
    project_id: str
    regulator_type: str  # ldo, buck, boost, buck-boost
    requirements: Dict[str, Any] = Field(default_factory=dict)


class RegulatorSelectionResponse(BaseModel):
    """Response schema for regulator selection."""
    id: str
    project_id: str
    regulator_type: str
    selected_regulator: Optional[Component] = None
    alternatives: List[Component] = Field(default_factory=list)
    power_dissipation_analysis: Dict[str, Any] = Field(default_factory=dict)
    efficiency_analysis: Dict[str, Any] = Field(default_factory=dict)
    thermal_analysis: Dict[str, Any] = Field(default_factory=dict)
    justification: EngineeringJustification = Field(default_factory=EngineeringJustification)
    tradeoffs: List[Tradeoff] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


class MosfetSelectionRequest(BaseModel):
    """Request schema for MOSFET selection."""
    project_id: str
    requirements: Dict[str, Any] = Field(default_factory=dict)


class MosfetSelectionResponse(BaseModel):
    """Response schema for MOSFET selection."""
    id: str
    project_id: str
    selected_mosfet: Optional[Component] = None
    alternatives: List[Component] = Field(default_factory=list)
    voltage_analysis: Dict[str, Any] = Field(default_factory=dict)
    current_analysis: Dict[str, Any] = Field(default_factory=dict)
    switching_analysis: Dict[str, Any] = Field(default_factory=dict)
    thermal_analysis: Dict[str, Any] = Field(default_factory=dict)
    justification: EngineeringJustification = Field(default_factory=EngineeringJustification)
    tradeoffs: List[Tradeoff] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


class CommunicationSelectionRequest(BaseModel):
    """Request schema for communication protocol selection."""
    project_id: str
    requirements: Dict[str, Any] = Field(default_factory=dict)


class CommunicationSelectionResponse(BaseModel):
    """Response schema for communication protocol selection."""
    id: str
    project_id: str
    selected_protocol: str
    alternatives: List[str] = Field(default_factory=list)
    justification: EngineeringJustification = Field(default_factory=EngineeringJustification)
    tradeoffs: List[Tradeoff] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


class CompatibilityAnalysisRequest(BaseModel):
    """Request schema for compatibility analysis."""
    project_id: str
    components: List[str] = Field(default_factory=list)  # Component IDs


class CompatibilityIssue(BaseModel):
    """Compatibility issue schema."""
    category: str
    severity: str  # "error", "warning", "info"
    message: str
    affected_components: List[str] = Field(default_factory=list)
    recommendation: str = ""


class CompatibilityAnalysisResponse(BaseModel):
    """Response schema for compatibility analysis."""
    id: str
    project_id: str
    voltage_compatibility: Dict[str, Any] = Field(default_factory=dict)
    current_compatibility: Dict[str, Any] = Field(default_factory=dict)
    logic_level_compatibility: Dict[str, Any] = Field(default_factory=dict)
    communication_compatibility: Dict[str, Any] = Field(default_factory=dict)
    thermal_compatibility: Dict[str, Any] = Field(default_factory=dict)
    overall_compatibility_score: float
    issues: List[CompatibilityIssue] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


class ElectronicsArchitectureRequest(BaseModel):
    """Request schema for electronics architecture generation."""
    project_id: str
    requirements: Dict[str, Any] = Field(default_factory=dict)


class ElectronicsArchitectureResponse(BaseModel):
    """Response schema for electronics architecture generation."""
    id: str
    project_id: str
    power_tree: Dict[str, Any] = Field(default_factory=dict)
    signal_architecture: Dict[str, Any] = Field(default_factory=dict)
    communication_architecture: Dict[str, Any] = Field(default_factory=dict)
    subsystem_architecture: Dict[str, Any] = Field(default_factory=dict)
    components: List[Component] = Field(default_factory=list)
    documentation: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: Optional[float] = None
    created_at: datetime
