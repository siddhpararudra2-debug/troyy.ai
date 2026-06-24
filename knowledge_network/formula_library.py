"""
Engineering Formula Library for Engineering OS.
Comprehensive collection of engineering formulas and standards.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime
import uuid


class EngineeringDomain(str, Enum):
    """Engineering domains."""
    MECHANICAL = "mechanical"
    AEROSPACE = "aerospace"
    ELECTRICAL = "electrical"
    THERMAL = "thermal"
    STRUCTURAL = "structural"
    FLUID_DYNAMICS = "fluid_dynamics"
    MATERIALS = "materials"


@dataclass
class FormulaParameter:
    """A parameter in a formula."""
    name: str = ""
    symbol: str = ""
    description: str = ""
    unit: str = ""
    typical_range: Optional[tuple] = None  # (min, max)
    standard_value: Optional[float] = None


@dataclass
class Formula:
    """An engineering formula."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    formula_id: str = ""
    domain: EngineeringDomain = EngineeringDomain.MECHANICAL
    
    # Basic information
    name: str = ""
    description: str = ""
    category: str = ""
    
    # Formula representation
    formula_latex: str = ""  # LaTeX representation
    formula_python: str = ""  # Python expression for calculation
    formula_text: str = ""  # Human-readable text
    
    # Parameters
    input_parameters: List[FormulaParameter] = field(default_factory=list)
    output_parameters: List[FormulaParameter] = field(default_factory=list)
    
    # Metadata
    source: str = ""  # Standard or reference
    applicability: str = ""  # When this formula applies
    limitations: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    valid_range: Dict[str, tuple] = field(default_factory=dict)  # Parameter ranges
    
    # Quality
    validated: bool = False
    validation_method: str = ""
    accuracy: float = 0.95  # 0-1
    reference: str = ""
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_verified: Optional[datetime] = None


