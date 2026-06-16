"""
Troy — Aerospace Aerodynamics Formulas
Implements core aerodynamic calculations with full step-by-step SymPy traces.

Formulas:
  1. Lift Force (L = ½ρv²SC_L)
  2. Drag Force (D = ½ρv²SC_D)
  3. Bernoulli Equation (P₁ + ½ρv₁² = P₂ + ½ρv₂²)
  4. Dynamic Pressure (q = ½ρv²)
  5. Lift-to-Drag Ratio
"""

from __future__ import annotations

import sympy as sp

from app.calculations.registry import register_formula
from app.calculations.engine import make_symbolic_step, make_substitution_step, make_result_step


# ═══════════════════════════════════════════════════════════════════
# 1. LIFT FORCE
# ═══════════════════════════════════════════════════════════════════
@register_formula(
    id="aerospace.aerodynamics.lift_force",
    domain="aerospace",
    category="aerodynamics",
    name="Lift Force",
    description="Calculate aerodynamic lift force using the standard lift equation. "
                "Fundamental to wing design and aircraft performance analysis.",
    formula_latex=r"L = \frac{1}{2} \rho v^2 S C_L",
    parameters=[
        {"name": "rho", "symbol": r"\rho", "unit": "kg/m³",
         "description": "Air density", "min_value": 0.01, "max_value": 15.0, "default": 1.225},
        {"name": "v", "symbol": "v", "unit": "m/s",
         "description": "Freestream velocity", "min_value": 0.0, "max_value": 1000.0},
        {"name": "S", "symbol": "S", "unit": "m²",
         "description": "Wing planform area", "min_value": 0.01, "max_value": 1000.0},
        {"name": "C_L", "symbol": "C_L", "unit": "-",
         "description": "Lift coefficient", "min_value": -2.0, "max_value": 4.0},
    ],
    outputs=[
        {"name": "L", "symbol": "L", "unit": "N",
         "description": "Lift force"},
        {"name": "q", "symbol": "q", "unit": "Pa",
         "description": "Dynamic pressure"},
    ],
    reference="Anderson, J.D., Fundamentals of Aerodynamics, 6th Ed., McGraw-Hill, Ch. 1.5",
    tags=["lift", "wing", "airfoil", "subsonic", "aerodynamic force"],
)
def lift_force(rho: float, v: float, S: float, C_L: float) -> dict:
    """Compute lift force with full symbolic trace."""
    # ── Symbolic setup ───────────────────────────────────────
    rho_s, v_s, S_s, C_L_s = sp.symbols(r"\rho v S C_L", positive=True)
    L_s = sp.Rational(1, 2) * rho_s * v_s**2 * S_s * C_L_s
    q_s = sp.Rational(1, 2) * rho_s * v_s**2

    # ── Numerical computation ────────────────────────────────
    q_val = 0.5 * rho * v**2
    L_val = q_val * S * C_L

    # ── Build steps ──────────────────────────────────────────
    steps = [
        make_symbolic_step(
            "Start with the standard lift equation",
            sp.Eq(sp.Symbol("L"), L_s),
            {r"\rho": "air density", "v": "velocity", "S": "wing area", "C_L": "lift coefficient"},
        ),
        make_symbolic_step(
            "First compute dynamic pressure",
            sp.Eq(sp.Symbol("q"), q_s),
        ),
        make_substitution_step(
            "Substitute known values into dynamic pressure",
            rf"q = \frac{{1}}{{2}} \times {rho} \times {v}^2 = {q_val:.4f} \; \text{{Pa}}",
            {r"\rho": f"{rho} kg/m³", "v": f"{v} m/s"},
        ),
        make_substitution_step(
            "Substitute all values into lift equation",
            rf"L = {q_val:.4f} \times {S} \times {C_L} = {L_val:.4f} \; \text{{N}}",
            {"q": f"{q_val:.4f} Pa", "S": f"{S} m²", "C_L": f"{C_L}"},
        ),
        make_result_step("Final lift force", "L", L_val, "N"),
    ]

    return {
        "steps": steps,
        "results": {"L": L_val, "q": q_val},
        "latex_summary": rf"L = \frac{{1}}{{2}} \times {rho} \times {v}^2 \times {S} \times {C_L} = {L_val:.4f} \; \text{{N}}",
    }


