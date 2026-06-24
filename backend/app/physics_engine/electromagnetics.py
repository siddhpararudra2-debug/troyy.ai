"""
Electromagnetics — Ohm's Law, Power, RC, LC
"""
from typing import Dict, Any
import math


class ElectromagneticsEngine:
    """Electromagnetics engine"""

    def ohms_law(
        self,
        v: float = None,
        i: float = None,
        r: float = None,
    ) -> Dict[str, Any]:
        """V = I·R"""
        if sum(x is None for x in [v, i, r]) != 1:
            raise ValueError("Exactly one parameter must be None")

        if v is None:
            return {"voltage": i * r, "units": "V"}
        if i is None:
            return {"current": v / r, "units": "A"}
        if r is None:
            return {"resistance": v / i, "units": "Ω"}

    def power(
        self,
        v: float = None,
        i: float = None,
        r: float = None,
    ) -> Dict[str, Any]:
        """P = V·I = I²·R = V²/R"""
        if v is not None and i is not None:
            return {"power": v * i, "units": "W"}
        if i is not None and r is not None:
            return {"power": i**2 * r, "units": "W"}
        if v is not None and r is not None:
            return {"power": v**2 / r, "units": "W"}
        raise ValueError("Need two of v/i/r")

    def rc_time_constant(
        self,
        r: float,
        c: float,
    ) -> Dict[str, Any]:
        """τ = R·C"""
        tau = r * c
        return {"time_constant": tau, "units": "s"}

    def lc_resonance(
        self,
        l: float,
        c: float,
    ) -> Dict[str, Any]:
        """f₀ = 1/(2π√(L·C))"""
        f0 = 1 / (2 * math.pi * math.sqrt(l * c))
        return {"resonance_frequency": f0, "units": "Hz"}
