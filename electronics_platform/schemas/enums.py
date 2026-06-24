from enum import Enum

class CircuitType(str, Enum):
    ANALOG = "ANALOG"
    DIGITAL = "DIGITAL"
    POWER = "POWER"
    MIXED_SIGNAL = "MIXED_SIGNAL"
    RF = "RF"
    SENSOR_INTERFACE = "SENSOR_INTERFACE"

class ComponentCategory(str, Enum):
    RESISTOR = "RESISTOR"
    CAPACITOR = "CAPACITOR"
    INDUCTOR = "INDUCTOR"
    DIODE = "DIODE"
    TRANSISTOR = "TRANSISTOR"
    IC = "IC"
    MICROCONTROLLER = "MICROCONTROLLER"
    SENSOR = "SENSOR"
    CONNECTOR = "CONNECTOR"
    CRYSTAL = "CRYSTAL"
    LED = "LED"
    REGULATOR = "REGULATOR"

class ComponentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    NRND = "NRND"  # Not Recommended for New Designs
    OBSOLETE = "OBSOLETE"
    PRELIMINARY = "PRELIMINARY"
    UNKNOWN = "UNKNOWN"

class SimulationType(str, Enum):
    DC = "DC"
    AC = "AC"
    TRANSIENT = "TRANSIENT"
    NOISE = "NOISE"
    OPERATING = "OPERATING"

class PCBLayer(str, Enum):
    F_CU = "F.Cu"       # Front copper
    B_CU = "B.Cu"       # Back copper
    IN1_CU = "In1.Cu"   # Inner layer 1
    IN2_CU = "In2.Cu"   # Inner layer 2
    F_SILK = "F.Silkscreen"
    B_SILK = "B.Silkscreen"
    F_MASK = "F.Mask"
    B_MASK = "B.Mask"
    EDGE_CUTS = "Edge.Cuts"

class DesignRuleClass(str, Enum):
    SIGNAL = "SIGNAL"
    POWER = "POWER"
    GROUND = "GROUND"
    HIGH_SPEED = "HIGH_SPEED"
    ANALOG = "ANALOG"
