"""
Thermodynamics engine for Engineering OS.
"""
import logging
import numpy as np
from physics.mechanics_engine import MechanicsResult

logger = logging.getLogger(__name__)


class ThermodynamicsEngine:
    """Thermodynamics and heat transfer calculations."""

    def ideal_gas_law(self, P: float, V: float, n: float, R: float = 8.314, T: float = None) -> MechanicsResult:
        """Ideal gas law: PV = nRT."""
        if T is None:
            T = P * V / (n * R)
            desc = f"T = {P} × {V} / ({n} × {R})"
            result_key = "temperature"
        else:
            result = P * V / (n * R)
            desc = f" {P} × {V} / ({n} × {R})"
            result_key = "temperature"
        
        T_val = P * V / (n * R)
        steps = [{"description": "Ideal gas law", "formula": "PV = nRT",
                  "values": desc, "result": f"T = {T_val:.4f} K"}]
        
        return MechanicsResult(
            result={"temperature": float(T_val), "unit": "K"},
            steps=steps, assumptions=["Ideal gas behavior", "Thermal equilibrium"])

    def heat_conduction(self, k: float, A: float, dT: float, L: float) -> MechanicsResult:
        """Fourier's law: Q = kA(dT)/L."""
        Q = k * A * dT / L
        steps = [{"description": "Fourier's law of conduction", "formula": "Q = kA(dT)/L",
                  "values": f"Q = {k} × {A} × {dT} / {L}",
                  "result": f"Q = {Q:.4f} W"}]
        return MechanicsResult(
            result={"heat_flow": float(Q), "unit": "W"},
            steps=steps, assumptions=["Steady state", "1D conduction", "Constant k"])

    def heat_convection(self, h: float, A: float, dT: float) -> MechanicsResult:
        """Newton's law of cooling: Q = hA(dT)."""
        Q = h * A * dT
        steps = [{"description": "Newton's law of cooling", "formula": "Q = hA(dT)",
                  "result": f"Q = {Q:.4f} W"}]
        return MechanicsResult(
            result={"heat_flow": float(Q), "unit": "W"},
            steps=steps, assumptions=["Steady state", "Constant h"])

    def thermal_expansion(self, alpha: float, L0: float, dT: float) -> MechanicsResult:
        """Linear thermal expansion: ΔL = αL₀ΔT."""
        dL = alpha * L0 * dT
        steps = [{"description": "Linear thermal expansion", "formula": "ΔL = αL₀ΔT",
                  "result": f"ΔL = {dL:.4e} m"}]
        return MechanicsResult(
            result={"expansion": float(dL), "unit": "m"},
            steps=steps, assumptions=["Isotropic material", "Constant α"])

    def heat_exchanger_lmtd(self, Th_in: float, Th_out: float, Tc_in: float, Tc_out: float,
                            U: float, A: float = None) -> MechanicsResult:
        """Log mean temperature difference for heat exchangers."""
        dT1 = Th_in - Tc_out
        dT2 = Th_out - Tc_in
        LMTD = (dT1 - dT2) / np.log(dT1 / dT2) if dT1 != dT2 else dT1
        
        steps = [
            {"description": "Temperature difference at ends",
             "result": f"ΔT₁ = {dT1:.2f}°C, ΔT₂ = {dT2:.2f}°C"},
            {"description": "Log mean temperature difference",
             "formula": "LMTD = (ΔT₁ - ΔT₂)/ln(ΔT₁/ΔT₂)",
             "result": f"LMTD = {LMTD:.4f}°C"},
        ]
        
        result = {"lmtd": float(LMTD), "unit": "°C"}
        if A is not None:
            Q = U * A * LMTD
            result["heat_transfer"] = float(Q)
            steps.append({"description": "Heat transfer rate", "result": f"Q = {Q:.4f} W"})
        
        return MechanicsResult(
            result=result, steps=steps,
            assumptions=["Steady state", "Constant U", "Counter-flow"])