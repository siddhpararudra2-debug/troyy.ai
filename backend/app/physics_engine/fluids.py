"""
Fluid Dynamics — Lift, Drag, Bernoulli, Reynolds
"""
from typing import Dict, Any


class FluidEngine:
    """Fluid dynamics engine"""

    def reynolds_number(
        self,
        rho: float,
        v: float,
        l: float,
        mu: float,
    ) -> Dict[str, Any]:
        """Re = (ρ·v·L)/μ"""
        re = (rho * v * l) / mu
        return {
            "reynolds": re,
            "flow_regime": "laminar" if re < 2300 else "turbulent" if re > 4000 else "transition",
            "formula": "Re = (ρ·v·L)/μ",
        }

    def lift_force(
        self,
        rho: float,
        v: float,
        s: float,
        cl: float,
    ) -> Dict[str, Any]:
        """L = ½·ρ·v²·S·C_L"""
        lift = 0.5 * rho * v**2 * s * cl
        return {
            "lift": lift,
            "units": "N",
            "formula": "L = ½·ρ·v²·S·C_L",
        }

    def drag_force(
        self,
        rho: float,
        v: float,
        s: float,
        cd: float,
    ) -> Dict[str, Any]:
        """D = ½·ρ·v²·S·C_D"""
        drag = 0.5 * rho * v**2 * s * cd
        return {
            "drag": drag,
            "units": "N",
            "formula": "D = ½·ρ·v²·S·C_D",
        }

    def bernoulli(
        self,
        p1: float,
        rho: float,
        v1: float,
        h1: float,
        p2: float,
        v2: float,
        h2: float,
        g: float = 9.81,
    ) -> Dict[str, Any]:
        """Bernoulli equation: P + ½ρv² + ρgh = constant"""
        left = p1 + 0.5 * rho * v1**2 + rho * g * h1
        right = p2 + 0.5 * rho * v2**2 + rho * g * h2
        return {
            "left_side": left,
            "right_side": right,
            "balanced": abs(left - right) < 1e-6,
            "formula": "P + ½ρv² + ρgh = constant",
        }

    def mach_number(
        self,
        v: float,
        c: float,
    ) -> Dict[str, Any]:
        """M = v/c"""
        mach = v / c
        regime = "subsonic" if mach < 0.8 else "transonic" if mach < 1.2 else "supersonic"
        return {
            "mach": mach,
            "regime": regime,
            "formula": "M = v/c",
        }
