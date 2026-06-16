"""
Troy — Electronics Circuit Analysis Formulas
Core electronics and circuit calculations.

Formulas:
  1. Ohm's Law (V = IR)
  2. Voltage Divider
  3. RC Time Constant
  4. Power Dissipation
  5. LED Resistor Calculator
"""

from __future__ import annotations

import math
import sympy as sp

from app.calculations.registry import register_formula
from app.calculations.engine import make_symbolic_step, make_substitution_step, make_result_step


# ═══════════════════════════════════════════════════════════════════
# 1. OHM'S LAW
# ═══════════════════════════════════════════════════════════════════
@register_formula(
    id="electronics.circuit_analysis.ohms_law",
    domain="electronics",
    category="circuit_analysis",
    name="Ohm's Law",
    description="The fundamental relationship between voltage, current, and resistance. "
                "Solve for any one quantity given the other two.",
    formula_latex=r"V = I \times R",
    parameters=[
        {"name": "V", "symbol": "V", "unit": "V",
         "description": "Voltage (leave 0 to solve for it)", "min_value": 0.0, "max_value": 100000.0, "default": 0.0},
        {"name": "I", "symbol": "I", "unit": "A",
         "description": "Current (leave 0 to solve for it)", "min_value": 0.0, "max_value": 10000.0, "default": 0.0},
        {"name": "R", "symbol": "R", "unit": "Ω",
         "description": "Resistance (leave 0 to solve for it)", "min_value": 0.0, "max_value": 1e9, "default": 0.0},
    ],
    outputs=[
        {"name": "V", "symbol": "V", "unit": "V", "description": "Voltage"},
        {"name": "I", "symbol": "I", "unit": "A", "description": "Current"},
        {"name": "R", "symbol": "R", "unit": "Ω", "description": "Resistance"},
        {"name": "P", "symbol": "P", "unit": "W", "description": "Power dissipated"},
    ],
    reference="Horowitz & Hill, The Art of Electronics, 3rd Ed., Ch. 1",
    tags=["ohm", "voltage", "current", "resistance", "basic"],
)
def ohms_law(V: float = 0.0, I: float = 0.0, R: float = 0.0) -> dict:
    """Compute Ohm's law — solve for the missing quantity."""
    # Determine which value to solve for
    given = sum(1 for x in [V, I, R] if x > 0)

    if given < 2:
        raise ValueError("Provide at least 2 of the 3 values (V, I, R). Set the unknown to 0.")

    steps = [
        make_symbolic_step(
            "Ohm's Law",
            sp.Eq(sp.Symbol("V"), sp.Symbol("I") * sp.Symbol("R")),
        ),
    ]

    if V == 0 and I > 0 and R > 0:
        V = I * R
        steps.append(make_substitution_step(
            "Solve for voltage",
            rf"V = I \times R = {I} \times {R} = {V:.6g} \; \text{{V}}",
            {"I": f"{I} A", "R": f"{R} Ω"},
        ))
    elif I == 0 and V > 0 and R > 0:
        I = V / R
        steps.append(make_substitution_step(
            "Solve for current",
            rf"I = \frac{{V}}{{R}} = \frac{{{V}}}{{{R}}} = {I:.6g} \; \text{{A}}",
            {"V": f"{V} V", "R": f"{R} Ω"},
        ))
    elif R == 0 and V > 0 and I > 0:
        R = V / I
        steps.append(make_substitution_step(
            "Solve for resistance",
            rf"R = \frac{{V}}{{I}} = \frac{{{V}}}{{{I}}} = {R:.6g} \; \text{{\Omega}}",
            {"V": f"{V} V", "I": f"{I} A"},
        ))

    P = V * I
    steps.append(make_substitution_step(
        "Compute power dissipation",
        rf"P = V \times I = {V:.6g} \times {I:.6g} = {P:.6g} \; \text{{W}}",
        {"V": f"{V:.6g} V", "I": f"{I:.6g} A"},
    ))
    steps.append(make_result_step("Power dissipated", "P", P, "W"))

    return {
        "steps": steps,
        "results": {"V": V, "I": I, "R": R, "P": P},
        "latex_summary": rf"V = {V:.6g} \; \text{{V}}, \; I = {I:.6g} \; \text{{A}}, \; R = {R:.6g} \; \Omega, \; P = {P:.6g} \; \text{{W}}",
    }