class MechanicalFormulas:
    """Mechanical engineering formulas."""

    @staticmethod
    def stress_formula() -> Formula:
        """Simple tensile stress formula: σ = F/A"""
        return Formula(
            formula_id="MECH-001",
            domain=EngineeringDomain.MECHANICAL,
            name="Tensile Stress",
            description="Stress under tensile loading",
            category="Stress Analysis",
            formula_latex=r"\sigma = \frac{F}{A}",
            formula_python="F / A",
            formula_text="Stress equals force divided by area",
            input_parameters=[
                FormulaParameter(
                    name="Force",
                    symbol="F",
                    description="Applied tensile force",
                    unit="N",
                    typical_range=(0, 1e6)
                ),
                FormulaParameter(
                    name="Cross-sectional Area",
                    symbol="A",
                    description="Cross-sectional area perpendicular to force",
                    unit="m^2",
                    typical_range=(0, 1.0)
                )
            ],
            output_parameters=[
                FormulaParameter(
                    name="Stress",
                    symbol="σ",
                    description="Normal stress",
                    unit="Pa"
                )
            ],
            source="Mechanics of Materials - Basic Principle",
            assumptions=["Uniform stress distribution", "Linear elastic material"],
            limitations=["Only valid for elastic range", "Assumes uniform cross-section"],
            valid_range={"F": (0, 1e7), "A": (1e-6, 10)},
            validated=True,
            accuracy=0.99
        )

    @staticmethod
    def strain_formula() -> Formula:
        """Engineering strain formula: ε = ΔL/L₀"""
        return Formula(
            formula_id="MECH-002",
            domain=EngineeringDomain.MECHANICAL,
            name="Engineering Strain",
            description="Strain under axial loading",
            category="Strain Analysis",
            formula_latex=r"\varepsilon = \frac{\Delta L}{L_0}",
            formula_python="delta_L / L0",
            formula_text="Strain equals change in length divided by original length",
            input_parameters=[
                FormulaParameter(
                    name="Change in Length",
                    symbol="ΔL",
                    description="Deformation",
                    unit="m",
                    typical_range=(-1.0, 1.0)
                ),
                FormulaParameter(
                    name="Original Length",
                    symbol="L₀",
                    description="Initial length",
                    unit="m",
                    typical_range=(0.001, 100)
                )
            ],
            output_parameters=[
                FormulaParameter(
                    name="Strain",
                    symbol="ε",
                    description="Dimensionless strain",
                    unit="dimensionless"
                )
            ],
            source="Mechanics of Materials",
            assumptions=["Small strain assumption"],
            limitations=["Not valid for large deformations"],
            valid_range={"delta_L": (-1, 1), "L0": (0.001, 100)},
            validated=True,
            accuracy=0.99
        )

    @staticmethod
    def youngs_modulus_formula() -> Formula:
        """Young's modulus: E = σ/ε"""
        return Formula(
            formula_id="MECH-003",
            domain=EngineeringDomain.MECHANICAL,
            name="Young's Modulus",
            description="Elastic modulus relating stress and strain",
            category="Material Properties",
            formula_latex=r"E = \frac{\sigma}{\varepsilon}",
            formula_python="sigma / epsilon",
            formula_text="Young's modulus equals stress divided by strain",
            input_parameters=[
                FormulaParameter(
                    name="Stress",
                    symbol="σ",
                    description="Applied stress",
                    unit="Pa",
                    typical_range=(0, 1e9)
                ),
                FormulaParameter(
                    name="Strain",
                    symbol="ε",
                    description="Resulting strain",
                    unit="dimensionless",
                    typical_range=(0, 0.01)
                )
            ],
            output_parameters=[
                FormulaParameter(
                    name="Young's Modulus",
                    symbol="E",
                    description="Elastic modulus",
                    unit="Pa"
                )
            ],
            source="Hooke's Law",
            assumptions=["Linear elastic behavior", "Isotropic material"],
            valid_range={"sigma": (0, 1e9), "epsilon": (0, 0.01)},
            validated=True,
            accuracy=0.98
        )

    @staticmethod
    def beam_deflection_formula() -> Formula:
        """Cantilever beam deflection: δ = PL³/(3EI)"""
        return Formula(
            formula_id="MECH-004",
            domain=EngineeringDomain.MECHANICAL,
            name="Cantilever Beam Deflection",
            description="Maximum deflection of cantilever beam",
            category="Structural Analysis",
            formula_latex=r"\delta = \frac{PL^3}{3EI}",
            formula_python="(P * L**3) / (3 * E * I)",
            formula_text="Deflection equals PL³ divided by 3EI",
            input_parameters=[
                FormulaParameter(
                    name="Point Load",
                    symbol="P",
                    description="Applied load at free end",
                    unit="N",
                    typical_range=(0, 1e5)
                ),
                FormulaParameter(
                    name="Length",
                    symbol="L",
                    description="Beam length",
                    unit="m",
                    typical_range=(0.1, 10)
                ),
                FormulaParameter(
                    name="Young's Modulus",
                    symbol="E",
                    description="Material elastic modulus",
                    unit="Pa",
                    typical_range=(1e10, 1e12)
                ),
                FormulaParameter(
                    name="Moment of Inertia",
                    symbol="I",
                    description="Second moment of area",
                    unit="m^4",
                    typical_range=(1e-8, 1e-3)
                )
            ],
            output_parameters=[
                FormulaParameter(
                    name="Deflection",
                    symbol="δ",
                    description="Maximum deflection",
                    unit="m"
                )
            ],
            source="Mechanics of Materials Textbook",
            assumptions=["Small deflection", "Linear elastic", "Uniform cross-section"],
            valid_range={"P": (0, 1e6), "L": (0.1, 100), "E": (1e10, 1e12), "I": (1e-10, 1e-2)},
            validated=True,
            accuracy=0.97
        )


