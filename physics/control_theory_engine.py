"""
Control theory engine for Engineering OS.
"""
import numpy as np
from physics.mechanics_engine import MechanicsResult


class ControlTheoryEngine:
    """Control systems analysis and design calculations."""

    def transfer_function_gain(self, num_coeffs: list[float], den_coeffs: list[float]) -> MechanicsResult:
        """Compute DC gain of a transfer function."""
        K = num_coeffs[-1] / den_coeffs[-1] if den_coeffs[-1] != 0 else 0
        steps = [{"description": "DC gain", "formula": "K = N(0)/D(0)",
                  "result": f"K = {K:.4f}"}]
        return MechanicsResult(result={"dc_gain": float(K)}, steps=steps,
                               assumptions=["Linear time-invariant system"])

    def natural_frequency(self, omega_n: float = None, zeta: float = None,
                          damping_ratio: float = None) -> MechanicsResult:
        """Second-order system characteristics."""
        if omega_n and zeta:
            wd = omega_n * np.sqrt(1 - zeta**2) if zeta < 1 else 0
            steps = [
                {"description": "Damped natural frequency",
                 "formula": "ωd = ωn√(1-ζ²)",
                 "result": f"ωd = {wd:.4f} rad/s"},
                {"description": "Damping classification",
                 "result": "Underdamped" if zeta < 1 else "Critically damped" if zeta == 1 else "Overdamped"},
            ]
            return MechanicsResult(
                result={"damped_frequency": float(wd), "damping_ratio": zeta}, steps=steps,
                assumptions=["Second-order system", "LTI"])

    def pid_tuning_zigler(self, Ku: float, Tu: float) -> MechanicsResult:
        """Ziegler-Nichols PID tuning."""
        Kp = 0.6 * Ku
        Ki = 2 * Kp / Tu
        Kd = Kp * Tu / 8
        steps = [
            {"description": "Ziegler-Nichols PID tuning",
             "result": f"Kp = {Kp:.4f}, Ki = {Ki:.4f}, Kd = {Kd:.4f}"}]
        return MechanicsResult(
            result={"Kp": Kp, "Ki": Ki, "Kd": Kd}, steps=steps,
            assumptions=["Stable system", "Quarter decay ratio"])