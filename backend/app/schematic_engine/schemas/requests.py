from pydantic import BaseModel, Field
from typing import List, Dict, Any

class SchematicGenerateRequest(BaseModel):
    project_name: str
    mcu_pinout: Dict[str, List[str]]  # e.g., {"PA0": ["ADC1_IN0", "TIM2_CH1"]}
    required_functions: Dict[str, int] # e.g., {"USART1_TX": 1, "I2C1_SCL": 1}
    power_rails: Dict[str, Dict[str, float]] # e.g., {"5V": {"voltage": 5.0, "current": 1.0}}
    input_voltage: float = 12.0