# ═══════════════════════════════════════════════════════════════════
# 2. DRAG FORCE
# ═══════════════════════════════════════════════════════════════════
@register_formula(
    id="aerospace.aerodynamics.drag_force",
    domain="aerospace",
    category="aerodynamics",
    name="Drag Force",
    description="Calculate aerodynamic drag force. Critical for performance, "
                "fuel consumption, and propulsion sizing.",
    formula_latex=r"D = \frac{1}{2} \rho v^2 S C_D",
    parameters=[
        {"name": "rho", "symbol": r"\rho", "unit": "kg/m³",
         "description": "Air density", "min_value": 0.01, "max_value": 15.0, "default": 1.225},
        {"name": "v", "symbol": "v", "unit": "m/s",
         "description": "Freestream velocity", "min_value": 0.0, "max_value": 1000.0},
        {"name": "S", "symbol": "S", "unit": "m²",
         "description": "Reference area", "min_value": 0.01, "max_value": 1000.0},
        {"name": "C_D", "symbol": "C_D", "unit": "-",
         "description": "Drag coefficient", "min_value": 0.0, "max_value": 3.0},
    ],
    outputs=[
        {"name": "D", "symbol": "D", "unit": "N",
         "description": "Drag force"},
    ],
    reference="Anderson, J.D., Fundamentals of Aerodynamics, 6th Ed., Ch. 1.5",
    tags=["drag", "parasitic", "induced", "aerodynamic force"],
)
def drag_force(rho: float, v: float, S: float, C_D: float) -> dict:
    """Compute drag force with full symbolic trace."""
    rho_s, v_s, S_s, C_D_s = sp.symbols(r"\rho v S C_D", positive=True)
    D_s = sp.Rational(1, 2) * rho_s * v_s**2 * S_s * C_D_s

    q_val = 0.5 * rho * v**2
    D_val = q_val * S * C_D

    steps = [
        make_symbolic_step(
            "Start with the standard drag equation",
            sp.Eq(sp.Symbol("D"), D_s),
        ),
        make_substitution_step(
            "Compute dynamic pressure",
            rf"q = \frac{{1}}{{2}} \times {rho} \times {v}^2 = {q_val:.4f} \; \text{{Pa}}",
            {r"\rho": f"{rho} kg/m³", "v": f"{v} m/s"},
        ),
        make_substitution_step(
            "Substitute into drag equation",
            rf"D = {q_val:.4f} \times {S} \times {C_D} = {D_val:.4f} \; \text{{N}}",
            {"q": f"{q_val:.4f} Pa", "S": f"{S} m²", "C_D": f"{C_D}"},
        ),
        make_result_step("Final drag force", "D", D_val, "N"),
    ]

    return {
        "steps": steps,
        "results": {"D": D_val},
        "latex_summary": rf"D = \frac{{1}}{{2}} \times {rho} \times {v}^2 \times {S} \times {C_D} = {D_val:.4f} \; \text{{N}}",
    }


