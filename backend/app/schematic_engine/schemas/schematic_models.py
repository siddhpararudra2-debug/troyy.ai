from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Tuple
from app.schematic_engine.schemas.enums import NetType, PinDirection

class ComponentPin(BaseModel):
    name: str
    number: str
    direction: PinDirection
    net_type: NetType
    voltage_level: Optional[float] = None

class Component(BaseModel):
    ref: str
    value: str
    footprint: str
    pins: List[ComponentPin]

class NetConnection(BaseModel):
    comp_ref: str
    pin_name: str
    direction: PinDirection

class Net(BaseModel):
    name: str
    net_type: NetType
    voltage: Optional[float] = None
    connections: List[NetConnection] = Field(default_factory=list)

class SchematicNetlist(BaseModel):
    components: List[Component]
    nets: List[Net]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PowerRail(BaseModel):
    name: str
    voltage: float
    max_current_a: float
    source_component: Optional[str] = None

class PowerTree(BaseModel):
    input_voltage: float
    rails: List[PowerRail]
    regulators: List[Dict[str, Any]]