# ═══════════════════════════════════════════════════════════════════
# 2. VOLTAGE DIVIDER
# ═══════════════════════════════════════════════════════════════════
@register_formula(
    id="electronics.circuit_analysis.voltage_divider",
    domain="electronics",
    category="circuit_analysis",
    name="Voltage Divider",
    description="Calculate output voltage of a resistive voltage divider. "
                "One of the most common circuits in electronics.",
    formula_latex=r"V_{out} = V_{in} \times \frac{R_2}{R_1 + R_2}",
    parameters=[
        {"name": "V_in", "symbol": "V_{in}", "unit": "V",
         "description": "Input voltage", "min_value": 0.0, "max_value": 100000.0},
        {"name": "R1", "symbol": "R_1", "unit": "Ω",
         "description": "Top resistor (series)", "min_value": 0.1, "max_value": 1e9},
        {"name": "R2", "symbol": "R_2", "unit": "Ω",
         "description": "Bottom resistor (to ground)", "min_value": 0.1, "max_value": 1e9},
    ],
    outputs=[
        {"name": "V_out", "symbol": "V_{out}", "unit": "V", "description": "Output voltage"},
        {"name": "ratio", "symbol": "k", "unit": "-", "description": "Division ratio"},
        {"name": "I_total", "symbol": "I", "unit": "A", "description": "Current through divider"},
    ],
    reference="Horowitz & Hill, The Art of Electronics, 3rd Ed., Ch. 1.2",
    tags=["voltage divider", "resistor", "bias", "analog"],
)
def voltage_divider(V_in: float, R1: float, R2: float) -> dict:
    """Calculate voltage divider output."""
    ratio = R2 / (R1 + R2)
    V_out = V_in * ratio
    I_total = V_in / (R1 + R2)

    steps = [
        make_symbolic_step(
            "Voltage divider equation",
            sp.Eq(
                sp.Symbol("V_{out}"),
                sp.Symbol("V_{in}") * sp.Symbol("R_2") / (sp.Symbol("R_1") + sp.Symbol("R_2"))
            ),
        ),
        make_substitution_step(
            "Compute division ratio",
            rf"k = \frac{{R_2}}{{R_1 + R_2}} = \frac{{{R2}}}{{{R1} + {R2}}} = {ratio:.6f}",
            {"R_1": f"{R1} Ω", "R_2": f"{R2} Ω"},
        ),
        make_substitution_step(
            "Compute output voltage",
            rf"V_{{out}} = {V_in} \times {ratio:.6f} = {V_out:.6g} \; \text{{V}}",
            {"V_{in}": f"{V_in} V", "k": f"{ratio:.6f}"},
        ),
        make_substitution_step(
            "Compute divider current (no load)",
            rf"I = \frac{{V_{{in}}}}{{R_1 + R_2}} = \frac{{{V_in}}}{{{R1 + R2:.1f}}} = {I_total:.6g} \; \text{{A}}",
            {"V_{in}": f"{V_in} V", "R_total": f"{R1 + R2:.1f} Ω"},
        ),
        make_result_step("Output voltage", "V_{out}", V_out, "V"),
    ]

    return {
        "steps": steps,
        "results": {"V_out": V_out, "ratio": ratio, "I_total": I_total},
        "latex_summary": rf"V_{{out}} = {V_in} \times \frac{{{R2}}}{{{R1} + {R2}}} = {V_out:.6g} \; \text{{V}}",
    }


# ═══════════════════════════════════════════════════════════════════
# 3. RC TIME CONSTANT
# ═══════════════════════════════════════════════════════════════════
@register_formula(
    id="electronics.circuit_analysis.rc_time_constant",
    domain="electronics",
    category="circuit_analysis",
    name="RC Time Constant",
    description="Calculate the time constant of an RC circuit. After 1τ the capacitor "
                "charges to 63.2%, after 5τ it reaches 99.3%.",
    formula_latex=r"\tau = R \times C",
    parameters=[
        {"name": "R", "symbol": "R", "unit": "Ω",
         "description": "Resistance", "min_value": 0.1, "max_value": 1e9},
        {"name": "C", "symbol": "C", "unit": "F",
         "description": "Capacitance", "min_value": 1e-15, "max_value": 1.0},
    ],
    outputs=[
        {"name": "tau", "symbol": r"\tau", "unit": "s", "description": "Time constant"},
        {"name": "f_cutoff", "symbol": "f_c", "unit": "Hz",
         "description": "Cutoff frequency (-3dB)"},
        {"name": "t_99", "symbol": "t_{99}", "unit": "s",
         "description": "Time to 99.3% charge (5τ)"},
    ],
    reference="Horowitz & Hill, The Art of Electronics, 3rd Ed., Ch. 1.4",
    tags=["RC", "time constant", "capacitor", "filter", "charging"],
)
def rc_time_constant(R: float, C: float) -> dict:
    """Calculate RC time constant and related parameters."""
    tau = R * C
    f_cutoff = 1.0 / (2 * math.pi * tau) if tau > 0 else float("inf")
    t_99 = 5 * tau

    steps = [
        make_symbolic_step(
            "RC time constant",
            sp.Eq(sp.Symbol(r"\tau"), sp.Symbol("R") * sp.Symbol("C")),
        ),
        make_substitution_step(
            "Compute time constant",
            rf"\tau = {R:.6g} \times {C:.6g} = {tau:.6g} \; \text{{s}}",
            {"R": f"{R} Ω", "C": f"{C} F"},
        ),
        make_substitution_step(
            "Compute -3dB cutoff frequency",
            rf"f_c = \frac{{1}}{{2\pi\tau}} = \frac{{1}}{{2\pi \times {tau:.6g}}} = {f_cutoff:.6g} \; \text{{Hz}}",
            {r"\tau": f"{tau:.6g} s"},
        ),
        make_substitution_step(
            "Time to 99.3% charge (5 time constants)",
            rf"t_{{99}} = 5\tau = 5 \times {tau:.6g} = {t_99:.6g} \; \text{{s}}",
            {r"\tau": f"{tau:.6g} s"},
        ),
        make_result_step("Time constant", r"\tau", tau, "s"),
        make_result_step("Cutoff frequency", "f_c", f_cutoff, "Hz"),
    ]

    return {
        "steps": steps,
        "results": {"tau": tau, "f_cutoff": f_cutoff, "t_99": t_99},
        "latex_summary": rf"\tau = {tau:.6g} \; \text{{s}}, \quad f_c = {f_cutoff:.6g} \; \text{{Hz}}",
    }