# ═══════════════════════════════════════════════════════════════════
# 3. DYNAMIC PRESSURE
# ═══════════════════════════════════════════════════════════════════
@register_formula(
    id="aerospace.aerodynamics.dynamic_pressure",
    domain="aerospace",
    category="aerodynamics",
    name="Dynamic Pressure",
    description="Calculate dynamic pressure — the kinetic energy per unit volume "
                "of the airflow. Foundation for all aerodynamic force calculations.",
    formula_latex=r"q = \frac{1}{2} \rho v^2",
    parameters=[
        {"name": "rho", "symbol": r"\rho", "unit": "kg/m³",
         "description": "Air density", "min_value": 0.01, "max_value": 15.0, "default": 1.225},
        {"name": "v", "symbol": "v", "unit": "m/s",
         "description": "Freestream velocity", "min_value": 0.0, "max_value": 1000.0},
    ],
    outputs=[
        {"name": "q", "symbol": "q", "unit": "Pa",
         "description": "Dynamic pressure"},
    ],
    reference="Anderson, J.D., Fundamentals of Aerodynamics, 6th Ed., Ch. 1.4",
    tags=["dynamic pressure", "velocity", "kinetic energy", "flow"],
)
def dynamic_pressure(rho: float, v: float) -> dict:
    """Compute dynamic pressure."""
    rho_s, v_s = sp.symbols(r"\rho v", positive=True)
    q_s = sp.Rational(1, 2) * rho_s * v_s**2

    q_val = 0.5 * rho * v**2

    steps = [
        make_symbolic_step("Dynamic pressure equation", sp.Eq(sp.Symbol("q"), q_s)),
        make_substitution_step(
            "Substitute values",
            rf"q = \frac{{1}}{{2}} \times {rho} \times {v}^2 = {q_val:.4f} \; \text{{Pa}}",
            {r"\rho": f"{rho} kg/m³", "v": f"{v} m/s"},
        ),
        make_result_step("Dynamic pressure result", "q", q_val, "Pa"),
    ]

    return {
        "steps": steps,
        "results": {"q": q_val},
        "latex_summary": rf"q = \frac{{1}}{{2}} \times {rho} \times {v}^2 = {q_val:.4f} \; \text{{Pa}}",
    }


# ═══════════════════════════════════════════════════════════════════
# 4. MACH NUMBER
# ═══════════════════════════════════════════════════════════════════
@register_formula(
    id="aerospace.aerodynamics.mach_number",
    domain="aerospace",
    category="aerodynamics",
    name="Mach Number",
    description="Calculate the Mach number — ratio of flow velocity to the local speed of sound. "
                "Determines flow regime: subsonic (M<0.8), transonic (0.8<M<1.2), supersonic (M>1.2).",
    formula_latex=r"M = \frac{v}{a} = \frac{v}{\sqrt{\gamma R T}}",
    parameters=[
        {"name": "v", "symbol": "v", "unit": "m/s",
         "description": "Flow velocity", "min_value": 0.0, "max_value": 10000.0},
        {"name": "T", "symbol": "T", "unit": "K",
         "description": "Static temperature", "min_value": 50.0, "max_value": 5000.0, "default": 288.15},
        {"name": "gamma", "symbol": r"\gamma", "unit": "-",
         "description": "Ratio of specific heats", "min_value": 1.0, "max_value": 1.67, "default": 1.4},
        {"name": "R", "symbol": "R", "unit": "J/(kg·K)",
         "description": "Specific gas constant", "min_value": 100.0, "max_value": 500.0, "default": 287.058},
    ],
    outputs=[
        {"name": "M", "symbol": "M", "unit": "-", "description": "Mach number"},
        {"name": "a", "symbol": "a", "unit": "m/s", "description": "Speed of sound"},
    ],
    reference="Anderson, J.D., Modern Compressible Flow, 3rd Ed., Ch. 1",
    tags=["mach", "compressible", "speed of sound", "supersonic", "subsonic"],
)
def mach_number(v: float, T: float = 288.15, gamma: float = 1.4, R: float = 287.058) -> dict:
    """Compute Mach number and speed of sound."""
    import math

    a_val = math.sqrt(gamma * R * T)
    M_val = v / a_val if a_val > 0 else 0

    # Determine flow regime
    if M_val < 0.3:
        regime = "Incompressible"
    elif M_val < 0.8:
        regime = "Subsonic"
    elif M_val < 1.2:
        regime = "Transonic"
    elif M_val < 5.0:
        regime = "Supersonic"
    else:
        regime = "Hypersonic"

    v_s, T_s, gamma_s, R_s = sp.symbols(r"v T \gamma R", positive=True)
    a_s = sp.sqrt(gamma_s * R_s * T_s)
    M_s = v_s / a_s

    steps = [
        make_symbolic_step(
            "Speed of sound from ideal gas relation",
            sp.Eq(sp.Symbol("a"), a_s),
        ),
        make_substitution_step(
            "Compute speed of sound",
            rf"a = \sqrt{{{gamma} \times {R} \times {T}}} = {a_val:.4f} \; \text{{m/s}}",
            {r"\gamma": str(gamma), "R": f"{R} J/(kg·K)", "T": f"{T} K"},
        ),
        make_symbolic_step(
            "Mach number definition",
            sp.Eq(sp.Symbol("M"), M_s),
        ),
        make_substitution_step(
            "Compute Mach number",
            rf"M = \frac{{{v}}}{{{a_val:.4f}}} = {M_val:.6f}",
            {"v": f"{v} m/s", "a": f"{a_val:.4f} m/s"},
        ),
        make_result_step(f"Mach number ({regime} regime)", "M", M_val, "-"),
    ]

    return {
        "steps": steps,
        "results": {"M": M_val, "a": a_val},
        "latex_summary": rf"M = \frac{{{v}}}{{{a_val:.4f}}} = {M_val:.6f} \quad \text{{({regime})}}",
    }


