"""
Troy — Robotics Kinematics & Dynamics Formulas
Core robotics calculations.

Formulas:
  1. Joint Torque Calculation
  2. Angular Velocity to Linear Velocity
  3. Gear Ratio Selection
"""

from __future__ import annotations

import math
import sympy as sp

from app.calculations.registry import register_formula
from app.calculations.engine import make_symbolic_step, make_substitution_step, make_result_step


# ═══════════════════════════════════════════════════════════════════
# 1. JOINT TORQUE CALCULATION
# ═══════════════════════════════════════════════════════════════════
@register_formula(
    id="robotics.dynamics.joint_torque",
    domain="robotics",
    category="dynamics",
    name="Joint Torque Requirement",
    description="Calculate the torque required at a robot joint to hold or move a payload. "
                "Considers gravity loading and desired angular acceleration.",
    formula_latex=r"\tau = m \cdot g \cdot L \cdot \cos(\theta) + I \cdot \ddot{\theta}",
    parameters=[
        {"name": "m", "symbol": "m", "unit": "kg",
         "description": "Mass of link + payload", "min_value": 0.01, "max_value": 1000.0},
        {"name": "g", "symbol": "g", "unit": "m/s²",
         "description": "Gravitational acceleration", "min_value": 9.0, "max_value": 10.0, "default": 9.80665},
        {"name": "L", "symbol": "L", "unit": "m",
         "description": "Distance from joint to center of mass", "min_value": 0.001, "max_value": 10.0},
        {"name": "theta_deg", "symbol": r"\theta", "unit": "°",
         "description": "Joint angle from vertical", "min_value": 0.0, "max_value": 360.0, "default": 0.0},
        {"name": "I", "symbol": "I", "unit": "kg·m²",
         "description": "Moment of inertia about joint", "min_value": 0.0, "max_value": 1000.0, "default": 0.0},
        {"name": "alpha", "symbol": r"\ddot{\theta}", "unit": "rad/s²",
         "description": "Desired angular acceleration", "min_value": 0.0, "max_value": 100.0, "default": 0.0},
    ],
    outputs=[
        {"name": "tau_gravity", "symbol": r"\tau_g", "unit": "N·m",
         "description": "Gravity torque component"},
        {"name": "tau_accel", "symbol": r"\tau_a", "unit": "N·m",
         "description": "Acceleration torque component"},
        {"name": "tau_total", "symbol": r"\tau", "unit": "N·m",
         "description": "Total required torque"},
    ],
    reference="Craig, J.J., Introduction to Robotics: Mechanics and Control, 4th Ed., Ch. 6",
    tags=["torque", "joint", "servo", "motor sizing", "dynamics"],
)
def joint_torque(
    m: float, g: float = 9.80665, L: float = 0.1,
    theta_deg: float = 0.0, I: float = 0.0, alpha: float = 0.0
) -> dict:
    """Calculate joint torque requirement."""
    theta_rad = math.radians(theta_deg)
    tau_gravity = m * g * L * math.cos(theta_rad)
    tau_accel = I * alpha
    tau_total = tau_gravity + tau_accel

    m_s, g_s, L_s, theta_s, I_s, alpha_s = sp.symbols(
        r"m g L \theta I \ddot{\theta}", positive=True
    )
    tau_s = m_s * g_s * L_s * sp.cos(theta_s) + I_s * alpha_s

    steps = [
        make_symbolic_step(
            "Joint torque equation (gravity + inertial)",
            sp.Eq(sp.Symbol(r"\tau"), tau_s),
        ),
        make_substitution_step(
            "Compute gravity torque component",
            rf"\tau_g = {m} \times {g} \times {L} \times \cos({theta_deg}°) = {tau_gravity:.6f} \; \text{{N·m}}",
            {"m": f"{m} kg", "g": f"{g} m/s²", "L": f"{L} m", r"\theta": f"{theta_deg}°"},
        ),
        make_substitution_step(
            "Compute acceleration torque component",
            rf"\tau_a = {I} \times {alpha} = {tau_accel:.6f} \; \text{{N·m}}",
            {"I": f"{I} kg·m²", r"\ddot{{\theta}}": f"{alpha} rad/s²"},
        ),
        make_substitution_step(
            "Sum torque components",
            rf"\tau = {tau_gravity:.6f} + {tau_accel:.6f} = {tau_total:.6f} \; \text{{N·m}}",
            {r"\tau_g": f"{tau_gravity:.6f} N·m", r"\tau_a": f"{tau_accel:.6f} N·m"},
        ),
        make_result_step("Total required torque", r"\tau", tau_total, "N·m"),
    ]

    return {
        "steps": steps,
        "results": {"tau_gravity": tau_gravity, "tau_accel": tau_accel, "tau_total": tau_total},
        "latex_summary": rf"\tau = {tau_total:.6f} \; \text{{N·m}} \quad (\tau_g = {tau_gravity:.4f}, \tau_a = {tau_accel:.4f})",
    }


