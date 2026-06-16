"""
Troy — Aerospace Propulsion Formulas
Implements propulsion and rocket science calculations.

Formulas:
  1. Tsiolkovsky Rocket Equation (Δv = Isp·g₀·ln(m₀/m_f))
  2. Thrust Equation (F = ṁ·vₑ + (Pₑ - P₀)·Aₑ)
  3. Specific Impulse
  4. Thrust-to-Weight Ratio
"""

from __future__ import annotations

import math
import sympy as sp

from app.calculations.registry import register_formula
from app.calculations.engine import make_symbolic_step, make_substitution_step, make_result_step


# ═══════════════════════════════════════════════════════════════════
# 1. TSIOLKOVSKY ROCKET EQUATION
# ═══════════════════════════════════════════════════════════════════
@register_formula(
    id="aerospace.propulsion.tsiolkovsky",
    domain="aerospace",
    category="propulsion",
    name="Tsiolkovsky Rocket Equation",
    description="Calculate the theoretical maximum delta-v of a rocket based on exhaust velocity "
                "and mass ratio. The fundamental equation of spaceflight.",
    formula_latex=r"\Delta v = I_{sp} \cdot g_0 \cdot \ln\left(\frac{m_0}{m_f}\right)",
    parameters=[
        {"name": "Isp", "symbol": "I_{sp}", "unit": "s",
         "description": "Specific impulse", "min_value": 50.0, "max_value": 5000.0},
        {"name": "m0", "symbol": "m_0", "unit": "kg",
         "description": "Initial mass (wet)", "min_value": 0.1, "max_value": 1e8},
        {"name": "mf", "symbol": "m_f", "unit": "kg",
         "description": "Final mass (dry)", "min_value": 0.01, "max_value": 1e8},
        {"name": "g0", "symbol": "g_0", "unit": "m/s²",
         "description": "Standard gravity", "min_value": 9.0, "max_value": 10.0, "default": 9.80665},
    ],
    outputs=[
        {"name": "delta_v", "symbol": r"\Delta v", "unit": "m/s",
         "description": "Delta-v (velocity change budget)"},
        {"name": "mass_ratio", "symbol": "R", "unit": "-",
         "description": "Mass ratio (m₀/m_f)"},
        {"name": "ve", "symbol": "v_e", "unit": "m/s",
         "description": "Effective exhaust velocity"},
    ],
    reference="Sutton, G.P., Rocket Propulsion Elements, 9th Ed., Ch. 2",
    tags=["rocket", "delta-v", "mass ratio", "exhaust velocity", "orbital mechanics"],
)
def tsiolkovsky(Isp: float, m0: float, mf: float, g0: float = 9.80665) -> dict:
    """Compute delta-v from the Tsiolkovsky rocket equation."""
    if mf >= m0:
        raise ValueError("Final mass must be less than initial mass (m_f < m_0)")
    if mf <= 0:
        raise ValueError("Final mass must be positive")

    ve = Isp * g0
    mass_ratio = m0 / mf
    delta_v = ve * math.log(mass_ratio)

    Isp_s, m0_s, mf_s, g0_s = sp.symbols("I_{sp} m_0 m_f g_0", positive=True)
    ve_s = Isp_s * g0_s
    dv_s = ve_s * sp.ln(m0_s / mf_s)

    steps = [
        make_symbolic_step(
            "Tsiolkovsky rocket equation",
            sp.Eq(sp.Symbol(r"\Delta v"), dv_s),
        ),
        make_substitution_step(
            "Compute effective exhaust velocity",
            rf"v_e = I_{{sp}} \times g_0 = {Isp} \times {g0} = {ve:.4f} \; \text{{m/s}}",
            {"I_{sp}": f"{Isp} s", "g_0": f"{g0} m/s²"},
        ),
        make_substitution_step(
            "Compute mass ratio",
            rf"R = \frac{{m_0}}{{m_f}} = \frac{{{m0}}}{{{mf}}} = {mass_ratio:.6f}",
            {"m_0": f"{m0} kg", "m_f": f"{mf} kg"},
        ),
        make_substitution_step(
            "Compute delta-v",
            rf"\Delta v = {ve:.4f} \times \ln({mass_ratio:.6f}) = {delta_v:.4f} \; \text{{m/s}}",
            {"v_e": f"{ve:.4f} m/s", "R": f"{mass_ratio:.6f}"},
        ),
        make_result_step("Delta-v result", r"\Delta v", delta_v, "m/s"),
    ]

    return {
        "steps": steps,
        "results": {"delta_v": delta_v, "mass_ratio": mass_ratio, "ve": ve},
        "latex_summary": rf"\Delta v = {ve:.2f} \times \ln\left(\frac{{{m0}}}{{{mf}}}\right) = {delta_v:.4f} \; \text{{m/s}}",
    }