# ═══════════════════════════════════════════════════════════════════
# 4. LED RESISTOR CALCULATOR
# ═══════════════════════════════════════════════════════════════════
@register_formula(
    id="electronics.circuit_analysis.led_resistor",
    domain="electronics",
    category="circuit_analysis",
    name="LED Series Resistor",
    description="Calculate the current-limiting resistor needed for an LED. "
                "Prevents LED burnout by controlling forward current.",
    formula_latex=r"R = \frac{V_{supply} - V_{LED}}{I_{LED}}",
    parameters=[
        {"name": "V_supply", "symbol": "V_{supply}", "unit": "V",
         "description": "Supply voltage", "min_value": 1.0, "max_value": 100.0},
        {"name": "V_led", "symbol": "V_{LED}", "unit": "V",
         "description": "LED forward voltage", "min_value": 0.5, "max_value": 10.0, "default": 2.0},
        {"name": "I_led_ma", "symbol": "I_{LED}", "unit": "mA",
         "description": "Desired LED current", "min_value": 1.0, "max_value": 1000.0, "default": 20.0},
    ],
    outputs=[
        {"name": "R", "symbol": "R", "unit": "Ω", "description": "Required resistance"},
        {"name": "P_resistor", "symbol": "P_R", "unit": "mW",
         "description": "Power dissipated in resistor"},
        {"name": "P_led", "symbol": "P_{LED}", "unit": "mW",
         "description": "Power dissipated in LED"},
    ],
    reference="Practical Electronics for Inventors, 4th Ed., Ch. 5",
    tags=["LED", "resistor", "current limiting", "digital output"],
)
def led_resistor(V_supply: float, V_led: float = 2.0, I_led_ma: float = 20.0) -> dict:
    """Calculate LED current-limiting resistor."""
    if V_supply <= V_led:
        raise ValueError(f"Supply voltage ({V_supply}V) must exceed LED forward voltage ({V_led}V)")

    I_led = I_led_ma / 1000.0
    V_drop = V_supply - V_led
    R = V_drop / I_led
    P_resistor = V_drop * I_led * 1000  # mW
    P_led = V_led * I_led * 1000  # mW

    # Suggest standard resistor value
    standard_values = [10, 22, 33, 47, 68, 100, 150, 220, 330, 470, 680,
                       1000, 1500, 2200, 3300, 4700, 6800, 10000]
    R_standard = min(standard_values, key=lambda x: abs(x - R) if x >= R * 0.9 else float("inf"))

    steps = [
        make_symbolic_step(
            "LED resistor equation",
            sp.Eq(
                sp.Symbol("R"),
                (sp.Symbol("V_{supply}") - sp.Symbol("V_{LED}")) / sp.Symbol("I_{LED}")
            ),
        ),
        make_substitution_step(
            "Compute voltage drop across resistor",
            rf"V_R = V_{{supply}} - V_{{LED}} = {V_supply} - {V_led} = {V_drop:.4f} \; \text{{V}}",
            {"V_{supply}": f"{V_supply} V", "V_{LED}": f"{V_led} V"},
        ),
        make_substitution_step(
            "Compute required resistance",
            rf"R = \frac{{{V_drop:.4f}}}{{{I_led:.6f}}} = {R:.2f} \; \Omega",
            {"V_R": f"{V_drop:.4f} V", "I_{LED}": f"{I_led_ma} mA = {I_led:.6f} A"},
        ),
        make_substitution_step(
            f"Nearest standard resistor value: {R_standard}Ω",
            rf"R_{{std}} = {R_standard} \; \Omega \quad \text{{(E24 series)}}",
            {"R_calc": f"{R:.2f} Ω"},
        ),
        make_substitution_step(
            "Power dissipated in resistor",
            rf"P_R = V_R \times I = {V_drop:.4f} \times {I_led:.6f} = {P_resistor:.2f} \; \text{{mW}}",
            {"V_R": f"{V_drop:.4f} V", "I": f"{I_led:.6f} A"},
        ),
        make_result_step("Required resistance", "R", R, "Ω"),
    ]

    return {
        "steps": steps,
        "results": {"R": R, "P_resistor": P_resistor, "P_led": P_led},
        "latex_summary": rf"R = \frac{{{V_supply} - {V_led}}}{{{I_led_ma} \; \text{{mA}}}} = {R:.2f} \; \Omega \quad (\text{{use }} {R_standard} \; \Omega)",
    }
