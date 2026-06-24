"""
Fluid mechanics and aerodynamics engine for Engineering OS.
"""
import logging
import numpy as np
from typing import Optional
from dataclasses import dataclass

from physics.mechanics_engine import MechanicsResult

logger = logging.getLogger(__name__)


class FluidEngine:
    """Fluid mechanics and aerodynamics calculations."""

    def reynolds_number(self, rho: float, v: float, L: float, mu: float) -> MechanicsResult:
        """Calculate Reynolds number: Re = ρvL/μ."""
        Re = rho * v * L / mu
        
        flow_type = "Laminar" if Re < 2300 else "Turbulent" if Re > 4000 else "Transitional"
        
        steps = [
            {"description": "Calculate Reynolds number", "formula": "Re = ρvL/μ",
             "values": f"Re = {rho} × {v} × {L} / {mu}",
             "result": f"Re = {Re:.4e}"},
            {"description": "Flow regime classification", "result": flow_type},
        ]
        
        return MechanicsResult(
            result={"reynolds_number": float(Re), "flow_type": flow_type},
            steps=steps,
            assumptions=["Newtonian fluid", "Steady flow"],
        )

    def lift_force(self, Cl: float, rho: float, v: float, S: float) -> MechanicsResult:
        """Calculate lift force: L = 0.5 * Cl * ρ * v² * S."""
        L = 0.5 * Cl * rho * v**2 * S
        
        steps = [
            {"description": "Apply lift equation", "formula": "L = ½ × Cl × ρ × v² × S",
             "values": f"L = 0.5 × {Cl} × {rho} × {v}² × {S}",
             "result": f"L = {L:.4f} N"},
        ]
        
        return MechanicsResult(
            result={"lift": float(L), "unit": "N"},
            steps=steps,
            assumptions=["Steady flow", "Incompressible fluid", "Small angle of attack"],
        )

    def drag_force(self, Cd: float, rho: float, v: float, S: float) -> MechanicsResult:
        """Calculate drag force: D = 0.5 * Cd * ρ * v² * S."""
        D = 0.5 * Cd * rho * v**2 * S
        
        steps = [
            {"description": "Apply drag equation", "formula": "D = ½ × Cd × ρ × v² × S",
             "values": f"D = 0.5 × {Cd} × {rho} × {v}² × {S}",
             "result": f"D = {D:.4f} N"},
        ]
        
        return MechanicsResult(
            result={"drag": float(D), "unit": "N"},
            steps=steps,
            assumptions=["Steady flow", "Incompressible fluid"],
        )

    def bernoulli(self, p1: float, v1: float, z1: float,
                  p2: float, v2: float, z2: float, rho: float = 1000.0) -> MechanicsResult:
        """Apply Bernoulli's equation: p + ½ρv² + ρgz = constant."""
        head1 = p1 + 0.5 * rho * v1**2 + rho * 9.81 * z1
        head2 = p2 + 0.5 * rho * v2**2 + rho * 9.81 * z2
        diff = head1 - head2
        
        steps = [
            {"description": "Total head at point 1", "formula": "H₁ = p₁ + ½ρv₁² + ρgz₁",
             "result": f"H₁ = {head1:.4f} Pa"},
            {"description": "Total head at point 2", "formula": "H₂ = p₂ + ½ρv₂² + ρgz₂",
             "result": f"H₂ = {head2:.4f} Pa"},
            {"description": "Head loss/gain", "result": f"ΔH = {diff:.4f} Pa"},
        ]
        
        return MechanicsResult(
            result={"head1": float(head1), "head2": float(head2), "delta": float(diff)},
            steps=steps,
            assumptions=["Steady flow", "Inviscid", "Incompressible", "Along streamline"],
        )

    def pipe_flow_darcy(self, f: float, L: float, D: float, v: float, rho: float) -> MechanicsResult:
        """Darcy-Weisbach friction loss in pipes."""
        h_f = f * (L / D) * (v**2 / (2 * 9.81))
        delta_p = rho * 9.81 * h_f
        
        steps = [
            {"description": "Darcy-Weisbach head loss", "formula": "hf = f × (L/D) × v²/(2g)",
             "values": f"hf = {f} × ({L}/{D}) × {v}²/(2×9.81)",
             "result": f"hf = {h_f:.4f} m"},
            {"description": "Pressure drop", "result": f"Δp = {delta_p:.4f} Pa"},
        ]
        
        return MechanicsResult(
            result={"head_loss": float(h_f), "pressure_drop": float(delta_p)},
            steps=steps,
            assumptions=["Fully developed flow", "Circular pipe", "Incompressible"],
        )

    def mach_number(self, v: float, T: float, gamma: float = 1.4, R: float = 287.0) -> MechanicsResult:
        """Calculate Mach number: M = v / √(γRT)."""
        a = np.sqrt(gamma * R * T)  # Speed of sound
        M = v / a
        
        regime = "Subsonic" if M < 0.8 else "Transonic" if M < 1.2 else "Supersonic" if M < 5.0 else "Hypersonic"
        
        steps = [
            {"description": "Speed of sound", "formula": "a = √(γRT)",
             "result": f"a = {a:.2f} m/s"},
            {"description": "Mach number", "formula": "M = v/a",
             "result": f"M = {M:.4f} ({regime})"},
        ]
        
        return MechanicsResult(
            result={"mach": float(M), "speed_of_sound": float(a), "regime": regime},
            steps=steps,
            assumptions=["Ideal gas", "Calorically perfect gas"],
        )