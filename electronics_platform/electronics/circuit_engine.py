"""
Circuit Engine — symbolic circuit analysis using SymPy.
Performs nodal analysis, transfer function derivation, and impedance calculations.
"""
import sympy as sp
import numpy as np
from typing import Dict, List, Tuple, Optional
from electronics_platform.schemas.models import Component, Net

class CircuitEngine:
    """Symbolic circuit analysis engine."""
    
    def nodal_analysis(self, components: List[Component], nets: List[Net],
                      sources: Dict[str, float]) -> Dict[str, float]:
        """
        Perform DC nodal analysis using Modified Nodal Analysis (MNA).
        Returns node voltages.
        """
        # Identify unique nodes (excluding ground)
        node_set = set()
        for net in nets:
            if net.name != "GND" and not net.is_ground:
                node_set.add(net.name)
        
        nodes = sorted(node_set)
        n = len(nodes)
        node_idx = {name: i for i, name in enumerate(nodes)}
        
        if n == 0:
            return {}
            
        # Build conductance matrix G and current vector I
        G = np.zeros((n, n))
        I = np.zeros(n)
        
        for comp in components:
            pins = comp.pins
            if len(pins) < 2:
                continue
                
            # Get the nets connected to first two pins
            net_a = self._find_pin_net(comp.ref, pins[0].number, nets)
            net_b = self._find_pin_net(comp.ref, pins[1].number, nets)
            
            if net_a is None or net_b is None:
                continue
                
            # Get component value (resistance, conductance)
            value = self._get_component_value(comp)
            if value is None or value == 0:
                continue
                
            # Determine if resistor or other
            if comp.category.value in ["RESISTOR"]:
                g = 1.0 / value  # Conductance
                idx_a = node_idx.get(net_a)
                idx_b = node_idx.get(net_b)
                
                # Add to conductance matrix
                if idx_a is not None and idx_b is not None:
                    G[idx_a, idx_a] += g
                    G[idx_b, idx_b] += g
                    G[idx_a, idx_b] -= g
                    G[idx_b, idx_a] -= g
                elif idx_a is not None:
                    # net_b is ground
                    G[idx_a, idx_a] += g
                elif idx_b is not None:
                    # net_a is ground
                    G[idx_b, idx_b] += g
                    
        # Add current sources
        for comp in components:
            if comp.category.value in ["IC"]:  # Treat as current source for simplicity
                continue  # Skip for now
                
        # Solve G * V = I
        try:
            # Add regularization for numerical stability
            G_reg = G + 1e-12 * np.eye(n)
            voltages = np.linalg.solve(G_reg, I)
            return {nodes[i]: float(voltages[i]) for i in range(n)}
        except np.linalg.LinAlgError:
            return {}
            
    def _find_pin_net(self, comp_ref: str, pin_num: str, nets: List[Net]) -> Optional[str]:
        """Find the net connected to a specific component pin."""
        for net in nets:
            for ref, pin in net.connections:
                if ref == comp_ref and pin == pin_num:
                    return net.name
        return None
        
    def _get_component_value(self, comp: Component) -> Optional[float]:
        """Extract numeric value from component."""
        try:
            # Parse value like "10k", "4.7u", "100"
            val_str = comp.value.upper().strip()
            multipliers = {"P": 1e-12, "T": 1e12, "G": 1e9, "MEG": 1e6, "K": 1e3,
                          "M": 1e-3, "U": 1e-6, "N": 1e-9, "PF": 1e-12}
            for suffix, mult in multipliers.items():
                if val_str.endswith(suffix):
                    return float(val_str[:-len(suffix)]) * mult
            return float(val_str)
        except (ValueError, AttributeError):
            return None
            
    def voltage_divider(self, v_in: float, r1: float, r2: float) -> Dict[str, float]:
        """Calculate voltage divider output."""
        v_out = v_in * r2 / (r1 + r2)
        i_total = v_in / (r1 + r2)
        p_r1 = i_total ** 2 * r1
        p_r2 = i_total ** 2 * r2
        return {
            "v_out": v_out,
            "ratio": r2 / (r1 + r2),
            "i_total": i_total,
            "p_r1": p_r1,
            "p_r2": p_r2,
            "p_total": p_r1 + p_r2
        }
        
    def rc_filter_cutoff(self, r: float, c: float) -> Dict[str, float]:
        """Calculate RC filter characteristics."""
        f_c = 1.0 / (2 * np.pi * r * c)
        tau = r * c
        return {
            "cutoff_frequency_hz": f_c,
            "time_constant_s": tau,
            "omega_c_rad_s": 2 * np.pi * f_c
        }
        
    def transfer_function_rc_lowpass(self) -> Tuple[sp.Expr, sp.Symbol, sp.Symbol]:
        """Derive RC low-pass transfer function symbolically."""
        s, R, C = sp.symbols('s R C')
        # H(s) = 1 / (1 + sRC)
        H = 1 / (1 + s * R * C)
        return H, s, R
        
    def impedance_at_frequency(self, components: List[Dict], frequency_hz: float) -> complex:
        """
        Calculate total impedance of series/parallel components at a frequency.
        components: [{"type": "R"|"C"|"L", "value": float, "connection": "series"|"parallel"}]
        """
        omega = 2 * np.pi * frequency_hz
        total_z = complex(0, 0)
        parallel_admittance = complex(0, 0)
        current_connection = "series"
        
        for comp in components:
            ctype = comp["type"].upper()
            value = comp["value"]
            connection = comp.get("connection", "series")
            
            if connection != current_connection and current_connection == "parallel":
                # Flush parallel group
                if parallel_admittance != 0:
                    total_z += 1.0 / parallel_admittance
                parallel_admittance = complex(0, 0)
                
            current_connection = connection
            
            if ctype == "R":
                z = complex(value, 0)
            elif ctype == "C":
                z = complex(0, -1.0 / (omega * value)) if omega != 0 else complex(1e12, 0)
            elif ctype == "L":
                z = complex(0, omega * value)
            else:
                continue
                
            if connection == "series":
                total_z += z
            else:  # parallel
                parallel_admittance += 1.0 / z if z != 0 else complex(0, 0)
                
        # Flush remaining parallel
        if current_connection == "parallel" and parallel_admittance != 0:
            total_z += 1.0 / parallel_admittance
            
        return total_z
