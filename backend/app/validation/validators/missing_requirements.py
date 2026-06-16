"""
Troy — Missing Requirements Validator
Checks if crucial mission parameters are missing.
"""
from typing import List
from app.solver.models import SolverState
from app.validation.models import ValidationIssue
from app.validation.validators.base import AsyncBaseValidator

class MissingRequirementsValidator(AsyncBaseValidator):
    name = "MissingRequirementsValidator"
    
    async def validate(self, state: SolverState) -> List[ValidationIssue]:
        issues = []
        reqs = state.requirements
        
        # Check if the extracted unknown requirements list has items
        if reqs.unknown_requirements:
            for missing in reqs.unknown_requirements:
                issues.append(ValidationIssue(
                    severity="error",
                    category="Requirements",
                    message=f"Missing critical requirement: {missing}",
                    validator_name=self.name
                ))
                
        # Domain specific checks
        if state.domain == "drones" and not reqs.payload:
            issues.append(ValidationIssue(
                severity="warning",
                category="Requirements",
                message="Drone payload was not explicitly provided. Assumed 0.5kg.",
                validator_name=self.name
            ))
            
        return issues
