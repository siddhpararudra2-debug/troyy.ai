"""
Peripheral Mapper — maps firmware requirements to MCU peripherals.
"""
from typing import List, Dict, Optional
from electronics_platform.schemas.electronics_models import MCUInfo, PeripheralType

class PeripheralMapper:
    """Maps system requirements to MCU peripheral configuration."""
    
    # Peripheral usage patterns
    PERIPHERAL_USAGE = {
        "flight_controller": {
            PeripheralType.UART: 3,  # GPS, telemetry, debug
            PeripheralType.SPI: 2,   # IMU, barometer
            PeripheralType.I2C: 1,   # Sensors
            PeripheralType.PWM: 8,   # ESC outputs
            PeripheralType.ADC: 4,   # Battery, current
            PeripheralType.CAN: 1,   # Optional
        },
        "sensor_node": {
            PeripheralType.UART: 1,  # Debug/telemetry
            PeripheralType.I2C: 2,   # Multiple sensors
            PeripheralType.SPI: 1,   # SD card or radio
            PeripheralType.ADC: 4,   # Analog sensors
        },
        "motor_controller": {
            PeripheralType.PWM: 6,   # Motor phases
            PeripheralType.ADC: 3,   # Current sensing
            PeripheralType.UART: 1,  # Communication
            PeripheralType.CAN: 1,   # CAN bus
        },
        "robot_arm": {
            PeripheralType.PWM: 6,   # Servo outputs
            PeripheralType.UART: 2,  # Communication
            PeripheralType.CAN: 2,   # Joint communication
            PeripheralType.ADC: 6,   # Force/torque sensors
            PeripheralType.SPI: 1,   # Encoders
        },
    }
    
    def map_application(self, application_type: str,
                       custom_requirements: Dict = None) -> Dict[str, int]:
        """Map application type to peripheral requirements."""
        base = self.PERIPHERAL_USAGE.get(application_type, {})
        
        if custom_requirements:
            # Merge with custom requirements (custom takes precedence)
            merged = base.copy()
            for periph, count in custom_requirements.items():
                try:
                    periph_enum = PeripheralType(periph.upper())
                    merged[periph_enum] = count
                except ValueError:
                    pass
            return merged
            
        return base
        
    def estimate_clock_requirement(self, application: str, 
                                  control_loop_hz: float = 1000) -> int:
        """Estimate required MCU clock speed."""
        # Rule of thumb: clock should be 100x control loop frequency
        base_clock = control_loop_hz * 100
        
        # Application-specific multipliers
        multipliers = {
            "flight_controller": 2.0,  # Fast control loops
            "motor_controller": 1.5,
            "sensor_node": 0.5,
            "robot_arm": 1.5,
        }
        
        required = base_clock * multipliers.get(application, 1.0)
        # Round up to nearest standard clock
        standard_clocks = [16, 24, 48, 72, 84, 100, 120, 168, 216, 240, 480]
        for clock in standard_clocks:
            if clock * 1e6 >= required:
                return clock
        return 480
        
    def estimate_memory_requirement(self, application: str,
                                   rtos: bool = False) -> Dict[str, int]:
        """Estimate flash and RAM requirements."""
        # Base memory by application
        base_flash = {
            "flight_controller": 64,
            "motor_controller": 32,
            "sensor_node": 16,
            "robot_arm": 128,
        }
        base_ram = {
            "flight_controller": 20,
            "motor_controller": 8,
            "sensor_node": 4,
            "robot_arm": 32,
        }
        
        flash = base_flash.get(application, 32)
        ram = base_ram.get(application, 8)
        
        # RTOS adds overhead
        if rtos:
            flash += 32  # RTOS kernel + libs
            ram += 16    # RTOS stacks + heap
            
        # Safety margin (2x)
        return {
            "flash_kb": flash * 2,
            "ram_kb": ram * 2
        }
