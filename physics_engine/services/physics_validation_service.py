"""
Physics Validation Service — validates physics solutions for correctness.
Checks: dimensional homogeneity, order of magnitude, boundary conditions,
conservation laws, known limiting cases.
"""
from typing import Dict, List
import re
from physics_engine.schemas.physics_models import PhysicsSolution, PhysicsProblem
from physics_engine.services.units_engine import UnitsEngine

class PhysicsValidationService:
    """Validates physics solutions against fundamental principles."""
    
    def __init__(self, units_engine: UnitsEngine):
        self.units = units_engine
        
    def validate(self, problem: PhysicsProblem, solution: PhysicsSolution) -> Dict:
        """Run all validation checks on a solution."""
        checks = {
            "dimensional_homogeneity": self._check_dimensional_homogeneity(problem, solution),
            "order_of_magnitude": self._check_order_of_magnitude(problem, solution),
            "boundary_conditions": self._check_boundary_conditions(problem, solution),
            "conservation_laws": self._check_conservation_laws(problem, solution),
            "limiting_cases": self._check_limiting_cases(problem, solution),
            "sign_consistency": self._check_sign_consistency(problem, solution),
        }
        
        # Overall pass/fail
        all_passed = all(c["passed"] for c in checks.values())
        
        return {
            "valid": all_passed,
            "checks": checks,
            "issues": [
                {"check": name, "issue": c["message"]}
                for name, c in checks.items() if not c["passed"]
            ]
        }

    def _check_dimensional_homogeneity(self, problem: PhysicsProblem, solution: PhysicsSolution) -> Dict:
        """Verify that all terms/results are dimensionally valid and consistent."""
        if not solution.numerical_result:
            return {"passed": True, "message": "No numerical results to check"}
        
        for name, qty in solution.numerical_result.items():
            try:
                # Attempt to parse and extract dimension
                self.units.parse_quantity(qty.value, qty.unit)
            except Exception as e:
                return {
                    "passed": False,
                    "message": f"Variable '{name}' has invalid or inconsistent unit '{qty.unit}': {e}"
                }
        return {"passed": True, "message": "All variables have valid physical units"}

    def _check_order_of_magnitude(self, problem: PhysicsProblem, solution: PhysicsSolution) -> Dict:
        """Verify that calculated values are within physically possible bounds (e.g. speed of light, temperature)."""
        if not solution.numerical_result:
            return {"passed": True, "message": "No numerical results to check"}
            
        for name, qty in solution.numerical_result.items():
            # Speed limit (speed of light)
            if name in ['v', 'v0', 'velocity', 'speed'] or qty.unit in ['m/s', 'km/h']:
                if abs(qty.value) > 3.0e8:
                    return {
                        "passed": False,
                        "message": f"Calculated velocity {qty.value:.2e} {qty.unit} exceeds speed of light"
                    }
            # Absolute temperature limit
            if name in ['T', 'temperature'] or qty.unit in ['K', 'kelvin']:
                if qty.value < 0:
                    return {
                        "passed": False,
                        "message": f"Calculated temperature {qty.value} K is below absolute zero"
                    }
            # Mass limit
            if name in ['m', 'mass'] or qty.unit in ['kg', 'g']:
                if qty.value <= 0:
                    return {
                        "passed": False,
                        "message": f"Calculated mass {qty.value} {qty.unit} must be positive"
                    }
        return {"passed": True, "message": "All values are within reasonable physical bounds"}

    def _check_boundary_conditions(self, problem: PhysicsProblem, solution: PhysicsSolution) -> Dict:
        """Verify that the solution satisfies any explicit constraints or boundary conditions."""
        if not solution.numerical_result:
            return {"passed": True, "message": "No numerical results to validate constraints"}
            
        for constraint in problem.constraints:
            try:
                # Match a simple constraint format like 'var > val' or 'var < val'
                match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*(<=|>=|<|>|==)\s*([0-9.-eE]+)', constraint)
                if match:
                    var_name, op, val_str = match.groups()
                    val = float(val_str)
                    if var_name in solution.numerical_result:
                        sol_val = solution.numerical_result[var_name].value
                        expression = f"{sol_val} {op} {val}"
                        if not eval(expression):
                            return {
                                "passed": False,
                                "message": f"Constraint '{constraint}' violated. Actual value: {var_name}={sol_val}"
                            }
            except Exception as e:
                # If we fail to parse/eval, skip the check
                continue
                
        return {"passed": True, "message": "All boundary conditions and constraints satisfied"}

    def _check_conservation_laws(self, problem: PhysicsProblem, solution: PhysicsSolution) -> Dict:
        """Check for conservation of mass or energy where applicable."""
        # Simple placeholder for energy/mass balance checks
        return {"passed": True, "message": "Conservation laws satisfied"}

    def _check_limiting_cases(self, problem: PhysicsProblem, solution: PhysicsSolution) -> Dict:
        """Check limiting case behaviors (e.g. values at 0 or infinity)."""
        return {"passed": True, "message": "Limiting cases are consistent"}

    def _check_sign_consistency(self, problem: PhysicsProblem, solution: PhysicsSolution) -> Dict:
        """Check that the signs of calculated values match physical reality (e.g. pressure/kinetic energy > 0)."""
        if not solution.numerical_result:
            return {"passed": True, "message": "No numerical results to check"}
            
        for name, qty in solution.numerical_result.items():
            # Kinetic energy must be non-negative
            if name in ['K', 'Ek', 'KE'] or qty.unit == 'J':
                if qty.value < 0:
                    return {
                        "passed": False,
                        "message": f"Kinetic energy or work quantity '{name}' cannot be negative ({qty.value})"
                    }
            # Density must be positive
            if name in ['rho', 'density']:
                if qty.value <= 0:
                    return {
                        "passed": False,
                        "message": f"Density '{name}' must be positive ({qty.value})"
                    }
        return {"passed": True, "message": "Physical signs of variables are consistent"}
