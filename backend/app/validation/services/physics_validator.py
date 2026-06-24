"""
Physics Validator
"""
from typing import Dict, Any
from dataclasses import dataclass, field


@dataclass
class PhysicsValidationIssue:
    type: str
    message: str
    field: str


class PhysicsValidator:
    """Validates physics calculations"""

    def validate_physics(
        self,
        calculation: Dict[str, Any],
    ):
        issues = []
        if "stress" in calculation:
            stress = calculation["stress"]
            if stress < 0:
                issues.append(
                    PhysicsValidationIssue(
                    type="unphysical",
                    message="Stress can't be negative in this context",
                    field="stress",
                )
        return {"valid": len(issues) ==0, "issues": issues}
