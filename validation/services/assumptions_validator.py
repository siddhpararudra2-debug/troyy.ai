from typing import Dict, Any, List
from validation.services.base_validator import BaseValidator
from validation.schemas.validation import ValidationIssueSchema, Severity

class AssumptionsValidator(BaseValidator):
    DANGEROUS_KEYWORDS = ["100% efficient", "zero friction", "infinite", "perfect", "no loss"]
    
    async def validate(self, data: Dict[str, Any]) -> List[ValidationIssueSchema]:
        issues = []
        assumptions = data.get("assumptions", [])
        
        for assumption in assumptions:
            assumption_lower = assumption.lower()
            if any(keyword in assumption_lower for keyword in self.DANGEROUS_KEYWORDS):
                issues.append(ValidationIssueSchema(
                    module="ASSUMPTIONS_VALIDATOR",
                    severity=Severity.CRITICAL,
                    description=f"Dangerous assumption detected: '{assumption}'",
                    engineering_reasoning="Physically unrealistic. No real-world system achieves 100% efficiency or zero friction.",
                    recommendation="Apply realistic derating factors (e.g., 85-90% efficiency for motors)."
                ))
            elif "negligible" in assumption_lower and ("weight" in assumption_lower or "mass" in assumption_lower):
                issues.append(ValidationIssueSchema(
                    module="ASSUMPTIONS_VALIDATOR",
                    severity=Severity.HIGH,
                    description=f"Questionable assumption: '{assumption}'",
                    engineering_reasoning="In aerospace/UAV design, mass is never negligible. Accumulated masses cause CG shifts.",
                    recommendation="Include all masses in the weight budget, even if < 1% of total mass."
                ))
        return issues
