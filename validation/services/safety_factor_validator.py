from typing import Dict, Any, List
from validation.services.base_validator import BaseValidator
from validation.schemas.validation import ValidationIssueSchema, Severity

class SafetyFactorValidator(BaseValidator):
    MIN_SF = {
        "AEROSPACE": 1.5,
        "UAV": 1.25,
        "ROBOTICS": 2.0,
        "ELECTRONICS": 1.5
    }

    async def validate(self, data: Dict[str, Any]) -> List[ValidationIssueSchema]:
        issues = []
        domain = data.get("domain", "AEROSPACE").upper()
        min_sf = self.MIN_SF.get(domain, 1.5)
        
        design_data = data.get("design_data", {})
        applied_sf = design_data.get("safety_factor")
        
        if applied_sf is None:
            issues.append(ValidationIssueSchema(
                module="SAFETY_FACTOR_VALIDATOR",
                severity=Severity.CRITICAL,
                description="No safety factor defined in design data.",
                engineering_reasoning="Engineering designs without explicit safety margins are unacceptable for flight or human interaction.",
                recommendation=f"Define a safety factor of at least {min_sf} for {domain} applications."
            ))
        elif applied_sf < min_sf:
            issues.append(ValidationIssueSchema(
                module="SAFETY_FACTOR_VALIDATOR",
                severity=Severity.HIGH,
                description=f"Safety factor {applied_sf} is below the {domain} minimum of {min_sf}.",
                engineering_reasoning="Insufficient margin for material defects, manufacturing tolerances, and unexpected load cases.",
                recommendation=f"Increase structural sizing or material strength to achieve SF >= {min_sf}."
            ))
        elif applied_sf > 4.0:
            issues.append(ValidationIssueSchema(
                module="SAFETY_FACTOR_VALIDATOR",
                severity=Severity.MEDIUM,
                description=f"Safety factor {applied_sf} is excessively high.",
                engineering_reasoning="Over-design leads to unnecessary mass, cost, and potential performance degradation.",
                recommendation="Optimize the design to reduce mass while maintaining SF >= 1.5."
            ))
            
        return issues
