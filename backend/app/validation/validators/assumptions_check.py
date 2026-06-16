"""
Troy — Dangerous Assumptions Validator
Flags potentially dangerous assumptions.
"""
from typing import List
from app.solver.models import SolverState
from app.validation.models import ValidationIssue
from app.validation.validators.base import AsyncBaseValidator

class DangerousAssumptionsValidator(AsyncBaseValidator):
    name = "DangerousAssumptionsValidator"
    
    async def validate(self, state: SolverState) -> List[ValidationIssue]:
        issues = []
        
        for assumption in state.assumptions:
            if "calm weather" in assumption.assumption.lower() and state.domain in ["drones", "aerospace"]:
                issues.append(ValidationIssue(
                    severity="warning",
                    category="Assumptions",
                    message="Assuming calm weather is risky for outdoor aerial vehicles. Consider adding a wind tolerance margin.",
                    validator_name=self.name
                ))
                
        return issues
