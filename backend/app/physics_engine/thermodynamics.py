"""
Thermodynamics — Ideal Gas, Fourier, Newton Cooling
"""
from typing import Dict, Any


class ThermodynamicsEngine:
    """Thermodynamics engine"""

    def ideal_gas_law(
        self,
        p: float = None,
        v: float = None,
        n: float = None,
        r: float = 8.314,
        t: float = None,
    ) -> Dict[str, Any]:
        """P·V = n·R·T"""
        if sum(x is None for x in [p, v, n, t]) != 1:
            raise ValueError("Exactly one parameter must be None to solve for")

        if p is None:
            p = (n * r * t) / v
            return {"pressure": p, "units": "Pa"}
        if v is None:
            v = (n * r * t) / p
            return {"volume": v, "units": "m³"}
        if n is None:
            n = (p * v) / (r * t)
            return {"moles": n, "units": "mol"}
        if t is None:
            t = (p * v) / (n * r)
            return {"temperature": t, "units": "K"}

    def fourier_conduction(
        self,
        k: float,
        a: float,
        delta_t: float,
        delta_x: float,
    ) -> Dict[str, Any]:
        """q = -k·A·(ΔT/Δx)"""
        q = k * a * (delta_t / delta_x)
        return {
            "heat_transfer_rate": q,
            "units": "W",
            "formula": "q = -k·A·(ΔT/Δx)",
        }

    def newton_cooling(
        self,
        h: float,
        a: float,
        t_s: float,
        t_inf: float,
    ) -> Dict[str, Any]:
        """q = h·A·(T_s - T_inf)"""
        q = h * a * (t_s - t_inf)
        return {
            "heat_transfer_rate": q,
            "units": "W",
            "formula": "q = h·A·(T_s - T_inf)",
        }
