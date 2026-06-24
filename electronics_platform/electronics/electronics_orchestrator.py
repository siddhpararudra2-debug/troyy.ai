"""
Electronics Orchestrator — coordinates the entire electronics design flow.
"""
from typing import Dict, List, Optional
from electronics_platform.schemas.models import Schematic, Component, Net, Pin, BOM
from electronics_platform.schemas.enums import ComponentCategory
from electronics_platform.electronics.circuit_engine import CircuitEngine
from electronics_platform.electronics.component_selector import ComponentSelector
from electronics_platform.electronics.power_analysis import PowerAnalysis

class ElectronicsOrchestrator:
    """Top-level orchestrator for electronics design."""
    
    def __init__(self, component_db):
        self.circuit_engine = CircuitEngine()
        self.selector = ComponentSelector(component_db)
        self.power = PowerAnalysis()
        self.db = component_db
        
    def create_voltage_divider(self, v_in: float, v_out: float,
                              i_quiescent_a: float = 0.001) -> Schematic:
        """Create a voltage divider circuit."""
        # Calculate resistor values
        r2 = v_out / i_quiescent_a
        r1 = (v_in - v_out) / i_quiescent_a
        
        # Select standard values
        r1_std = self._nearest_e24(r1)
        r2_std = self._nearest_e24(r2)
        
        # Build schematic
        components = [
            Component(
                ref="R1", value=self._format_value(r1_std), footprint="Resistor_SMD:R_0402_1005Metric",
                category=ComponentCategory.RESISTOR,
                pins=[Pin(number="1", name="A", pin_type="PASSIVE"),
                      Pin(number="2", name="B", pin_type="PASSIVE")]
            ),
            Component(
                ref="R2", value=self._format_value(r2_std), footprint="Resistor_SMD:R_0402_1005Metric",
                category=ComponentCategory.RESISTOR,
                pins=[Pin(number="1", name="A", pin_type="PASSIVE"),
                      Pin(number="2", name="B", pin_type="PASSIVE")]
            )
        ]
        
        nets = [
            Net(name="VIN", connections=[("R1", "1")], is_power=True),
            Net(name="VOUT", connections=[("R1", "2"), ("R2", "1")]),
            Net(name="GND", connections=[("R2", "2")], is_ground=True)
        ]
        
        actual_vout = v_in * r2_std / (r1_std + r2_std)
        
        schematic = Schematic(
            name=f"Voltage Divider {v_in}V to {v_out}V",
            components=components,
            nets=nets,
            power_rails={"VIN": v_in, "VOUT": actual_vout}
        )
        
        return schematic
        
    def create_rc_lowpass(self, cutoff_hz: float, impedance_ohm: float = 10000) -> Schematic:
        """Create an RC low-pass filter."""
        r = impedance_ohm
        c = 1.0 / (2 * 3.14159 * cutoff_hz * r)
        
        r_std = self._nearest_e24(r)
        c_std = self._nearest_capacitor(c)
        
        components = [
            Component(
                ref="R1", value=self._format_value(r_std), footprint="Resistor_SMD:R_0402_1005Metric",
                category=ComponentCategory.RESISTOR,
                pins=[Pin(number="1", name="A", pin_type="PASSIVE"),
                      Pin(number="2", name="B", pin_type="PASSIVE")]
            ),
            Component(
                ref="C1", value=self._format_value(c_std), footprint="Capacitor_SMD:C_0402_1005Metric",
                category=ComponentCategory.CAPACITOR,
                pins=[Pin(number="1", name="A", pin_type="PASSIVE"),
                      Pin(number="2", name="B", pin_type="PASSIVE")]
            )
        ]
        
        nets = [
            Net(name="VIN", connections=[("R1", "1")], is_power=True),
            Net(name="VOUT", connections=[("R1", "2"), ("C1", "1")]),
            Net(name="GND", connections=[("C1", "2")], is_ground=True)
        ]
        
        actual_fc = 1.0 / (2 * 3.14159 * r_std * c_std)
        
        schematic = Schematic(
            name=f"RC Low-Pass Filter {cutoff_hz}Hz",
            components=components,
            nets=nets,
            power_rails={"VIN": 3.3}
        )
        
        return schematic
        
    def analyze_schematic(self, schematic: Schematic) -> Dict:
        """Run full analysis on a schematic."""
        # Nodal analysis
        voltages = self.circuit_engine.nodal_analysis(schematic.components, schematic.nets, {})
        
        # Power analysis
        power_budget = self.power.compute_power_budget(schematic, voltages)
        
        # ERC (Electrical Rules Check)
        erc_findings = self._run_erc(schematic)
        
        return {
            "node_voltages": voltages,
            "power_budget": power_budget,
            "erc_findings": erc_findings,
            "status": "PASS" if not any(f["severity"] == "ERROR" for f in erc_findings) else "FAIL"
        }
        
    def _run_erc(self, schematic: Schematic) -> List[Dict]:
        """Run Electrical Rules Check."""
        findings = []
        
        # Check for floating pins
        connected_pins = set()
        for net in schematic.nets:
            for conn in net.connections:
                connected_pins.add(conn)
                
        for comp in schematic.components:
            for pin in comp.pins:
                if (comp.ref, pin.number) not in connected_pins:
                    findings.append({
                        "severity": "WARNING",
                        "category": "ERC",
                        "message": f"Floating pin: {comp.ref}.{pin.number}",
                        "component_ref": comp.ref
                    })
                    
        # Check for power rail presence
        has_power = any(net.is_power for net in schematic.nets)
        has_ground = any(net.is_ground for net in schematic.nets)
        
        if not has_power:
            findings.append({
                "severity": "ERROR",
                "category": "ERC",
                "message": "No power rail defined"
            })
        if not has_ground:
            findings.append({
                "severity": "ERROR",
                "category": "ERC",
                "message": "No ground defined"
            })
            
        # Check for output-to-output shorts
        for net in schematic.nets:
            output_count = 0
            for ref, pin_num in net.connections:
                comp = next((c for c in schematic.components if c.ref == ref), None)
                if comp:
                    pin = next((p for p in comp.pins if p.number == pin_num), None)
                    if pin and pin.pin_type == "OUTPUT":
                        output_count += 1
            if output_count > 1:
                findings.append({
                    "severity": "ERROR",
                    "category": "ERC",
                    "message": f"Shorted outputs on net {net.name}",
                    "component_ref": net.name
                })
                
        return findings
        
    def _nearest_e24(self, value: float) -> float:
        """Find nearest E24 standard resistor value."""
        e24 = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
               3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]
        
        if value <= 0:
            return e24[0]
            
        # Find decade
        import math
        decade = math.floor(math.log10(value))
        normalized = value / (10 ** decade)
        
        # Find nearest E24 value
        nearest = min(e24, key=lambda x: abs(x - normalized))
        return nearest * (10 ** decade)
        
    def _nearest_capacitor(self, value: float) -> float:
        """Find nearest standard capacitor value (E6 series)."""
        e6 = [1.0, 1.5, 2.2, 3.3, 4.7, 6.8]
        import math
        if value <= 0:
            return e6[0]
        decade = math.floor(math.log10(value))
        normalized = value / (10 ** decade)
        nearest = min(e6, key=lambda x: abs(x - normalized))
        return nearest * (10 ** decade)
        
    def _format_value(self, value: float) -> str:
        """Format a value with appropriate suffix."""
        if value >= 1e6:
            return f"{value/1e6:.2f}M"
        elif value >= 1e3:
            return f"{value/1e3:.2f}K"
        elif value >= 1:
            return f"{value:.2f}"
        elif value >= 1e-3:
            return f"{value*1e3:.2f}m"
        elif value >= 1e-6:
            return f"{value*1e6:.2f}u"
        elif value >= 1e-9:
            return f"{value*1e9:.2f}n"
        else:
            return f"{value*1e12:.2f}p"