class AerospaceFormulas:
    """Aerospace engineering formulas."""

    @staticmethod
    def lift_formula() -> Formula:
        """Lift force: L = 0.5 * ρ * V² * S * Cl"""
        return Formula(
            formula_id="AERO-001",
            domain=EngineeringDomain.AEROSPACE,
            name="Aerodynamic Lift",
            description="Lift force on an airfoil",
            category="Aerodynamics",
            formula_latex=r"L = \frac{1}{2} \rho V^2 S C_L",
            formula_python="0.5 * rho * V**2 * S * Cl",
            formula_text="Lift equals half density times velocity squared times wing area times lift coefficient",
            input_parameters=[
                FormulaParameter(
                    name="Air Density",
                    symbol="ρ",
                    description="Density of air",
                    unit="kg/m^3",
                    standard_value=1.225,
                    typical_range=(0.4, 1.5)
                ),
                FormulaParameter(
                    name="Velocity",
                    symbol="V",
                    description="Airflow velocity",
                    unit="m/s",
                    typical_range=(10, 300)
                ),
                FormulaParameter(
                    name="Wing Area",
                    symbol="S",
                    description="Planform area of wing",
                    unit="m^2",
                    typical_range=(1, 1000)
                ),
                FormulaParameter(
                    name="Lift Coefficient",
                    symbol="Cl",
                    description="Dimensionless lift coefficient",
                    unit="dimensionless",
                    typical_range=(0.2, 2.0)
                )
            ],
            output_parameters=[
                FormulaParameter(
                    name="Lift Force",
                    symbol="L",
                    description="Total lift force",
                    unit="N"
                )
            ],
            source="Aerodynamics - Fundamentals",
            assumptions=["Incompressible flow", "Steady state"],
            limitations=["Not valid at transonic/supersonic speeds"],
            valid_range={"rho": (0.3, 2.0), "V": (5, 500), "S": (0.1, 5000), "Cl": (0.0, 3.0)},
            validated=True,
            accuracy=0.95
        )

    @staticmethod
    def drag_formula() -> Formula:
        """Drag force: D = 0.5 * ρ * V² * S * Cd"""
        return Formula(
            formula_id="AERO-002",
            domain=EngineeringDomain.AEROSPACE,
            name="Aerodynamic Drag",
            description="Drag force on an airfoil",
            category="Aerodynamics",
            formula_latex=r"D = \frac{1}{2} \rho V^2 S C_D",
            formula_python="0.5 * rho * V**2 * S * Cd",
            input_parameters=[
                FormulaParameter(
                    name="Air Density",
                    symbol="ρ",
                    description="Density of air",
                    unit="kg/m^3",
                    standard_value=1.225
                ),
                FormulaParameter(
                    name="Velocity",
                    symbol="V",
                    description="Airflow velocity",
                    unit="m/s",
                    typical_range=(10, 300)
                ),
                FormulaParameter(
                    name="Wing Area",
                    symbol="S",
                    description="Reference area",
                    unit="m^2",
                    typical_range=(1, 1000)
                ),
                FormulaParameter(
                    name="Drag Coefficient",
                    symbol="Cd",
                    description="Dimensionless drag coefficient",
                    unit="dimensionless",
                    typical_range=(0.01, 2.0)
                )
            ],
            output_parameters=[
                FormulaParameter(
                    name="Drag Force",
                    symbol="D",
                    description="Total drag force",
                    unit="N"
                )
            ],
            source="Aerodynamics - Fundamentals",
            assumptions=["Incompressible flow", "Steady state"],
            valid_range={"rho": (0.3, 2.0), "V": (5, 500), "S": (0.1, 5000), "Cd": (0.0, 3.0)},
            validated=True,
            accuracy=0.94
        )


