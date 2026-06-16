"""
Troy — Drone Flight Dynamics Formulas
Core multirotor and fixed-wing drone calculations.

Formulas:
  1. Hover Thrust (per motor)
  2. Flight Time Estimation
  3. Power Required for Hover
  4. Max Speed Estimation
  5. Disc Loading
"""

from __future__ import annotations

import math
import sympy as sp

from app.calculations.registry import register_formula
from app.calculations.engine import make_symbolic_step, make_substitution_step, make_result_step


# ═══════════════════════════════════════════════════════════════════
# 1. HOVER THRUST (PER MOTOR)
# ═══════════════════════════════════════════════════════════════════
@register_formula(
    id="drones.flight_dynamics.hover_thrust",
    domain="drones",
    category="flight_dynamics",
    name="Hover Thrust Per Motor",
    description="Calculate the thrust each motor must produce for stable hover. "
                "Includes a safety factor for control authority margin.",
    formula_latex=r"T_{motor} = \frac{m \cdot g}{n} \cdot f_{safety}",
    parameters=[
        {"name": "m", "symbol": "m", "unit": "kg",
         "description": "All-up weight (AUW)", "min_value": 0.01, "max_value": 500.0},
        {"name": "g", "symbol": "g", "unit": "m/s²",
         "description": "Gravitational acceleration", "min_value": 9.0, "max_value": 10.0, "default": 9.80665},
        {"name": "n", "symbol": "n", "unit": "-",
         "description": "Number of motors", "min_value": 1, "max_value": 12, "default": 4},
        {"name": "f_safety", "symbol": "f_{safety}", "unit": "-",
         "description": "Safety factor (typically 1.5-2.0 for maneuverability)",
         "min_value": 1.0, "max_value": 3.0, "default": 1.5},
    ],
    outputs=[
        {"name": "T_motor", "symbol": "T_{motor}", "unit": "N",
         "description": "Required thrust per motor"},
        {"name": "T_motor_g", "symbol": "T_{motor,g}", "unit": "g",
         "description": "Required thrust per motor in grams"},
        {"name": "T_total", "symbol": "T_{total}", "unit": "N",
         "description": "Total system thrust required"},
    ],
    reference="Quan, Q., Introduction to Multicopter Design and Control, Springer, Ch. 2",
    tags=["hover", "thrust", "multirotor", "motor", "quadcopter"],
)
def hover_thrust(m: float, g: float = 9.80665, n: float = 4, f_safety: float = 1.5) -> dict:
    """Calculate hover thrust per motor."""
    n = int(n)
    W = m * g
    T_hover = W / n
    T_with_safety = T_hover * f_safety
    T_total = T_with_safety * n
    T_motor_grams = T_with_safety / g * 1000  # Convert to grams-force

    steps = [
        make_symbolic_step(
            "Weight of the drone",
            sp.Eq(sp.Symbol("W"), sp.Symbol("m") * sp.Symbol("g")),
        ),
        make_substitution_step(
            "Compute total weight",
            rf"W = {m} \times {g} = {W:.4f} \; \text{{N}}",
            {"m": f"{m} kg", "g": f"{g} m/s²"},
        ),
        make_substitution_step(
            "Thrust per motor at hover (no safety margin)",
            rf"T_{{hover}} = \frac{{W}}{{n}} = \frac{{{W:.4f}}}{{{n}}} = {T_hover:.4f} \; \text{{N}}",
            {"W": f"{W:.4f} N", "n": str(n)},
        ),
        make_substitution_step(
            f"Apply safety factor (×{f_safety}) for control authority",
            rf"T_{{motor}} = T_{{hover}} \times f_{{safety}} = {T_hover:.4f} \times {f_safety} = {T_with_safety:.4f} \; \text{{N}}",
            {"T_hover": f"{T_hover:.4f} N", "f_safety": str(f_safety)},
        ),
        make_result_step("Required thrust per motor", "T_{motor}", T_with_safety, "N"),
        make_result_step("Required thrust per motor", "T_{motor}", T_motor_grams, "gf"),
    ]

    return {
        "steps": steps,
        "results": {"T_motor": T_with_safety, "T_motor_g": T_motor_grams, "T_total": T_total},
        "latex_summary": rf"T_{{motor}} = \frac{{{m} \times {g}}}{{{n}}} \times {f_safety} = {T_with_safety:.4f} \; \text{{N}} \approx {T_motor_grams:.0f} \; \text{{gf}}",
    }