# ═══════════════════════════════════════════════════════════════════
# 2. THRUST-TO-WEIGHT RATIO
# ═══════════════════════════════════════════════════════════════════
@register_formula(
    id="aerospace.propulsion.thrust_to_weight",
    domain="aerospace",
    category="propulsion",
    name="Thrust-to-Weight Ratio",
    description="Calculate thrust-to-weight ratio (TWR). Must be >1 for vertical ascent. "
                "Typical values: launch vehicles 1.2-1.8, fighters 0.8-1.1, airliners 0.2-0.3.",
    formula_latex=r"TWR = \frac{F}{m \cdot g}",
    parameters=[
        {"name": "F", "symbol": "F", "unit": "N",
         "description": "Thrust force", "min_value": 0.0, "max_value": 1e9},
        {"name": "m", "symbol": "m", "unit": "kg",
         "description": "Vehicle mass", "min_value": 0.01, "max_value": 1e8},
        {"name": "g", "symbol": "g", "unit": "m/s²",
         "description": "Gravitational acceleration", "min_value": 0.1, "max_value": 25.0, "default": 9.80665},
    ],
    outputs=[
        {"name": "TWR", "symbol": "TWR", "unit": "-",
         "description": "Thrust-to-weight ratio"},
        {"name": "W", "symbol": "W", "unit": "N",
         "description": "Weight"},
    ],
    reference="Raymer, D.P., Aircraft Design: A Conceptual Approach, 6th Ed., Ch. 5",
    tags=["thrust", "weight", "TWR", "performance", "launch"],
)
def thrust_to_weight(F: float, m: float, g: float = 9.80665) -> dict:
    """Compute thrust-to-weight ratio."""
    W = m * g
    TWR = F / W if W > 0 else float("inf")

    assessment = (
        "Can sustain vertical ascent" if TWR > 1.0
        else "Cannot hover/ascend vertically" if TWR > 0
        else "No thrust"
    )

    steps = [
        make_symbolic_step(
            "Thrust-to-weight ratio definition",
            sp.Eq(sp.Symbol("TWR"), sp.Symbol("F") / (sp.Symbol("m") * sp.Symbol("g"))),
        ),
        make_substitution_step(
            "Compute weight",
            rf"W = m \times g = {m} \times {g} = {W:.4f} \; \text{{N}}",
            {"m": f"{m} kg", "g": f"{g} m/s²"},
        ),
        make_substitution_step(
            "Compute TWR",
            rf"TWR = \frac{{{F}}}{{{W:.4f}}} = {TWR:.6f}",
            {"F": f"{F} N", "W": f"{W:.4f} N"},
        ),
        make_result_step(f"TWR ({assessment})", "TWR", TWR, "-"),
    ]

    return {
        "steps": steps,
        "results": {"TWR": TWR, "W": W},
        "latex_summary": rf"TWR = \frac{{{F}}}{{{W:.2f}}} = {TWR:.4f} \quad \text{{({assessment})}}",
    }
