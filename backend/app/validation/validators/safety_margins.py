"""
Troy — Safety Margin Validator
Verifies if safety margins meet domain standards.
"""
from typing import List
from app.solver.models import SolverState
from app.validation.models import ValidationIssue
from app.validation.validators.base import AsyncBaseValidator

class SafetyMarginValidator(AsyncBaseValidator):
    name = "SafetyMarginValidator"
    
    async def validate(self, state: SolverState) -> List[ValidationIssue]:
        issues = []
        
        # Extract safety factor from known variables
        safety_factor = state.variables.known.get("n_safety", {}).get("value")
        
        if safety_factor is not None:
            if state.domain == "aerospace" and safety_factor < 1.5:
                issues.append(ValidationIssue(
                    severity="error",
                    category="Safety",
                    message=f"Safety factor {safety_factor} is below aerospace minimum standard (1.5).",
                    validator_name=self.name
                ))
            elif state.domain == "drones" and safety_factor < 1.2:
                issues.append(ValidationIssue(
                    severity="warning",
                    category="Safety",
                    message=f"Safety factor {safety_factor} is low for UAVs, reducing maneuverability margin.",
                    validator_name=self.name
                ))
                
        return issues
