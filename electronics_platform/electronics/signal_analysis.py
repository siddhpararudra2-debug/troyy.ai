"""
Signal Analysis — impedance calculations, crosstalk estimation, high-speed checks.
"""
import numpy as np
from typing import List, Dict, Tuple, Optional

class SignalAnalysis:
    """Analyzes signal integrity aspects of a design."""
    
    # Typical PCB material properties
    FR4_ER = 4.5  # Relative permittivity
    FR4_LOSS_TANGENT = 0.02
    C0 = 3e8  # Speed of light in vacuum (m/s)
    
    def microstrip_impedance(self, trace_width_mm: float, dielectric_height_mm: float,
                            trace_thickness_mm: float = 0.035, er: float = None) -> float:
        """
        Calculate microstrip characteristic impedance using IPC-2141 formulas.
        Returns impedance in Ohms.
        """
        er = er or self.FR4_ER
        w = trace_width_mm
        h = dielectric_height_mm
        t = trace_thickness_mm
        
        # Width-to-height ratio
        w_h = w / h
        
        if w_h < 1:
            # Narrow trace formula
            z0 = (60 / np.sqrt(er)) * np.log(8 * h / w + w / (4 * h))
        else:
            # Wide trace formula
            eff_er = (er + 1) / 2 + (er - 1) / 2 * (1 / np.sqrt(1 + 12 * h / w))
            z0 = (60 / np.sqrt(eff_er)) / (w_h + 1.393 + 0.667 * np.log(w_h + 1.444))
            
        return float(z0)
        
    def stripline_impedance(self, trace_width_mm: float, dielectric_height_mm: float,
                           er: float = None) -> float:
        """Calculate stripline (internal layer) characteristic impedance."""
        er = er or self.FR4_ER
        w = trace_width_mm
        b = 2 * dielectric_height_mm  # Distance between reference planes
        
        # Approximate formula
        z0 = (60 / np.sqrt(er)) * np.log(4 * b / (0.67 * np.pi * (0.8 * w + trace_width_mm * 0.1)))
        return float(z0)
        
    def effective_dielectric_constant(self, w_mm: float, h_mm: float, er: float = None) -> float:
        """Calculate effective dielectric constant for microstrip."""
        er = er or self.FR4_ER
        w_h = w_mm / h_mm
        eff_er = (er + 1) / 2 + (er - 1) / 2 * (1 / np.sqrt(1 + 12 / w_h))
        return float(eff_er)
        
    def propagation_delay(self, length_mm: float, er: float = None) -> float:
        """Calculate propagation delay in ps/mm."""
        er = er or self.FR4_ER
        # Delay per unit length: sqrt(er) / c
        delay_ps_per_mm = np.sqrt(er) / self.C0 * 1e12 / 1000
        return float(delay_ps_per_mm * length_mm)
        
    def critical_length(self, rise_time_ns: float, er: float = None) -> float:
        """
        Calculate critical trace length where transmission line effects matter.
        Rule of thumb: length > rise_time / (6 * propagation_delay_per_length)
        Returns length in mm.
        """
        er = er or self.FR4_ER
        # Propagation delay ~ 150 ps/inch for FR4 (~6 ps/mm)
        delay_per_mm = np.sqrt(er) * 3.33  # ps/mm
        
        # Critical length: where trace delay > 1/6 of rise time
        rise_time_ps = rise_time_ns * 1000
        critical_mm = rise_time_ps / (6 * delay_per_mm)
        return float(critical_mm)
        
    def crosstalk_estimate(self, aggressor_rise_ns: float, spacing_mm: float,
                          coupling_length_mm: float, h_mm: float) -> Dict[str, float]:
        """
        Estimate near-end and far-end crosstalk.
        Simplified model based on IPC-2141.
        """
        # Coupling coefficient (simplified)
        k = np.exp(-2.5 * spacing_mm / h_mm)
        
        # Near-end crosstalk (capacitive + inductive)
        next_coeff = k * 0.5  # Simplified
        
        # Far-end crosstalk (proportional to length for lossless)
        fext_coeff = k * coupling_length_mm / (10 * h_mm)
        
        return {
            "next_coefficient": float(next_coeff),
            "fext_coefficient": float(fext_coeff),
            "next_voltage_v": float(next_coeff * 3.3),  # Assuming 3.3V aggressor
            "fext_voltage_v": float(fext_coeff * 3.3),
            "recommendation": self._crosstalk_recommendation(next_coeff, fext_coeff)
        }
        
    def _crosstalk_recommendation(self, next_c: float, fext_c: float) -> str:
        if next_c > 0.1 or fext_c > 0.05:
            return "CRITICAL: Increase spacing or add guard traces"
        elif next_c > 0.05 or fext_c > 0.02:
            return "WARNING: Consider increasing spacing for sensitive signals"
        else:
            return "OK: Crosstalk within acceptable limits"
        
    def analyze_high_speed_net(self, net_name: str, frequency_mhz: float,
                              rise_time_ns: float, trace_length_mm: float,
                              trace_width_mm: float, target_impedance: float = 50.0,
                              layer_stackup: Dict = None) -> Dict:
        """Analyze a high-speed net for SI issues."""
        issues = []
        
        # Check if transmission line effects matter
        critical_length = self.critical_length(rise_time_ns)
        is_transmission_line = trace_length_mm > critical_length
        
        if is_transmission_line:
            issues.append({
                "severity": "WARNING",
                "message": f"Net {net_name} is electrically long ({trace_length_mm:.1f}mm > {critical_length:.1f}mm critical)",
                "recommendation": "Treat as transmission line — control impedance"
            })
            
        # Check impedance (assuming default 4-layer stackup: 0.2mm prepreg)
        h_mm = 0.2  # Default dielectric height
        if layer_stackup:
            h_mm = layer_stackup.get("prepreg_thickness_mm", 0.2)
            
        z0 = self.microstrip_impedance(trace_width_mm, h_mm)
        impedance_error_pct = abs(z0 - target_impedance) / target_impedance * 100
        
        if impedance_error_pct > 10:
            issues.append({
                "severity": "ERROR",
                "message": f"Impedance mismatch: {z0:.1f}Ω vs target {target_impedance}Ω ({impedance_error_pct:.1f}% error)",
                "recommendation": f"Adjust trace width to achieve {target_impedance}Ω"
            })
            
        # Bandwidth check (for digital signals)
        bandwidth_mhz = 0.35 / (rise_time_ns * 1e-3)  # MHz
        if frequency_mhz > bandwidth_mhz * 0.5:
            issues.append({
                "severity": "WARNING",
                "message": f"Signal frequency ({frequency_mhz}MHz) approaches bandwidth limit ({bandwidth_mhz:.0f}MHz)",
                "recommendation": "Reduce rise time or use faster material"
            })
            
        return {
            "net_name": net_name,
            "frequency_mhz": frequency_mhz,
            "rise_time_ns": rise_time_ns,
            "trace_length_mm": trace_length_mm,
            "critical_length_mm": critical_length,
            "is_transmission_line": is_transmission_line,
            "calculated_impedance_ohm": z0,
            "target_impedance_ohm": target_impedance,
            "impedance_error_pct": impedance_error_pct,
            "propagation_delay_ps": self.propagation_delay(trace_length_mm),
            "issues": issues,
            "status": "FAIL" if any(i["severity"] == "ERROR" for i in issues) else "PASS"
        }
