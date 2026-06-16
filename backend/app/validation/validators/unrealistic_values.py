"""
Troy — Unrealistic Values Validator
Detects physically improbable values.
"""
from typing import List
from app.solver.models import SolverState
from app.validation.models import ValidationIssue
from app.validation.validators.base import AsyncBaseValidator

class UnrealisticValuesValidator(AsyncBaseValidator):
    name = "UnrealisticValuesValidator"
    
    async def validate(self, state: SolverState) -> List[ValidationIssue]:
        issues = []
        
        # Check known variables
        for var_name, var_data in state.variables.known.items():
            val = var_data.get("value")
            if isinstance(val, (int, float)) and val <= 0:
                issues.append(ValidationIssue(
                    severity="error",
                    category="Values",
                    message=f"Variable {var_name} has non-positive value: {val}",
                    validator_name=self.name
                ))
                
        # Check derived variables
        for var_name, var_data in state.variables.derived.items():
            val = var_data.get("value")
            if isinstance(val, (int, float)) and val <= 0:
                issues.append(ValidationIssue(
                    severity="error",
                    category="Values",
                    message=f"Derived variable {var_name} resulted in non-positive value: {val}",
                    validator_name=self.name
                ))

        # Check calculation results
        for res_name, res_val in state.calculation_results.items():
            if isinstance(res_val, (int, float)) and res_val < 0:
                 issues.append(ValidationIssue(
                    severity="error",
                    category="Values",
                    message=f"Calculation result {res_name} is negative: {res_val}",
                    validator_name=self.name
                ))
                
        return issues
