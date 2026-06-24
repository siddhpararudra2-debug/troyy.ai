"""
Firmware Planner — creates complete firmware architecture plan.
"""
from typing import Dict, List, Optional
from electronics_platform.schemas.electronics_models import (
    FirmwarePlan, MCUInfo, PinAssignment, MCUFamily
)
from electronics_platform.firmware.mcu_selector import MCUSelector
from electronics_platform.firmware.peripheral_mapper import PeripheralMapper
from electronics_platform.firmware.pin_allocator import PinAllocator

class FirmwarePlanner:
    """Plans firmware architecture for a design."""
    
    def __init__(self):
        self.mcu_selector = MCUSelector()
        self.peripheral_mapper = PeripheralMapper()
        
    def plan(self, application: str, custom_requirements: Dict = None) -> Dict:
        """
        Create complete firmware plan.
        application: "flight_controller", "sensor_node", "motor_controller", etc.
        custom_requirements: optional overrides
        """
        # Step 1: Map application to peripheral requirements
        peripheral_reqs = self.peripheral_mapper.map_application(application, custom_requirements)
        
        # Step 2: Estimate memory and clock requirements
        memory_reqs = self.peripheral_mapper.estimate_memory_requirement(application)
        clock_mhz = self.peripheral_mapper.estimate_clock_requirement(application)
        
        # Step 3: Build MCU selection requirements
        mcu_requirements = {
            "flash_kb": memory_reqs["flash_kb"],
            "ram_kb": memory_reqs["ram_kb"],
            "clock_mhz": clock_mhz,
            "gpio": 20,  # Default
            "voltage_v": 3.3,
        }
        
        # Add peripheral requirements
        for periph, count in peripheral_reqs.items():
            mcu_requirements[periph.value.lower()] = count
            
        # Add custom requirements
        if custom_requirements:
            mcu_requirements.update(custom_requirements)
            
        # Step 4: Select MCU
        mcu_candidates = self.mcu_selector.select(mcu_requirements)
        if not mcu_candidates:
            return {
                "success": False,
                "error": "No MCU matches requirements",
                "requirements": mcu_requirements
            }
            
        best_mcu_dict = mcu_candidates[0]["mcu"]
        best_mcu = MCUInfo(**best_mcu_dict)
        
        # Step 5: Allocate pins
        pin_requirements = self._build_pin_requirements(application, peripheral_reqs)
        allocator = PinAllocator(best_mcu)
        allocation_result = allocator.allocate(pin_requirements)
        
        # Step 6: Build firmware plan
        plan = FirmwarePlan(
            mcu_part=best_mcu.part_number,
            mcu_family=best_mcu.family,
            pin_assignments=allocation_result["assignments"],
            peripheral_config=self._build_peripheral_config(peripheral_reqs),
            clock_config={
                "source": "HSE" if best_mcu.family in [MCUFamily.STM32F1, MCUFamily.STM32F4] else "Internal",
                "frequency_mhz": best_mcu.clock_max_mhz,
                "pll_multiplier": 1
            },
            memory_map={
                "flash_kb": best_mcu.flash_kb,
                "ram_kb": best_mcu.ram_kb,
                "application_kb": int(best_mcu.flash_kb * 0.7),
                "bootloader_kb": int(best_mcu.flash_kb * 0.1),
                "config_kb": int(best_mcu.flash_kb * 0.1),
                "heap_kb": int(best_mcu.ram_kb * 0.5),
                "stack_kb": int(best_mcu.ram_kb * 0.3)
            },
            rtos_required=application in ["flight_controller", "robot_arm"],
            driver_modules=self._determine_drivers(application, peripheral_reqs)
        )
        
        return {
            "success": True,
            "mcu_candidates": mcu_candidates[:5],
            "selected_mcu": best_mcu_dict,
            "pin_allocation": allocation_result,
            "firmware_plan": plan.model_dump(),
            "peripheral_requirements": {k.value: v for k, v in peripheral_reqs.items()},
            "memory_requirements": memory_reqs
        }
        
    def _build_pin_requirements(self, application: str,
                               peripheral_reqs: Dict) -> List[Dict]:
        """Build pin requirements from peripheral requirements."""
        requirements = []
        
        for periph, count in peripheral_reqs.items():
            if periph == PeripheralType.UART:
                for i in range(count):
                    requirements.extend([
                        {"function": f"UART{i+1}_TX", "peripheral": "UART", "direction": "OUTPUT"},
                        {"function": f"UART{i+1}_RX", "peripheral": "UART", "direction": "INPUT"},
                    ])
            elif periph == PeripheralType.SPI:
                for i in range(count):
                    requirements.extend([
                        {"function": f"SPI{i+1}_SCK", "peripheral": "SPI", "direction": "OUTPUT"},
                        {"function": f"SPI{i+1}_MOSI", "peripheral": "SPI", "direction": "OUTPUT"},
                        {"function": f"SPI{i+1}_MISO", "peripheral": "SPI", "direction": "INPUT"},
                        {"function": f"SPI{i+1}_CS", "peripheral": "SPI", "direction": "OUTPUT"},
                    ])
            elif periph == PeripheralType.I2C:
                for i in range(count):
                    requirements.extend([
                        {"function": f"I2C{i+1}_SCL", "peripheral": "I2C", "direction": "BIDIR"},
                        {"function": f"I2C{i+1}_SDA", "peripheral": "I2C", "direction": "BIDIR"},
                    ])
            elif periph == PeripheralType.PWM:
                for i in range(count):
                    requirements.append({
                        "function": f"PWM_CH{i}", "peripheral": "PWM", "direction": "OUTPUT"
                    })
            elif periph == PeripheralType.ADC:
                for i in range(count):
                    requirements.append({
                        "function": f"ADC_IN{i}", "peripheral": "ADC", "direction": "INPUT"
                    })
            elif periph == PeripheralType.CAN:
                for i in range(count):
                    requirements.extend([
                        {"function": f"CAN{i+1}_TX", "peripheral": "CAN", "direction": "OUTPUT"},
                        {"function": f"CAN{i+1}_RX", "peripheral": "CAN", "direction": "INPUT"},
                    ])
                    
        return requirements
        
    def _build_peripheral_config(self, peripheral_reqs: Dict) -> Dict:
        """Build peripheral configuration."""
        config = {}
        for periph, count in peripheral_reqs.items():
            config[periph.value] = {
                "instances": count,
                "enabled": True,
                "baud_rate": self._default_baud_rate(periph),
                "clock_divider": 1
            }
        return config
        
    def _default_baud_rate(self, periph) -> int:
        defaults = {
            PeripheralType.UART: 115200,
            PeripheralType.SPI: 1000000,
            PeripheralType.I2C: 400000,
            PeripheralType.CAN: 500000,
        }
        return defaults.get(periph, 1000000)
        
    def _determine_drivers(self, application: str,
                          peripheral_reqs: Dict) -> List[str]:
        """Determine required firmware driver modules."""
        drivers = ["hal", "system", "clock"]
        
        for periph in peripheral_reqs.keys():
            drivers.append(periph.value.lower())
            
        if application == "flight_controller":
            drivers.extend(["imu", "barometer", "gps", "esc_control", "pid"])
        elif application == "motor_controller":
            drivers.extend(["motor_control", "current_sense", "encoder"])
        elif application == "robot_arm":
            drivers.extend(["servo", "kinematics", "trajectory"])
            
        return drivers