# ═══════════════════════════════════════════════════════════════════
# 5. REYNOLDS NUMBER
# ═══════════════════════════════════════════════════════════════════
@register_formula(
    id="aerospace.aerodynamics.reynolds_number",
    domain="aerospace",
    category="aerodynamics",
    name="Reynolds Number",
    description="Calculate the Reynolds number — ratio of inertial to viscous forces. "
                "Determines flow character: laminar (Re < 5×10⁵) or turbulent (Re > 5×10⁵).",
    formula_latex=r"Re = \frac{\rho v L}{\mu}",
    parameters=[
        {"name": "rho", "symbol": r"\rho", "unit": "kg/m³",
         "description": "Fluid density", "min_value": 0.01, "max_value": 15.0, "default": 1.225},
        {"name": "v", "symbol": "v", "unit": "m/s",
         "description": "Flow velocity", "min_value": 0.0, "max_value": 1000.0},
        {"name": "L", "symbol": "L", "unit": "m",
         "description": "Characteristic length", "min_value": 0.001, "max_value": 100.0},
        {"name": "mu", "symbol": r"\mu", "unit": "Pa·s",
         "description": "Dynamic viscosity", "min_value": 1e-7, "max_value": 1.0, "default": 1.789e-5},
    ],
    outputs=[
        {"name": "Re", "symbol": "Re", "unit": "-", "description": "Reynolds number"},
    ],
    reference="Anderson, J.D., Fundamentals of Aerodynamics, 6th Ed., Ch. 1.8",
    tags=["reynolds", "viscous", "laminar", "turbulent", "boundary layer"],
)
def reynolds_number(rho: float, v: float, L: float, mu: float = 1.789e-5) -> dict:
    """Compute Reynolds number."""
    Re_val = (rho * v * L) / mu if mu > 0 else float("inf")

    regime = "Laminar" if Re_val < 5e5 else "Turbulent"

    rho_s, v_s, L_s, mu_s = sp.symbols(r"\rho v L \mu", positive=True)
    Re_s = (rho_s * v_s * L_s) / mu_s

    steps = [
        make_symbolic_step("Reynolds number definition", sp.Eq(sp.Symbol("Re"), Re_s)),
        make_substitution_step(
            "Substitute values",
            rf"Re = \frac{{{rho} \times {v} \times {L}}}{{{mu:.6e}}} = {Re_val:.2f}",
            {r"\rho": f"{rho} kg/m³", "v": f"{v} m/s", "L": f"{L} m", r"\mu": f"{mu:.6e} Pa·s"},
        ),
        make_result_step(f"Reynolds number ({regime} flow)", "Re", Re_val, "-"),
    ]

    return {
        "steps": steps,
        "results": {"Re": Re_val},
        "latex_summary": rf"Re = {Re_val:.2f} \quad \text{{({regime})}}",
    }