# ═══════════════════════════════════════════════════════════════════
# 2. GEAR RATIO SELECTION
# ═══════════════════════════════════════════════════════════════════
@register_formula(
    id="robotics.dynamics.gear_ratio",
    domain="robotics",
    category="dynamics",
    name="Gear Ratio Selection",
    description="Calculate output torque and speed after gear reduction. "
                "Higher gear ratio = more torque, less speed.",
    formula_latex=r"\tau_{out} = \tau_{motor} \times N \times \eta, \quad \omega_{out} = \frac{\omega_{motor}}{N}",
    parameters=[
        {"name": "tau_motor", "symbol": r"\tau_{motor}", "unit": "N·m",
         "description": "Motor output torque", "min_value": 0.001, "max_value": 1000.0},
        {"name": "omega_motor_rpm", "symbol": r"\omega_{motor}", "unit": "RPM",
         "description": "Motor speed", "min_value": 1, "max_value": 100000},
        {"name": "N", "symbol": "N", "unit": "-",
         "description": "Gear ratio", "min_value": 1.0, "max_value": 1000.0},
        {"name": "eta", "symbol": r"\eta", "unit": "-",
         "description": "Gear efficiency", "min_value": 0.5, "max_value": 1.0, "default": 0.9},
    ],
    outputs=[
        {"name": "tau_out", "symbol": r"\tau_{out}", "unit": "N·m",
         "description": "Output torque"},
        {"name": "omega_out_rpm", "symbol": r"\omega_{out}", "unit": "RPM",
         "description": "Output speed"},
        {"name": "P_out", "symbol": "P_{out}", "unit": "W",
         "description": "Output power"},
    ],
    reference="Norton, R.L., Machine Design, 5th Ed., Ch. 9",
    tags=["gear", "reduction", "torque", "speed", "motor"],
)
def gear_ratio(tau_motor: float, omega_motor_rpm: float, N: float, eta: float = 0.9) -> dict:
    """Calculate gear output torque and speed."""
    tau_out = tau_motor * N * eta
    omega_out_rpm = omega_motor_rpm / N
    omega_out_rad = omega_out_rpm * 2 * math.pi / 60
    P_out = tau_out * omega_out_rad

    steps = [
        make_substitution_step(
            "Compute output torque (with efficiency loss)",
            rf"\tau_{{out}} = {tau_motor} \times {N} \times {eta} = {tau_out:.6f} \; \text{{N·m}}",
            {r"\tau_{motor}": f"{tau_motor} N·m", "N": str(N), r"\eta": str(eta)},
        ),
        make_substitution_step(
            "Compute output speed",
            rf"\omega_{{out}} = \frac{{{omega_motor_rpm}}}{{{N}}} = {omega_out_rpm:.2f} \; \text{{RPM}}",
            {r"\omega_{motor}": f"{omega_motor_rpm} RPM", "N": str(N)},
        ),
        make_substitution_step(
            "Compute output mechanical power",
            rf"P_{{out}} = \tau_{{out}} \times \omega_{{out}} = {tau_out:.6f} \times {omega_out_rad:.4f} = {P_out:.4f} \; \text{{W}}",
            {r"\tau_{out}": f"{tau_out:.6f} N·m", r"\omega_{out}": f"{omega_out_rad:.4f} rad/s"},
        ),
        make_result_step("Output torque", r"\tau_{out}", tau_out, "N·m"),
        make_result_step("Output speed", r"\omega_{out}", omega_out_rpm, "RPM"),
    ]

    return {
        "steps": steps,
        "results": {"tau_out": tau_out, "omega_out_rpm": omega_out_rpm, "P_out": P_out},
        "latex_summary": rf"\tau_{{out}} = {tau_out:.4f} \; \text{{N·m}}, \quad \omega_{{out}} = {omega_out_rpm:.2f} \; \text{{RPM}}",
    }
