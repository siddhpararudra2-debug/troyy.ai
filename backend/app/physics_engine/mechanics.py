"""
Mechanics — Statics, Dynamics, Beam Bending, Torsion, Stress
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class BeamResult:
    sigma: float
    tau: float
    safety_factor: float
    units: str


class MechanicsEngine:
    """Core mechanics engine"""

    def force(self, mass: float, acceleration: float) -> Dict[str, Any]:
        """F = m*a"""
        return {
            "force": mass * acceleration,
            "units": "N",
            "formula": "F = m·a",
        }

    def torque(self, r: float, f: float, theta: float = 90.0) -> Dict[str, Any]:
        """τ = r·F·sin(θ)"""
        import math
        theta_rad = math.radians(theta)
        return {
            "torque": r * f * math.sin(theta_rad),
            "units": "N·m",
            "formula": "τ = r·F·sin(θ)",
        }

    def bending_stress(
        self,
        m: float,
        c: float,
        i: float,
    ) -> Dict[str, Any]:
        """σ = (M·c)/I"""
        sigma = (m * c) / i
        return {
            "stress": sigma,
            "units": "Pa",
            "formula": "σ = (M·c)/I",
        }

    def shear_stress(
        self,
        v: float,
        q: float,
        i: float,
        b: float,
    ) -> Dict[str, Any]:
        """τ = (V·Q)/(I·b)"""
        tau = (v * q) / (i * b)
        return {
            "shear_stress": tau,
            "units": "Pa",
            "formula": "τ = (V·Q)/(I·b)",
        }

    def torsion_stress(
        self,
        t: float,
        r: float,
        j: float,
    ) -> Dict[str, Any]:
        """τ = (T·r)/J"""
        tau = (t * r) / j
        return {
            "torsion_stress": tau,
            "units": "Pa",
            "formula": "τ = (T·r)/J",
        }

    def critical_buckling_load(
        self,
        e: float,
        i: float,
        k: float,
        l: float,
    ) -> Dict[str, Any]:
        """P_cr = (π²·E·I)/(K·L)²"""
        import math
        p_cr = (math.pi**2 * e * i) / (k * l)**2
        return {
            "critical_load": p_cr,
            "units": "N",
            "formula": "P_cr = (π²·E·I)/(K·L)²",
        }

    def von_mises_stress(
        self,
        sigma1: float,
        sigma2: float,
        sigma3: float,
    ) -> Dict[str, Any]:
        """Von Mises equivalent stress for triaxial state"""
        import math
        sigma_von = (
            0.5 * (
                (sigma1 - sigma2)**2 +
                (sigma2 - sigma3)**2 +
                (sigma3 - sigma1)**2
            )
        )**0.5
        return {
            "von_mises": sigma_von,
            "units": "Pa",
        }
