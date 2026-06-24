"""
Pin Allocator — assigns MCU pins to functions using constraint satisfaction.
Uses backtracking search with forward checking.
"""
from typing import List, Dict, Set, Optional, Tuple
from electronics_platform.schemas.electronics_models import (
    MCUInfo, PinAssignment, PinAllocationStatus, PeripheralType
)

class PinAllocator:
    """Allocates MCU pins to required functions using CSP."""
    
    def __init__(self, mcu: MCUInfo):
        self.mcu = mcu
        self.assignments: Dict[str, PinAssignment] = {}
        self.allocated_pins: Set[str] = set()
        
    def allocate(self, requirements: List[Dict]) -> Dict:
        """
        Allocate pins to requirements.
        requirements: [
            {"function": "UART1_TX", "peripheral": "UART", "direction": "OUTPUT"},
            {"function": "UART1_RX", "peripheral": "UART", "direction": "INPUT"},
            {"function": "IMU_CS", "peripheral": "SPI", "direction": "OUTPUT"},
            ...
        ]
        Returns: {
            "success": bool,
            "assignments": [PinAssignment],
            "unassigned": [...],
            "conflicts": [...]
        }
        """
        # Reset state
        self.assignments = {}
        self.allocated_pins = set()
        
        # Build pin capability map: pin -> [possible functions]
        pin_capabilities = self._build_pin_capability_map()
        
        # Group requirements by peripheral (for efficient allocation)
        grouped_reqs = self._group_by_peripheral(requirements)
        
        # Allocate pins using backtracking
        success = self._backtrack_allocate(grouped_reqs, pin_capabilities, 0)
        
        if success:
            return {
                "success": True,
                "assignments": list(self.assignments.values()),
                "unassigned": [],
                "conflicts": [],
                "utilization_pct": len(self.allocated_pins) / len(pin_capabilities) * 100
            }
        else:
            # Return partial results with unassigned
            unassigned = [r for r in requirements 
                         if r["function"] not in self.assignments]
            return {
                "success": False,
                "assignments": list(self.assignments.values()),
                "unassigned": unassigned,
                "conflicts": self._detect_conflicts(requirements),
                "utilization_pct": len(self.allocated_pins) / len(pin_capabilities) * 100
            }
            
    def _build_pin_capability_map(self) -> Dict[str, List[str]]:
        """Build map of pin -> possible functions from MCU pinout."""
        capabilities = {}
        
        if self.mcu.pinout:
            # Use actual MCU pinout data
            for pin, info in self.mcu.pinout.items():
                functions = info.get("functions", [])
                capabilities[pin] = functions
        else:
            # Generate synthetic pinout based on peripheral counts
            pin_num = 1
            for periph_type, count in self.mcu.peripherals.items():
                for i in range(count):
                    # Each peripheral instance gets some pins
                    if periph_type == PeripheralType.UART:
                        capabilities[f"P{pin_num}"] = [f"UART{i+1}_TX", f"UART{i+1}_RX"]
                        pin_num += 2
                    elif periph_type == PeripheralType.SPI:
                        capabilities[f"P{pin_num}"] = [f"SPI{i+1}_SCK", f"SPI{i+1}_MOSI",
                                                       f"SPI{i+1}_MISO", f"SPI{i+1}_CS"]
                        pin_num += 4
                    elif periph_type == PeripheralType.I2C:
                        capabilities[f"P{pin_num}"] = [f"I2C{i+1}_SCL", f"I2C{i+1}_SDA"]
                        pin_num += 2
                    elif periph_type == PeripheralType.ADC:
                        for ch in range(self.mcu.adc_channels // max(count, 1)):
                            capabilities[f"P{pin_num}"] = [f"ADC{i+1}_IN{ch}"]
                            pin_num += 1
                    elif periph_type == PeripheralType.PWM:
                        for ch in range(self.mcu.pwm_channels // max(count, 1)):
                            capabilities[f"P{pin_num}"] = [f"PWM{i+1}_CH{ch}"]
                            pin_num += 1
                    elif periph_type == PeripheralType.GPIO:
                        capabilities[f"P{pin_num}"] = [f"GPIO{pin_num}"]
                        pin_num += 1
                        
            # Fill remaining pins as GPIO
            while pin_num <= self.mcu.gpio_count:
                capabilities[f"P{pin_num}"] = [f"GPIO{pin_num}"]
                pin_num += 1
                
        return capabilities
        
    def _group_by_peripheral(self, requirements: List[Dict]) -> Dict[str, List[Dict]]:
        """Group requirements by peripheral type for efficient allocation."""
        grouped = {}
        for req in requirements:
            periph = req.get("peripheral", "GPIO")
            grouped.setdefault(periph, []).append(req)
        return grouped
        
    def _backtrack_allocate(self, grouped_reqs: Dict[str, List[Dict]],
                           pin_capabilities: Dict[str, List[str]],
                           group_idx: int) -> bool:
        """Backtracking search for pin allocation."""
        groups = list(grouped_reqs.items())
        if group_idx >= len(groups):
            return True  # All groups allocated
            
        periph, reqs = groups[group_idx]
        
        # Try to allocate all requirements in this group
        if self._allocate_group(reqs, pin_capabilities):
            # Recurse to next group
            if self._backtrack_allocate(grouped_reqs, pin_capabilities, group_idx + 1):
                return True
            # Backtrack: undo this group's allocations
            for req in reqs:
                if req["function"] in self.assignments:
                    pin = self.assignments[req["function"]].pin_number
                    self.allocated_pins.remove(pin)
                    del self.assignments[req["function"]]
                    
        return False
        
    def _allocate_group(self, reqs: List[Dict],
                       pin_capabilities: Dict[str, List[str]]) -> bool:
        """Allocate a group of related requirements (e.g., all UART1 pins)."""
        for req in reqs:
            function = req["function"]
            direction = req.get("direction", "BIDIR")
            
            # Find a pin that supports this function
            allocated = False
            for pin, functions in pin_capabilities.items():
                if pin in self.allocated_pins:
                    continue
                # Check if this pin supports the required function
                if any(function in f or f in function for f in functions):
                    # Allocate
                    assignment = PinAssignment(
                        pin_number=pin,
                        pin_name=pin,
                        function=function,
                        peripheral=req.get("peripheral"),
                        signal_name=req.get("signal_name", function),
                        direction=direction,
                        status=PinAllocationStatus.ALLOCATED
                    )
                    self.assignments[function] = assignment
                    self.allocated_pins.add(pin)
                    allocated = True
                    break
                    
            if not allocated:
                # Try to allocate as GPIO
                for pin, functions in pin_capabilities.items():
                    if pin in self.allocated_pins:
                        continue
                    if any("GPIO" in f for f in functions):
                        assignment = PinAssignment(
                            pin_number=pin,
                            pin_name=pin,
                            function=function,
                            peripheral="GPIO",
                            signal_name=function,
                            direction=direction,
                            status=PinAllocationStatus.ALLOCATED
                        )
                        self.assignments[function] = assignment
                        self.allocated_pins.add(pin)
                        allocated = True
                        break
                        
            if not allocated:
                return False
                
        return True
        
    def _detect_conflicts(self, requirements: List[Dict]) -> List[Dict]:
        """Detect allocation conflicts."""
        conflicts = []
        # Check for duplicate function names
        seen = {}
        for req in requirements:
            fn = req["function"]
            if fn in seen:
                conflicts.append({
                    "function": fn,
                    "message": f"Duplicate function requirement: {fn}"
                })
            seen[fn] = req
        return conflicts
