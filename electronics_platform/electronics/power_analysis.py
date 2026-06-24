"""
Power Analysis — computes power budget, distribution, and thermal estimates.
"""
import numpy as np
from typing import List, Dict, Tuple
from electronics_platform.schemas.models import Component, Schematic

class PowerAnalysis:
    """Analyzes power distribution in a circuit."""
    
    # Typical power consumption by component category (Watts)
    TYPICAL_POWER = {
        "MICROCONTROLLER": 0.5,
        "SENSOR": 0.05,
        "LED": 0.02,
        "REGULATOR": 0.1,  # Quiescent
        "IC": 0.2,
        "RESISTOR": 0.0,  # Computed from circuit
        "CAPACITOR": 0.0,
    }
    
    def compute_power_budget(self, schematic: Schematic,
                            node_voltages: Dict[str, float]) -> Dict:
        """Compute total power budget for a schematic."""
        total_power = 0.0
        rail_power = {}
        component_power = {}
        
        for comp in schematic.components:
            # Estimate power based on category
            base_power = self.TYPICAL_POWER.get(comp.category.value, 0.0)
            
            # Add resistive losses
            if comp.category.value == "RESISTOR":
                # Find voltage across resistor
                v_across = self._estimate_voltage_across(comp, schematic.nets, node_voltages)
                try:
                    r_value = self._parse_value(comp.value)
                    if r_value > 0:
                        base_power = v_across ** 2 / r_value
                except Exception:
                    pass
                    
            component_power[comp.ref] = base_power
            total_power += base_power
            
            # Attribute to power rail (simplified — assumes VCC)
            rail = "VCC"
            rail_power[rail] = rail_power.get(rail, 0) + base_power
            
        return {
            "total_power_w": total_power,
            "rail_power": rail_power,
            "component_power": component_power,
            "hottest_components": sorted(component_power.items(), key=lambda x: x[1], reverse=True)[:5]
        }
        
    def _estimate_voltage_across(self, comp: Component, nets: List,
                                 node_voltages: Dict[str, float]) -> float:
        """Estimate voltage across a 2-terminal component."""
        if len(comp.pins) < 2:
            return 0.0
            
        # Find nets for pins
        net_a = net_b = None
        for net in nets:
            for ref, pin in net.connections:
                if ref == comp.ref and pin == comp.pins[0].number:
                    net_a = net.name
                elif ref == comp.ref and pin == comp.pins[1].number:
                    net_b = net.name
                    
        v_a = node_voltages.get(net_a, 0.0)
        v_b = node_voltages.get(net_b, 0.0)
        return abs(v_a - v_b)
        
    def _parse_value(self, value_str: str) -> float:
        """Parse component value string."""
        val_str = value_str.upper().strip()
        multipliers = {"K": 1e3, "MEG": 1e6, "M": 1e-3, "U": 1e-6, "N": 1e-9, "P": 1e-12}
        for suffix, mult in multipliers.items():
            if val_str.endswith(suffix):
                return float(val_str[:-len(suffix)]) * mult
        return float(val_str)
        
    def estimate_thermal_rise(self, power_w: float,
                             thermal_resistance_c_w: float = 50.0,
                             ambient_c: float = 25.0) -> Dict[str, float]:
        """Estimate junction temperature rise."""
        delta_t = power_w * thermal_resistance_c_w
        t_junction = ambient_c + delta_t
        return {
            "power_w": power_w,
            "thermal_resistance_c_w": thermal_resistance_c_w,
            "delta_t_c": delta_t,
            "junction_temp_c": t_junction,
            "ambient_c": ambient_c
        }
        
    def size_battery(self, total_power_w: float, runtime_hours: float,
                    battery_voltage_v: float = 3.7, efficiency: float = 0.9) -> Dict:
        """Size a battery for required runtime."""
        energy_wh = total_power_w * runtime_hours / efficiency
        capacity_mah = (energy_wh / battery_voltage_v) * 1000
        return {
            "energy_wh": energy_wh,
            "capacity_mah": capacity_mah,
            "battery_voltage_v": battery_voltage_v,
            "runtime_hours": runtime_hours,
            "efficiency": efficiency
        }
