"""
Engineering formula library with comprehensive engineering formulas.
"""
from dataclasses import dataclass


@dataclass
class Formula:
    """An engineering formula with metadata."""
    id: str
    name: str
    category: str
    domain: str
    formula_latex: str
    description: str
    parameters: list[dict]
    outputs: list[dict]
    reference: str = ""
    tags: list[str] = None


FORMULA_LIBRARY = {
    # ===== Mechanical Engineering =====
    "stress_axial": Formula(
        id="stress_axial", name="Axial Stress", category="stress_analysis", domain="mechanical",
        formula_latex="\\sigma = \\frac{F}{A}",
        description="Normal stress due to axial loading",
        parameters=[
            {"name": "Force", "symbol": "F", "unit": "N", "description": "Applied axial force"},
            {"name": "Area", "symbol": "A", "unit": "m²", "description": "Cross-sectional area"},
        ],
        outputs=[{"name": "Stress", "symbol": "σ", "unit": "Pa", "description": "Normal stress"}],
        reference="Mechanics of Materials, Beer & Johnston", tags=["stress", "axial", "mechanical"],
    ),
    "bending_stress": Formula(
        id="bending_stress", name="Bending Stress", category="stress_analysis", domain="mechanical",
        formula_latex="\\sigma = \\frac{Mc}{I}",
        description="Maximum bending stress in a beam",
        parameters=[
            {"name": "Moment", "symbol": "M", "unit": "N·m", "description": "Bending moment"},
            {"name": "Distance", "symbol": "c", "unit": "m", "description": "Distance from neutral axis"},
            {"name": "Inertia", "symbol": "I", "unit": "m⁴", "description": "Area moment of inertia"},
        ],
        outputs=[{"name": "Bending Stress", "symbol": "σ", "unit": "Pa", "description": "Bending stress"}],
    ),
    "shear_stress": Formula(
        id="shear_stress", name="Shear Stress", category="stress_analysis", domain="mechanical",
        formula_latex="\\tau = \\frac{VQ}{Ib}",
        description="Transverse shear stress in a beam",
        parameters=[
            {"name": "Shear Force", "symbol": "V", "unit": "N", "description": "Internal shear force"},
            {"name": "First Moment", "symbol": "Q", "unit": "m³", "description": "First moment of area"},
            {"name": "Inertia", "symbol": "I", "unit": "m⁴", "description": "Area moment of inertia"},
            {"name": "Width", "symbol": "b", "unit": "m", "description": "Width at section"},
        ],
        outputs=[{"name": "Shear Stress", "symbol": "τ", "unit": "Pa", "description": "Shear stress"}],
    ),
    "torsion": Formula(
        id="torsion", name="Torsional Shear Stress", category="stress_analysis", domain="mechanical",
        formula_latex="\\tau = \\frac{Tr}{J}",
        description="Shear stress due to torsion",
        parameters=[
            {"name": "Torque", "symbol": "T", "unit": "N·m", "description": "Applied torque"},
            {"name": "Radius", "symbol": "r", "unit": "m", "description": "Radial distance"},
            {"name": "Polar Inertia", "symbol": "J", "unit": "m⁴", "description": "Polar moment of inertia"},
        ],
        outputs=[{"name": "Torsional Stress", "symbol": "τ", "unit": "Pa"}],
    ),
    "euler_buckling": Formula(
        id="euler_buckling", name="Euler Buckling", category="stability", domain="mechanical",
        formula_latex="P_{cr} = \\frac{\\pi^2 EI}{(KL)^2}",
        description="Critical buckling load for columns",
        parameters=[
            {"name": "Elastic Modulus", "symbol": "E", "unit": "Pa", "description": "Young's modulus"},
            {"name": "Inertia", "symbol": "I", "unit": "m⁴", "description": "Area moment of inertia"},
            {"name": "Length", "symbol": "L", "unit": "m", "description": "Column length"},
            {"name": "K Factor", "symbol": "K", "unit": "", "description": "Effective length factor"},
        ],
        outputs=[{"name": "Critical Load", "symbol": "P_cr", "unit": "N"}],
    ),
    "beam_deflection": Formula(
        id="beam_deflection", name="Beam Deflection (Center Load)", category="deflection", domain="mechanical",
        formula_latex="\\delta = \\frac{PL^3}{48EI}",
        description="Deflection of simply supported beam with point load at center",
        parameters=[
            {"name": "Load", "symbol": "P", "unit": "N"},
            {"name": "Length", "symbol": "L", "unit": "m"},
            {"name": "Modulus", "symbol": "E", "unit": "Pa"},
            {"name": "Inertia", "symbol": "I", "unit": "m⁴"},
        ],
        outputs=[{"name": "Deflection", "symbol": "δ", "unit": "m"}],
    ),
    # ===== Aerospace =====
    "lift": Formula(
        id="lift", name="Lift Force", category="aerodynamics", domain="aerospace",
        formula_latex="L = \\frac{1}{2} \\rho v^2 S C_L",
        description="Aerodynamic lift force",
        parameters=[
            {"name": "Air Density", "symbol": "ρ", "unit": "kg/m³"},
            {"name": "Velocity", "symbol": "v", "unit": "m/s"},
            {"name": "Wing Area", "symbol": "S", "unit": "m²"},
            {"name": "Lift Coefficient", "symbol": "C_L", "unit": ""},
        ],
        outputs=[{"name": "Lift", "symbol": "L", "unit": "N"}],
    ),
    "drag": Formula(
        id="drag", name="Drag Force", category="aerodynamics", domain="aerospace",
        formula_latex="D = \\frac{1}{2} \\rho v^2 S C_D",
        description="Aerodynamic drag force",
        parameters=[
            {"name": "Air Density", "symbol": "ρ", "unit": "kg/m³"},
            {"name": "Velocity", "symbol": "v", "unit": "m/s"},
            {"name": "Area", "symbol": "S", "unit": "m²"},
            {"name": "Drag Coefficient", "symbol": "C_D", "unit": ""},
        ],
        outputs=[{"name": "Drag", "symbol": "D", "unit": "N"}],
    ),
    "reynolds": Formula(
        id="reynolds", name="Reynolds Number", category="fluid_mechanics", domain="aerospace",
        formula_latex="Re = \\frac{\\rho v L}{\\mu}",
        description="Reynolds number for flow regime characterization",
        parameters=[
            {"name": "Density", "symbol": "ρ", "unit": "kg/m³"},
            {"name": "Velocity", "symbol": "v", "unit": "m/s"},
            {"name": "Length", "symbol": "L", "unit": "m"},
            {"name": "Dynamic Viscosity", "symbol": "μ", "unit": "Pa·s"},
        ],
        outputs=[{"name": "Reynolds Number", "symbol": "Re", "unit": ""}],
    ),
    # ===== Electrical =====
    "ohms_law": Formula(
        id="ohms_law", name="Ohm's Law", category="circuits", domain="electrical",
        formula_latex="V = IR",
        description="Voltage-current-resistance relationship",
        parameters=[
            {"name": "Current", "symbol": "I", "unit": "A"},
            {"name": "Resistance", "symbol": "R", "unit": "Ω"},
        ],
        outputs=[{"name": "Voltage", "symbol": "V", "unit": "V"}],
    ),
    "power_electrical": Formula(
        id="power_electrical", name="Electrical Power", category="circuits", domain="electrical",
        formula_latex="P = VI = I^2R = \\frac{V^2}{R}",
        description="Electrical power in DC circuits",
        parameters=[
            {"name": "Voltage", "symbol": "V", "unit": "V"},
            {"name": "Current", "symbol": "I", "unit": "A"},
        ],
        outputs=[{"name": "Power", "symbol": "P", "unit": "W"}],
    ),
    # ===== Thermal =====
    "heat_conduction": Formula(
        id="heat_conduction", name="Fourier's Law", category="heat_transfer", domain="thermal",
        formula_latex="Q = \\frac{kA\\Delta T}{L}",
        description="One-dimensional heat conduction",
        parameters=[
            {"name": "Conductivity", "symbol": "k", "unit": "W/(m·K)"},
            {"name": "Area", "symbol": "A", "unit": "m²"},
            {"name": "Temp Diff", "symbol": "ΔT", "unit": "K"},
            {"name": "Length", "symbol": "L", "unit": "m"},
        ],
        outputs=[{"name": "Heat Flow", "symbol": "Q", "unit": "W"}],
    ),
    "ideal_gas": Formula(
        id="ideal_gas", name="Ideal Gas Law", category="thermodynamics", domain="thermal",
        formula_latex="PV = nRT",
        description="Ideal gas equation of state",
        parameters=[
            {"name": "Pressure", "symbol": "P", "unit": "Pa"},
            {"name": "Volume", "symbol": "V", "unit": "m³"},
            {"name": "Moles", "symbol": "n", "unit": "mol"},
        ],
        outputs=[{"name": "Temperature", "symbol": "T", "unit": "K"}],
    ),
}


def get_formula(formula_id: str) -> Formula:
    """Get a formula by ID."""
    if formula_id in FORMULA_LIBRARY:
        return FORMULA_LIBRARY[formula_id]
    raise KeyError(f"Formula '{formula_id}' not found")


def search_formulas(query: str, domain: str = None) -> list[Formula]:
    """Search formulas by name, description, or tags."""
    query = query.lower()
    results = []
    for f in FORMULA_LIBRARY.values():
        if domain and f.domain != domain:
            continue
        if (query in f.name.lower() or query in f.description.lower() or
            any(query in t.lower() for t in (f.tags or []))):
            results.append(f)
    return results


def get_formulas_by_domain(domain: str) -> list[Formula]:
    """Get all formulas for a domain."""
    return [f for f in FORMULA_LIBRARY.values() if f.domain == domain]


def get_formulas_by_category(category: str) -> list[Formula]:
    """Get all formulas for a category."""
    return [f for f in FORMULA_LIBRARY.values() if f.category == category]


def list_domains() -> list[str]:
    """List all available formula domains."""
    return list(set(f.domain for f in FORMULA_LIBRARY.values()))


def list_categories() -> list[str]:
    """List all available formula categories."""
    return list(set(f.category for f in FORMULA_LIBRARY.values()))