# ═══════════════════════════════════════════════════════════════════
# 2. FLIGHT TIME ESTIMATION
# ═══════════════════════════════════════════════════════════════════
@register_formula(
    id="drones.flight_dynamics.flight_time",
    domain="drones",
    category="flight_dynamics",
    name="Flight Time Estimation",
    description="Estimate multirotor flight time based on battery capacity and power draw. "
                "Accounts for battery discharge efficiency and minimum reserve.",
    formula_latex=r"t_{flight} = \frac{E_{batt} \times \eta_{discharge}}{P_{hover}} \times 60",
    parameters=[
        {"name": "capacity_mah", "symbol": "C", "unit": "mAh",
         "description": "Battery capacity", "min_value": 100, "max_value": 100000},
        {"name": "voltage", "symbol": "V", "unit": "V",
         "description": "Nominal battery voltage", "min_value": 3.0, "max_value": 60.0},
        {"name": "P_hover", "symbol": "P_{hover}", "unit": "W",
         "description": "Power draw at hover", "min_value": 1.0, "max_value": 50000.0},
        {"name": "eta", "symbol": r"\eta", "unit": "-",
         "description": "Discharge efficiency (typically 0.8 for LiPo)",
         "min_value": 0.5, "max_value": 1.0, "default": 0.8},
    ],
    outputs=[
        {"name": "t_flight_min", "symbol": "t_{flight}", "unit": "min",
         "description": "Estimated flight time"},
        {"name": "E_total", "symbol": "E_{total}", "unit": "Wh",
         "description": "Total battery energy"},
        {"name": "E_usable", "symbol": "E_{usable}", "unit": "Wh",
         "description": "Usable battery energy"},
    ],
    reference="Gundlach, J., Designing Unmanned Aircraft Systems, AIAA, Ch. 9",
    tags=["flight time", "endurance", "battery", "LiPo", "multirotor"],
)
def flight_time(capacity_mah: float, voltage: float, P_hover: float, eta: float = 0.8) -> dict:
    """Estimate multirotor flight time."""
    E_total_wh = (capacity_mah / 1000.0) * voltage  # mAh → Ah → Wh
    E_usable = E_total_wh * eta
    t_hours = E_usable / P_hover
    t_minutes = t_hours * 60

    steps = [
        make_substitution_step(
            "Convert battery capacity to energy",
            rf"E_{{total}} = \frac{{{capacity_mah}}}{{1000}} \times {voltage} = {E_total_wh:.4f} \; \text{{Wh}}",
            {"C": f"{capacity_mah} mAh", "V": f"{voltage} V"},
        ),
        make_substitution_step(
            f"Apply discharge efficiency (η = {eta})",
            rf"E_{{usable}} = {E_total_wh:.4f} \times {eta} = {E_usable:.4f} \; \text{{Wh}}",
            {"E_total": f"{E_total_wh:.4f} Wh", r"\eta": str(eta)},
        ),
        make_substitution_step(
            "Calculate flight time",
            rf"t_{{flight}} = \frac{{{E_usable:.4f}}}{{{P_hover}}} \times 60 = {t_minutes:.2f} \; \text{{min}}",
            {"E_usable": f"{E_usable:.4f} Wh", "P_hover": f"{P_hover} W"},
        ),
        make_result_step("Estimated hover flight time", "t_{flight}", t_minutes, "min"),
    ]

    return {
        "steps": steps,
        "results": {"t_flight_min": t_minutes, "E_total": E_total_wh, "E_usable": E_usable},
        "latex_summary": rf"t_{{flight}} = \frac{{{E_usable:.2f} \; \text{{Wh}}}}{{{P_hover} \; \text{{W}}}} = {t_minutes:.2f} \; \text{{min}}",
    }


# ═══════════════════════════════════════════════════════════════════
# 3. HOVER POWER (MOMENTUM THEORY)
# ═══════════════════════════════════════════════════════════════════
@register_formula(
    id="drones.flight_dynamics.hover_power",
    domain="drones",
    category="flight_dynamics",
    name="Hover Power (Momentum Theory)",
    description="Estimate power required for hover using actuator disc / momentum theory. "
                "P = T × v_i, where v_i is the induced velocity through the rotor disc.",
    formula_latex=r"P = T \sqrt{\frac{T}{2 \rho A}}",
    parameters=[
        {"name": "T", "symbol": "T", "unit": "N",
         "description": "Total thrust (= weight)", "min_value": 0.1, "max_value": 50000.0},
        {"name": "rho", "symbol": r"\rho", "unit": "kg/m³",
         "description": "Air density", "min_value": 0.5, "max_value": 1.5, "default": 1.225},
        {"name": "A", "symbol": "A", "unit": "m²",
         "description": "Total rotor disc area", "min_value": 0.001, "max_value": 100.0},
    ],
    outputs=[
        {"name": "P", "symbol": "P", "unit": "W", "description": "Power required for hover"},
        {"name": "v_i", "symbol": "v_i", "unit": "m/s", "description": "Induced velocity"},
        {"name": "disc_loading", "symbol": "DL", "unit": "N/m²", "description": "Disc loading"},
    ],
    reference="Leishman, J.G., Principles of Helicopter Aerodynamics, 2nd Ed., Ch. 2",
    tags=["hover", "power", "momentum theory", "induced velocity", "rotor"],
)
def hover_power(T: float, rho: float = 1.225, A: float = 0.1) -> dict:
    """Compute hover power via momentum theory."""
    disc_loading = T / A
    v_i = math.sqrt(T / (2 * rho * A))
    P = T * v_i

    steps = [
        make_substitution_step(
            "Compute disc loading",
            rf"DL = \frac{{T}}{{A}} = \frac{{{T}}}{{{A}}} = {disc_loading:.4f} \; \text{{N/m²}}",
            {"T": f"{T} N", "A": f"{A} m²"},
        ),
        make_substitution_step(
            "Compute induced velocity (momentum theory)",
            rf"v_i = \sqrt{{\frac{{T}}{{2 \rho A}}}} = \sqrt{{\frac{{{T}}}{{2 \times {rho} \times {A}}}}} = {v_i:.4f} \; \text{{m/s}}",
            {"T": f"{T} N", r"\rho": f"{rho} kg/m³", "A": f"{A} m²"},
        ),
        make_substitution_step(
            "Compute ideal hover power",
            rf"P = T \times v_i = {T} \times {v_i:.4f} = {P:.4f} \; \text{{W}}",
            {"T": f"{T} N", "v_i": f"{v_i:.4f} m/s"},
        ),
        make_result_step("Power required for hover", "P", P, "W"),
    ]

    return {
        "steps": steps,
        "results": {"P": P, "v_i": v_i, "disc_loading": disc_loading},
        "latex_summary": rf"P = {T} \times \sqrt{{\frac{{{T}}}{{2 \times {rho} \times {A}}}}} = {P:.4f} \; \text{{W}}",
    }
