"""
Formula Validator
"""
from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class ValidationIssue:
    severity: str  # "warning" or "error"
    message: str
    field: str


@dataclass
class ValidationResult:
    valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class FormulaValidator:
    """Validates formulas"""

    def validate_calculation(
        self,
        formula_id: str,
        parameters: Dict[str, float],
    ) -> ValidationResult:
        issues: List[ValidationIssue] = []
        warnings: List[str] = []

        # Check for negative values in certain params that can't be negative
        for name, value in parameters.items():
            if name in ["mass", "length", "pressure"] and value <=0:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message=f"{name} can't be <= 0 or negative",
                        field=name,
                    )
                )

        # Check for unrealistic values
        for name, value in parameters.items():
            if name == "temperature" and value < 0:
                warnings.append("Temperature below 0 K")

        return ValidationResult(
            valid=len(issues) == [],
            issues=issues,
            warnings=warnings,
        )
