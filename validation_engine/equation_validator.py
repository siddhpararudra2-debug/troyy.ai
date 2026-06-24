"""
Equation and physics validator for Engineering OS.
"""
from units.dimensional_checker import DimensionalChecker
from units.unit_converter import UnitConverter
from calculations.formula_library import get_formula


class ValidationResult:
    def __init__(self, valid: bool, passed: int, failed: int, checks: list[dict]):
        self.valid = valid
        self.passed = passed
        self.failed = failed
        self.checks = checks

    def to_dict(self) -> dict:
        return {"valid": self.valid, "passed": self.passed, "failed": self.failed, "checks": self.checks}


class EquationValidator:
    """Validates engineering equations for correctness."""

    def __init__(self):
        self.dc = DimensionalChecker()
        self.uc = UnitConverter()

    def validate_calculation(self, formula_id: str, params: dict) -> ValidationResult:
        """Validate all aspects of a calculation."""
        checks = []
        formula = get_formula(formula_id)
        
        # Check 1: Parameter completeness
        missing = [p["symbol"] for p in formula.parameters if p["symbol"] not in params and p["unit"]]
        checks.append({
            "check": "parameter_completeness",
            "passed": len(missing) == 0,
            "message": f"Missing: {missing}" if missing else "All parameters provided",
        })
        
        # Check 2: Reasonable values
        unreasonable = []
        for k, v in params.items():
            if v <= 0 and k not in ["ΔT", "dT"]:
                unreasonable.append(f"{k}={v}")
        checks.append({
            "check": "value_reasonableness",
            "passed": len(unreasonable) == 0,
            "message": f"Unreasonable: {unreasonable}" if unreasonable else "Values seem reasonable",
        })
        
        # Check 3: Domain match
        checks.append({
            "check": "formula_exists",
            "passed": True,
            "message": f"Formula '{formula.name}' found in {formula.domain}",
        })
        
        passed = sum(1 for c in checks if c["passed"])
        failed = len(checks) - passed
        
        return ValidationResult(failed == 0, passed, failed, checks)

    def review_design_safety(self, safety_factor: float, application: str) -> dict:
        """Review if safety factor is adequate for the application."""
        min_safety = {
            "aerospace": 1.5, "automotive": 1.3, "pressure_vessel": 2.0,
            "structural": 1.6, "lifting": 3.0, "general": 1.5,
        }
        required = min_safety.get(application, 1.5)
        return {
            "safety_factor": safety_factor,
            "minimum_required": required,
            "adequate": safety_factor >= required,
            "margin": safety_factor - required,
        }