class ThermalFormulas:
    """Thermal engineering formulas."""

    @staticmethod
    def heat_transfer_conduction() -> Formula:
        """Fourier's Law: Q = -k * A * (dT/dx)"""
        return Formula(
            formula_id="THERM-001",
            domain=EngineeringDomain.THERMAL,
            name="Heat Conduction",
            description="Steady-state heat conduction",
            category="Heat Transfer",
            formula_latex=r"Q = -k A \frac{dT}{dx}",
            formula_python="k * A * dT / dx",
            input_parameters=[
                FormulaParameter(
                    name="Thermal Conductivity",
                    symbol="k",
                    description="Material thermal conductivity",
                    unit="W/(m·K)",
                    typical_range=(0.01, 1000)
                ),
                FormulaParameter(
                    name="Area",
                    symbol="A",
                    description="Cross-sectional area",
                    unit="m^2",
                    typical_range=(0.001, 100)
                ),
                FormulaParameter(
                    name="Temperature Gradient",
                    symbol="dT/dx",
                    description="Temperature gradient",
                    unit="K/m",
                    typical_range=(0, 1000)
                )
            ],
            output_parameters=[
                FormulaParameter(
                    name="Heat Transfer Rate",
                    symbol="Q",
                    description="Rate of heat transfer",
                    unit="W"
                )
            ],
            source="Heat Transfer - Fundamentals",
            assumptions=["Steady state", "Constant properties"],
            validated=True,
            accuracy=0.96
        )


class EngineeringFormulaLibrary:
    """Complete engineering formula library."""

    def __init__(self):
        self.formulas: Dict[str, Formula] = {}
        self._initialize_library()

    def _initialize_library(self):
        """Initialize with standard formulas."""
        # Mechanical
        self.formulas["MECH-001"] = MechanicalFormulas.stress_formula()
        self.formulas["MECH-002"] = MechanicalFormulas.strain_formula()
        self.formulas["MECH-003"] = MechanicalFormulas.youngs_modulus_formula()
        self.formulas["MECH-004"] = MechanicalFormulas.beam_deflection_formula()
        
        # Aerospace
        self.formulas["AERO-001"] = AerospaceFormulas.lift_formula()
        self.formulas["AERO-002"] = AerospaceFormulas.drag_formula()
        
        # Thermal
        self.formulas["THERM-001"] = ThermalFormulas.heat_transfer_conduction()

    def get_formula(self, formula_id: str) -> Optional[Formula]:
        """Get a formula by ID."""
        return self.formulas.get(formula_id)

    def search_formulas(self, domain: EngineeringDomain = None, category: str = None) -> List[Formula]:
        """Search formulas by domain or category."""
        results = []
        for formula in self.formulas.values():
            if domain and formula.domain != domain:
                continue
            if category and formula.category != category:
                continue
            results.append(formula)
        return results

    def get_formulas_by_domain(self, domain: EngineeringDomain) -> List[Formula]:
        """Get all formulas for a domain."""
        return [f for f in self.formulas.values() if f.domain == domain]

    async def validate_formula_applicability(
        self,
        formula_id: str,
        parameters: Dict[str, float]
    ) -> Dict[str, Any]:
        """Validate if a formula can be applied to given parameters."""
        formula = self.get_formula(formula_id)
        if not formula:
            return {"valid": False, "error": "Formula not found"}
        
        issues = []
        
        for param_name, param_value in parameters.items():
            param_def = None
            for p in formula.input_parameters:
                if p.symbol == param_name or p.name.lower() == param_name.lower():
                    param_def = p
                    break
            
            if param_def and param_def.typical_range:
                min_val, max_val = param_def.typical_range
                if param_value < min_val or param_value > max_val:
                    issues.append(
                        f"{param_name} = {param_value} outside typical range [{min_val}, {max_val}]"
                    )
        
        return {
            "valid": len(issues) == 0,
            "formula_id": formula_id,
            "formula_name": formula.name,
            "applicability_issues": issues,
            "assumptions": formula.assumptions,
            "limitations": formula.limitations
        }
