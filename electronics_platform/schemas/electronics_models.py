from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Tuple
import uuid
from datetime import datetime
from enum import Enum
from electronics_platform.schemas.models import PCBBoard

class MCUFamily(str, Enum):
    STM32F0 = "STM32F0"
    STM32F1 = "STM32F1"
    STM32F4 = "STM32F4"
    STM32H7 = "STM32H7"
    ESP32 = "ESP32"
    ESP32S3 = "ESP32S3"
    RP2040 = "RP2040"
    AVR_ATMEGA = "AVR_ATMEGA"
    AVR_ATTINY = "AVR_ATTINY"

class PeripheralType(str, Enum):
    UART = "UART"
    SPI = "SPI"
    I2C = "I2C"
    ADC = "ADC"
    DAC = "DAC"
    PWM = "PWM"
    TIMER = "TIMER"
    CAN = "CAN"
    USB = "USB"
    ETHERNET = "ETHERNET"
    GPIO = "GPIO"
    DMA = "DMA"

class PinAllocationStatus(str, Enum):
    UNALLOCATED = "UNALLOCATED"
    ALLOCATED = "ALLOCATED"
    CONFLICT = "CONFLICT"
    RESERVED = "RESERVED"

class GerberLayer(str, Enum):
    TOP_COPPER = "GTL"
    BOTTOM_COPPER = "GBL"
    INNER1_COPPER = "G1"
    INNER2_COPPER = "G2"
    TOP_SILKSCREEN = "GTO"
    BOTTOM_SILKSCREEN = "GBO"
    TOP_SOLDERMASK = "GTS"
    BOTTOM_SOLDERMASK = "GBS"
    TOP_PASTE = "GTP"
    BOTTOM_PASTE = "GBP"
    BOARD_OUTLINE = "GKO"
    DRILL = "DRILL"

class MCUInfo(BaseModel):
    """Microcontroller definition."""
    part_number: str
    family: MCUFamily
    manufacturer: str
    package: str
    footprint: str
    flash_kb: int
    ram_kb: int
    clock_max_mhz: int
    voltage_min_v: float
    voltage_max_v: float
    gpio_count: int
    peripherals: Dict[PeripheralType, int] = Field(default_factory=dict)
    adc_channels: int = 0
    adc_resolution_bits: int = 12
    dac_channels: int = 0
    pwm_channels: int = 0
    dma_channels: int = 0
    price_usd: float = 0.0
    pinout: Dict[str, Dict[str, Any]] = Field(default_factory=dict)  # pin -> {functions: [...]}
    status: str = "ACTIVE"

class PinAssignment(BaseModel):
    """A single pin assignment."""
    pin_number: str
    pin_name: str
    function: str
    peripheral: Optional[str] = None
    signal_name: Optional[str] = None
    direction: str = "BIDIR"  # INPUT, OUTPUT, BIDIR
    status: PinAllocationStatus = PinAllocationStatus.UNALLOCATED
    constraints: Dict[str, Any] = Field(default_factory=dict)

class FirmwarePlan(BaseModel):
    """Firmware architecture plan."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mcu_part: str
    mcu_family: MCUFamily
    pin_assignments: List[PinAssignment] = Field(default_factory=list)
    peripheral_config: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    clock_config: Dict[str, Any] = Field(default_factory=dict)
    memory_map: Dict[str, Any] = Field(default_factory=dict)
    rtos_required: bool = False
    driver_modules: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CostEstimate(BaseModel):
    """Cost estimate for a design."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_name: str
    quantity: int = 1
    component_cost_usd: float = 0.0
    pcb_fab_cost_usd: float = 0.0
    assembly_cost_usd: float = 0.0
    shipping_cost_usd: float = 0.0
    total_cost_usd: float = 0.0
    cost_per_unit_usd: float = 0.0
    breakdown: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ManufacturingPackage(BaseModel):
    """Complete manufacturing package."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_name: str
    pcb_id: str
    bom_id: str
    gerber_files: Dict[str, str] = Field(default_factory=dict)  # layer -> content
    drill_file: Optional[str] = None
    pick_and_place_file: Optional[str] = None
    assembly_drawing: Optional[str] = None
    fab_notes: str = ""
    assembly_notes: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SignalIntegrityReport(BaseModel):
    """Signal integrity analysis report."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pcb_id: str
    high_speed_nets: List[Dict[str, Any]] = Field(default_factory=list)
    impedance_violations: List[Dict[str, Any]] = Field(default_factory=list)
    crosstalk_risks: List[Dict[str, Any]] = Field(default_factory=list)
    length_mismatches: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    status: str = "PASS"

class PowerIntegrityReport(BaseModel):
    """Power integrity analysis report."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pcb_id: str
    power_rails: List[Dict[str, Any]] = Field(default_factory=list)
    ir_drop_violations: List[Dict[str, Any]] = Field(default_factory=list)
    decoupling_recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    pdn_impedance: Dict[str, Any] = Field(default_factory=dict)
    status: str = "PASS"
