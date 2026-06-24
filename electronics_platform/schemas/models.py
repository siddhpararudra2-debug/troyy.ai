from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Tuple
import uuid
from datetime import datetime
from electronics_platform.schemas.enums import ComponentCategory, ComponentStatus, SimulationType, DesignRuleClass

class Pin(BaseModel):
    """A component pin."""
    number: str
    name: str
    pin_type: str  # "INPUT", "OUTPUT", "BIDIR", "POWER_IN", "POWER_OUT", "PASSIVE"
    net: Optional[str] = None

class Component(BaseModel):
    """An electronic component."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ref: str  # Reference designator (R1, C1, U1, etc.)
    value: str
    footprint: str
    category: ComponentCategory
    manufacturer: Optional[str] = None
    mpn: Optional[str] = None  # Manufacturer Part Number
    pins: List[Pin] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)
    position: Optional[Tuple[float, float]] = None  # (x, y) in mm
    rotation: float = 0.0  # degrees

class Net(BaseModel):
    """An electrical net connecting component pins."""
    name: str
    net_class: DesignRuleClass = DesignRuleClass.SIGNAL
    connections: List[Tuple[str, str]] = Field(default_factory=list)  # [(ref, pin), ...]
    is_power: bool = False
    is_ground: bool = False
    high_speed: bool = False

class Schematic(BaseModel):
    """A complete schematic."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    version: str = "1.0"
    components: List[Component] = Field(default_factory=list)
    nets: List[Net] = Field(default_factory=list)
    power_rails: Dict[str, float] = Field(default_factory=dict)  # {name: voltage}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    content_hash: str = ""

class PCBBoard(BaseModel):
    """A PCB layout."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    schematic_id: str
    layers: int = 2
    board_outline: List[Tuple[float, float]] = Field(default_factory=list)  # mm
    components: List[Component] = Field(default_factory=list)  # with positions
    traces: List[Dict[str, Any]] = Field(default_factory=list)
    vias: List[Dict[str, Any]] = Field(default_factory=list)
    zones: List[Dict[str, Any]] = Field(default_factory=list)  # Copper pours
    drill_hits: List[Tuple[float, float]] = Field(default_factory=list)
    design_rules: Dict[str, float] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ComponentInfo(BaseModel):
    """Component database entry."""
    mpn: str
    manufacturer: str
    category: ComponentCategory
    description: str
    package: str  # e.g., "0402", "SOT-23", "QFP-64"
    footprint: str  # KiCad footprint name
    value_range: Optional[str] = None
    voltage_rating: Optional[float] = None
    current_rating: Optional[float] = None
    power_rating: Optional[float] = None
    tolerance: Optional[float] = None
    price_usd: float = 0.0
    stock_available: int = 0
    status: ComponentStatus = ComponentStatus.ACTIVE
    properties: Dict[str, Any] = Field(default_factory=dict)
    datasheet_url: Optional[str] = None
    alternatives: List[str] = Field(default_factory=list)
    lifecycle_stage: str = "Production"
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class BOMLine(BaseModel):
    """A single line in a Bill of Materials."""
    ref_des: List[str]  # Reference designators sharing same part
    quantity: int
    value: str
    footprint: str
    mpn: str
    manufacturer: str
    description: str
    unit_price_usd: float
    total_price_usd: float
    status: ComponentStatus
    alternatives: List[str] = Field(default_factory=list)

class BOM(BaseModel):
    """Complete Bill of Materials."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_name: str
    version: str = "1.0"
    lines: List[BOMLine] = Field(default_factory=list)
    total_cost_usd: float = 0.0
    unique_parts: int = 0
    total_components: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SimulationResult(BaseModel):
    """Result of a SPICE simulation."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    simulation_type: SimulationType
    netlist: str
    status: str  # "SUCCESS", "FAILED", "DID_NOT_CONVERGE"
    waveforms: Dict[str, List[float]] = Field(default_factory=dict)  # {signal_name: [values]}
    time_vector: Optional[List[float]] = None
    frequency_vector: Optional[List[float]] = None
    operating_point: Dict[str, float] = Field(default_factory=dict)
    error_message: Optional[str] = None
    computation_time_ms: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ValidationFinding(BaseModel):
    """A single validation finding."""
    severity: str  # "ERROR", "WARNING", "INFO"
    category: str  # "ELECTRICAL", "THERMAL", "DRC", "MANUFACTURABILITY"
    message: str
    component_ref: Optional[str] = None
    recommendation: Optional[str] = None

class ValidationReport(BaseModel):
    """Complete validation report."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_id: str
    target_type: str  # "SCHEMATIC", "PCB"
    status: str  # "PASS", "FAIL", "WARNING"
    findings: List[ValidationFinding] = Field(default_factory=list)
    drc_passed: bool = True
    erc_passed: bool = True
    thermal_ok: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
