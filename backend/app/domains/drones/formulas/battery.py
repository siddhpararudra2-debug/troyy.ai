"""
Troy — Drone Battery Formulas
Battery sizing and energy calculations for UAV systems.

Formulas:
  1. Battery Energy Density
  2. Battery C-Rate & Max Current
"""

from __future__ import annotations

import sympy as sp

from app.calculations.registry import register_formula
from app.calculations.engine import make_symbolic_step, make_substitution_step, make_result_step


@register_formula(
    id="drones.battery.energy_density",
    domain="drones",
    category="battery",
    name="Battery Energy & Weight Analysis",
    description="Analyze battery energy density and its contribution to total drone weight. "
                "Critical for flight time optimization.",
    formula_latex=r"E = \frac{C \times V}{1000}, \quad \rho_E = \frac{E}{m_{batt}}",
    parameters=[
        {"name": "capacity_mah", "symbol": "C", "unit": "mAh",
         "description": "Battery capacity", "min_value": 100, "max_value": 100000},
        {"name": "voltage", "symbol": "V", "unit": "V",
         "description": "Nominal voltage", "min_value": 3.0, "max_value": 60.0},
        {"name": "mass_batt", "symbol": "m_{batt}", "unit": "kg",
         "description": "Battery mass", "min_value": 0.01, "max_value": 50.0},
        {"name": "mass_total", "symbol": "m_{total}", "unit": "kg",
         "description": "Total drone mass (AUW)", "min_value": 0.01, "max_value": 500.0},
    ],
    outputs=[
        {"name": "E_wh", "symbol": "E", "unit": "Wh", "description": "Total energy"},
        {"name": "energy_density", "symbol": r"\rho_E", "unit": "Wh/kg",
         "description": "Specific energy"},
        {"name": "batt_fraction", "symbol": "f_{batt}", "unit": "%",
         "description": "Battery weight fraction"},
    ],
    reference="Gundlach, J., Designing Unmanned Aircraft Systems, AIAA, Ch. 9",
    tags=["battery", "energy density", "LiPo", "weight fraction"],
)
def energy_density(capacity_mah: float, voltage: float, mass_batt: float, mass_total: float) -> dict:
    """Analyze battery energy density."""
    E_wh = (capacity_mah / 1000.0) * voltage
    specific_energy = E_wh / mass_batt if mass_batt > 0 else 0
    batt_fraction = (mass_batt / mass_total) * 100 if mass_total > 0 else 0

    steps = [
        make_substitution_step(
            "Compute total battery energy",
            rf"E = \frac{{{capacity_mah}}}{{1000}} \times {voltage} = {E_wh:.4f} \; \text{{Wh}}",
            {"C": f"{capacity_mah} mAh", "V": f"{voltage} V"},
        ),
        make_substitution_step(
            "Compute specific energy (energy density)",
            rf"\rho_E = \frac{{{E_wh:.4f}}}{{{mass_batt}}} = {specific_energy:.2f} \; \text{{Wh/kg}}",
            {"E": f"{E_wh:.4f} Wh", "m_batt": f"{mass_batt} kg"},
        ),
        make_substitution_step(
            "Compute battery weight fraction",
            rf"f_{{batt}} = \frac{{{mass_batt}}}{{{mass_total}}} \times 100 = {batt_fraction:.2f}\%",
            {"m_batt": f"{mass_batt} kg", "m_total": f"{mass_total} kg"},
        ),
        make_result_step("Battery energy", "E", E_wh, "Wh"),
        make_result_step("Specific energy", r"\rho_E", specific_energy, "Wh/kg"),
    ]

    return {
        "steps": steps,
        "results": {"E_wh": E_wh, "energy_density": specific_energy, "batt_fraction": batt_fraction},
        "latex_summary": rf"E = {E_wh:.2f} \; \text{{Wh}}, \quad \rho_E = {specific_energy:.2f} \; \text{{Wh/kg}}, \quad f_{{batt}} = {batt_fraction:.1f}\%",
    }


@register_formula(
    id="drones.battery.c_rate",
    domain="drones",
    category="battery",
    name="Battery C-Rate & Max Current",
    description="Calculate maximum continuous discharge current from C-rating. "
                "Exceeding the C-rate damages the battery and risks fire.",
    formula_latex=r"I_{max} = C_{rate} \times \frac{C_{capacity}}{1000}",
    parameters=[
        {"name": "capacity_mah", "symbol": "C_{cap}", "unit": "mAh",
         "description": "Battery capacity", "min_value": 100, "max_value": 100000},
        {"name": "c_rate", "symbol": "C_{rate}", "unit": "C",
         "description": "Continuous discharge C-rating", "min_value": 1, "max_value": 200},
        {"name": "voltage", "symbol": "V", "unit": "V",
         "description": "Nominal voltage", "min_value": 3.0, "max_value": 60.0},
    ],
    outputs=[
        {"name": "I_max", "symbol": "I_{max}", "unit": "A", "description": "Max continuous current"},
        {"name": "P_max", "symbol": "P_{max}", "unit": "W", "description": "Max continuous power"},
    ],
    reference="Battery University, Discharge Methods, Ch. 5",
    tags=["battery", "C-rate", "discharge", "current", "LiPo"],
)
def c_rate(capacity_mah: float, c_rate: float, voltage: float) -> dict:
    """Calculate max discharge current from C-rate."""
    I_max = c_rate * (capacity_mah / 1000.0)
    P_max = I_max * voltage

    steps = [
        make_substitution_step(
            "Convert capacity to Ah",
            rf"C_{{Ah}} = \frac{{{capacity_mah}}}{{1000}} = {capacity_mah/1000:.4f} \; \text{{Ah}}",
            {"C_cap": f"{capacity_mah} mAh"},
        ),
        make_substitution_step(
            "Compute max continuous current",
            rf"I_{{max}} = {c_rate} \times {capacity_mah/1000:.4f} = {I_max:.4f} \; \text{{A}}",
            {"C_rate": f"{c_rate} C", "C_Ah": f"{capacity_mah/1000:.4f} Ah"},
        ),
        make_substitution_step(
            "Compute max continuous power",
            rf"P_{{max}} = {I_max:.4f} \times {voltage} = {P_max:.4f} \; \text{{W}}",
            {"I_max": f"{I_max:.4f} A", "V": f"{voltage} V"},
        ),
        make_result_step("Max continuous current", "I_{max}", I_max, "A"),
        make_result_step("Max continuous power", "P_{max}", P_max, "W"),
    ]

    return {
        "steps": steps,
        "results": {"I_max": I_max, "P_max": P_max},
        "latex_summary": rf"I_{{max}} = {c_rate}C \times {capacity_mah/1000:.3f} \text{{Ah}} = {I_max:.2f} \; \text{{A}}, \quad P_{{max}} = {P_max:.2f} \; \text{{W}}",
    }
