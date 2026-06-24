"""
Electromagnetics engine for Engineering OS.
"""
import numpy as np
from physics.mechanics_engine import MechanicsResult


class ElectromagneticsEngine:
    """Electromagnetics calculations for circuits, fields, and systems."""

    def ohms_law(self, V: float = None, I: float = None, R: float = None) -> MechanicsResult:
        """Ohm's law: V = IR."""
        if V is None:
            V = I * R
            desc = f"V = {I} × {R}"
        elif I is None:
            I = V / R
            desc = f"I = {V} / {R}"
        else:
            R = V / I
            desc = f"R = {V} / {I}"
        
        steps = [{"description": "Ohm's law", "formula": "V = IR",
                  "values": desc, "result": f"Result: {V or I or R:.4f}"}]
        return MechanicsResult(
            result={"voltage": V, "current": I, "resistance": R}, steps=steps,
            assumptions=["Ohmic conductor", "DC steady state"])

    def power_electrical(self, V: float = None, I: float = None, R: float = None) -> MechanicsResult:
        """Electrical power: P = VI = I²R = V²/R."""
        if V is not None and I is not None:
            P = V * I
            formula = "P = VI"
        elif I is not None and R is not None:
            P = I**2 * R
            formula = "P = I²R"
        else:
            P = V**2 / R
            formula = "P = V²/R"
        
        steps = [{"description": "Electrical power", "formula": formula,
                  "result": f"P = {P:.4f} W"}]
        return MechanicsResult(result={"power": float(P), "unit": "W"}, steps=steps,
                               assumptions=["DC circuit", "Steady state"])

    def rc_time_constant(self, R: float, C: float) -> MechanicsResult:
        """RC time constant: τ = RC."""
        tau = R * C
        steps = [{"description": "RC time constant", "formula": "τ = RC",
                  "result": f"τ = {tau:.4e} s"}]
        return MechanicsResult(result={"time_constant": float(tau), "unit": "s"}, steps=steps,
                               assumptions=["Ideal capacitor", "Linear circuit"])

    def resonant_frequency(self, L: float, C: float) -> MechanicsResult:
        """LC resonant frequency: f₀ = 1/(2π√(LC))."""
        f0 = 1 / (2 * np.pi * np.sqrt(L * C))
        steps = [{"description": "Resonant frequency", "formula": "f₀ = 1/(2π√(LC))",
                  "result": f"f₀ = {f0:.4f} Hz"}]
        return MechanicsResult(result={"frequency": float(f0), "unit": "Hz"}, steps=steps,
                               assumptions=["Ideal LC circuit", "No losses"])

    def coulomb_force(self, q1: float, q2: float, r: float) -> MechanicsResult:
        """Coulomb's law: F = k|q₁q₂|/r²."""
        k = 8.9875517923e9
        F = k * abs(q1 * q2) / r**2
        steps = [{"description": "Coulomb's law", "formula": "F = k|q₁q₂|/r²",
                  "values": f"F = 8.99e9 × |{q1} × {q2}| / {r}²",
                  "result": f"F = {F:.4f} N"}]
        return MechanicsResult(result={"force": float(F), "unit": "N"}, steps=steps,
                               assumptions=["Point charges", "Vacuum"])

    def filter_cutoff(self, R: float, C: float, filter_type: str = "low_pass") -> MechanicsResult:
        """RC filter cutoff frequency: fc = 1/(2πRC)."""
        fc = 1 / (2 * np.pi * R * C)
        steps = [{"description": f"{filter_type.replace('_', ' ').title()} filter cutoff",
                  "formula": "fc = 1/(2πRC)",
                  "result": f"fc = {fc:.4f} Hz"}]
        return MechanicsResult(result={"cutoff_frequency": float(fc), "unit": "Hz"}, steps=steps,
                               assumptions=["First order RC", "Ideal components"])

    def transformer_ratio(self, Vp: float = None, Vs: float = None,
                          Np: float = None, Ns: float = None) -> MechanicsResult:
        """Ideal transformer: Vp/Vs = Np/Ns."""
        if Vp is not None and Vs is not None:
            ratio = Vp / Vs
            desc = f"Ratio = {Vp}/{Vs}"
        elif Np is not None and Ns is not None:
            ratio = Np / Ns
            desc = f"Ratio = {Np}/{Ns}"
        
        steps = [{"description": "Transformer ratio", "formula": "Vp/Vs = Np/Ns",
                  "result": f"Ratio = {ratio:.4f}"}]
        return MechanicsResult(result={"turns_ratio": float(ratio)}, steps=steps,
                               assumptions=["Ideal transformer", "No losses"])