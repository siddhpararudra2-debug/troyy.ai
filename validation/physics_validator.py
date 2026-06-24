"""
Physics Validation Engine for Engineering OS.
Validates physics principles and laws.
"""
from dataclasses import dataclass
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum
from datetime import datetime


class PhysicsDomain(str, Enum):
    """Physics domains for validation."""
    MECHANICS = "mechanics"
    THERMODYNAMICS = "thermodynamics"
    FLUID_DYNAMICS = "fluid_dynamics"
    ELECTROMAGNETISM = "electromagnetism"
    MATERIALS = "materials"
    AERODYNAMICS = "aerodynamics"


@dataclass
class PhysicsValidationError:
    """Physics validation error."""
    rule: str
    message: str
    severity: str  # "error", "warning"
    affected_parameters: List[str]
    suggested_correction: Optional[str] = None


@dataclass
class PhysicsValidationResult:
    """Result of physics validation."""
    domain: PhysicsDomain
    is_valid: bool
    errors: List[PhysicsValidationError]
    warnings: List[PhysicsValidationError]
    validated_laws: List[str]
    metadata: Dict[str, Any]


class PhysicsValidator:
    """Validates engineering physics principles."""

    def __init__(self):
        self.physics_rules = self._initialize_rules()

    def _initialize_rules(self) -> Dict[PhysicsDomain, List[Dict]]:
        """Initialize physics validation rules."""
        return {
            PhysicsDomain.MECHANICS: [
                {
                    "name": "Newton's First Law",
                    "description": "Force equals mass times acceleration (F=ma)",
                    "check": self._check_newtons_laws
                },
                {
                    "name": "Energy Conservation",
                    "description": "Total mechanical energy is conserved",
                    "check": self._check_energy_conservation
                },
                {
                    "name": "Stress-Strain Relationship",
                    "description": "Stress proportional to strain (Hooke's Law)",
                    "check": self._check_hookes_law
                },
                {
                    "name": "Fatigue Limits",
                    "description": "Fatigue strength less than ultimate strength",
                    "check": self._check_fatigue_limits
                }
            ],
            PhysicsDomain.THERMODYNAMICS: [
                {
                    "name": "First Law",
                    "description": "Energy conservation in thermodynamic systems",
                    "check": self._check_first_law_thermo
                },
                {
                    "name": "Second Law",
                    "description": "Entropy increase in isolated systems",
                    "check": self._check_second_law_thermo
                },
                {
                    "name": "Absolute Zero",
                    "description": "Temperature must be ≥ 0K",
                    "check": self._check_absolute_zero
                }
            ],
            PhysicsDomain.FLUID_DYNAMICS: [
                {
                    "name": "Continuity Equation",
                    "description": "Mass conservation in flow",
                    "check": self._check_continuity
                },
                {
                    "name": "Bernoulli Equation",
                    "description": "Energy conservation in incompressible flow",
                    "check": self._check_bernoulli
                },
                {
                    "name": "Positive Pressure",
                    "description": "Gauge pressure ≥ -atmospheric pressure",
                    "check": self._check_positive_pressure
                }
            ],
            PhysicsDomain.ELECTROMAGNETISM: [
                {
                    "name": "Ohm's Law",
                    "description": "Voltage = Current × Resistance",
                    "check": self._check_ohms_law
                },
                {
                    "name": "Power Dissipation",
                    "description": "Power dissipation is positive",
                    "check": self._check_power_dissipation
                }
            ],
            PhysicsDomain.AERODYNAMICS: [
                {
                    "name": "Lift Coefficient",
                    "description": "Lift coefficient typically 0.2 to 2.0",
                    "check": self._check_lift_coefficient
                },
                {
                    "name": "Drag Coefficient",
                    "description": "Drag coefficient typically 0.01 to 2.0",
                    "check": self._check_drag_coefficient
                }
            ]
        }

    async def validate_physics(
        self,
        domain: PhysicsDomain,
        parameters: Dict[str, float],
        formula: Optional[str] = None
    ) -> PhysicsValidationResult:
        """Validate physics for a given domain."""
        errors = []
        warnings = []
        validated_laws = []

        rules = self.physics_rules.get(domain, [])

        for rule in rules:
            try:
                is_valid, issues = await rule["check"](parameters, formula)
                if is_valid:
                    validated_laws.append(rule["name"])
                else:
                    errors.extend(issues)
            except Exception as e:
                warnings.append(PhysicsValidationError(
                    rule=rule["name"],
                    message=f"Could not validate: {str(e)}",
                    severity="warning",
                    affected_parameters=list(parameters.keys())
                ))

        return PhysicsValidationResult(
            domain=domain,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validated_laws=validated_laws,
            metadata={
                "parameters": parameters,
                "formula": formula,
                "validation_count": len(rules)
            }
        )

    async def _check_newtons_laws(self, params: Dict, formula: Optional[str]) -> Tuple[bool, List]:
        """Check Newton's laws (F=ma)."""
        issues = []
        
        # Check for negative mass
        if "mass" in params and params["mass"] <= 0:
            issues.append(PhysicsValidationError(
                rule="Newton's First Law",
                message="Mass must be positive",
                severity="error",
                affected_parameters=["mass"],
                suggested_correction="Ensure mass > 0"
            ))
        
        # Check for impossible accelerations (> speed of light)
        c = 3e8  # speed of light
        if "acceleration" in params and abs(params["acceleration"]) > 1e17:  # a = c^2 / 1m
            issues.append(PhysicsValidationError(
                rule="Newton's First Law",
                message="Acceleration exceeds relativistic limits",
                severity="warning",
                affected_parameters=["acceleration"]
            ))
        
        return len(issues) == 0, issues

    async def _check_energy_conservation(self, params: Dict, formula: Optional[str]) -> Tuple[bool, List]:
        """Check energy conservation."""
        issues = []
        
        if "energy_initial" in params and "energy_final" in params:
            if params["energy_final"] > params["energy_initial"]:
                issues.append(PhysicsValidationError(
                    rule="Energy Conservation",
                    message="Final energy exceeds initial energy (violation of conservation)",
                    severity="warning",
                    affected_parameters=["energy_initial", "energy_final"]
                ))
        
        return len(issues) == 0, issues

    async def _check_hookes_law(self, params: Dict, formula: Optional[str]) -> Tuple[bool, List]:
        """Check Hooke's Law (stress-strain relationship)."""
        issues = []
        
        # Young's modulus must be positive
        if "youngs_modulus" in params and params["youngs_modulus"] <= 0:
            issues.append(PhysicsValidationError(
                rule="Hooke's Law",
                message="Young's modulus must be positive",
                severity="error",
                affected_parameters=["youngs_modulus"]
            ))
        
        # Strain should typically be < 0.1 (10%) for elastic region
        if "strain" in params and abs(params["strain"]) > 0.1:
            issues.append(PhysicsValidationError(
                rule="Hooke's Law",
                message="Strain exceeds typical elastic limit (10%)",
                severity="warning",
                affected_parameters=["strain"]
            ))
        
        return len(issues) == 0, issues

    async def _check_fatigue_limits(self, params: Dict, formula: Optional[str]) -> Tuple[bool, List]:
        """Check fatigue strength limits."""
        issues = []
        
        if "fatigue_strength" in params and "ultimate_strength" in params:
            if params["fatigue_strength"] > params["ultimate_strength"]:
                issues.append(PhysicsValidationError(
                    rule="Fatigue Limits",
                    message="Fatigue strength cannot exceed ultimate strength",
                    severity="error",
                    affected_parameters=["fatigue_strength", "ultimate_strength"],
                    suggested_correction="Ensure fatigue_strength < ultimate_strength"
                ))
        
        return len(issues) == 0, issues

    async def _check_first_law_thermo(self, params: Dict, formula: Optional[str]) -> Tuple[bool, List]:
        """Check First Law of Thermodynamics."""
        issues = []
        
        # ΔU = Q - W (change in internal energy)
        if all(k in params for k in ["internal_energy_change", "heat", "work"]):
            calculated = params["heat"] - params["work"]
            if abs(calculated - params["internal_energy_change"]) > 0.01 * abs(params["heat"]):
                issues.append(PhysicsValidationError(
                    rule="First Law",
                    message="Energy balance violation (ΔU ≠ Q - W)",
                    severity="warning",
                    affected_parameters=["internal_energy_change", "heat", "work"]
                ))
        
        return len(issues) == 0, issues

    async def _check_second_law_thermo(self, params: Dict, formula: Optional[str]) -> Tuple[bool, List]:
        """Check Second Law of Thermodynamics."""
        issues = []
        
        if "entropy_change" in params and params["entropy_change"] < 0:
            issues.append(PhysicsValidationError(
                rule="Second Law",
                message="Entropy decrease in isolated system (violates 2nd Law)",
                severity="error",
                affected_parameters=["entropy_change"],
                suggested_correction="Ensure ΔS ≥ 0 for isolated systems"
            ))
        
        return len(issues) == 0, issues

    async def _check_absolute_zero(self, params: Dict, formula: Optional[str]) -> Tuple[bool, List]:
        """Check absolute zero constraint."""
        issues = []
        
        absolute_zero_k = 0  # Kelvin
        for key in ["temperature", "temp", "T"]:
            if key in params and params[key] < absolute_zero_k:
                issues.append(PhysicsValidationError(
                    rule="Absolute Zero",
                    message=f"Temperature ({params[key]}K) below absolute zero",
                    severity="error",
                    affected_parameters=[key],
                    suggested_correction="Temperature must be ≥ 0K"
                ))
        
        return len(issues) == 0, issues

    async def _check_continuity(self, params: Dict, formula: Optional[str]) -> Tuple[bool, List]:
        """Check continuity equation (mass conservation)."""
        issues = []
        
        # ρ₁A₁V₁ = ρ₂A₂V₂
        required = ["density1", "area1", "velocity1", "density2", "area2", "velocity2"]
        if all(k in params for k in required):
            lhs = params["density1"] * params["area1"] * params["velocity1"]
            rhs = params["density2"] * params["area2"] * params["velocity2"]
            if abs(lhs - rhs) > 0.01 * max(abs(lhs), abs(rhs)):
                issues.append(PhysicsValidationError(
                    rule="Continuity Equation",
                    message="Mass flow rate not conserved",
                    severity="warning",
                    affected_parameters=required
                ))
        
        return len(issues) == 0, issues

    async def _check_bernoulli(self, params: Dict, formula: Optional[str]) -> Tuple[bool, List]:
        """Check Bernoulli equation."""
        issues = []
        
        # P + ½ρV² + ρgh = constant
        # Implementation would check if the sum is constant between points
        
        return len(issues) == 0, issues

    async def _check_positive_pressure(self, params: Dict, formula: Optional[str]) -> Tuple[bool, List]:
        """Check pressure is above absolute vacuum."""
        issues = []
        
        if "pressure" in params and params["pressure"] < -101325:  # Pa (absolute vacuum)
            issues.append(PhysicsValidationError(
                rule="Positive Pressure",
                message="Gauge pressure below absolute vacuum",
                severity="error",
                affected_parameters=["pressure"],
                suggested_correction="Ensure pressure ≥ -101325 Pa"
            ))
        
        return len(issues) == 0, issues

    async def _check_ohms_law(self, params: Dict, formula: Optional[str]) -> Tuple[bool, List]:
        """Check Ohm's Law (V = IR)."""
        issues = []
        
        if all(k in params for k in ["voltage", "current", "resistance"]):
            calculated = params["current"] * params["resistance"]
            if abs(calculated - params["voltage"]) > 0.01 * abs(params["voltage"]):
                issues.append(PhysicsValidationError(
                    rule="Ohm's Law",
                    message="Voltage does not equal current × resistance",
                    severity="warning",
                    affected_parameters=["voltage", "current", "resistance"]
                ))
        
        return len(issues) == 0, issues

    async def _check_power_dissipation(self, params: Dict, formula: Optional[str]) -> Tuple[bool, List]:
        """Check power dissipation is positive."""
        issues = []
        
        if "power" in params and params["power"] < 0:
            issues.append(PhysicsValidationError(
                rule="Power Dissipation",
                message="Power cannot be negative",
                severity="warning",
                affected_parameters=["power"],
                suggested_correction="Ensure power ≥ 0"
            ))
        
        return len(issues) == 0, issues

    async def _check_lift_coefficient(self, params: Dict, formula: Optional[str]) -> Tuple[bool, List]:
        """Check aerodynamic lift coefficient."""
        issues = []
        
        if "lift_coefficient" in params:
            cl = params["lift_coefficient"]
            if cl < 0.2 or cl > 2.0:
                issues.append(PhysicsValidationError(
                    rule="Lift Coefficient",
                    message=f"Lift coefficient {cl} outside typical range [0.2, 2.0]",
                    severity="warning",
                    affected_parameters=["lift_coefficient"]
                ))
        
        return len(issues) == 0, issues

    async def _check_drag_coefficient(self, params: Dict, formula: Optional[str]) -> Tuple[bool, List]:
        """Check aerodynamic drag coefficient."""
        issues = []
        
        if "drag_coefficient" in params:
            cd = params["drag_coefficient"]
            if cd < 0.01 or cd > 2.0:
                issues.append(PhysicsValidationError(
                    rule="Drag Coefficient",
                    message=f"Drag coefficient {cd} outside typical range [0.01, 2.0]",
                    severity="warning",
                    affected_parameters=["drag_coefficient"]
                ))
        
        return len(issues) == 0, issues
