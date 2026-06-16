import pint
from typing import Dict, Any, List
from validation.services.base_validator import BaseValidator
from validation.schemas.validation import ValidationIssueSchema, Severity

# Singleton Pint Registry for Performance (<50ms initialization)
ureg = pint.UnitRegistry()
ureg.formatter.default_format = "~P"

class UnitValidator(BaseValidator):
    async def validate(self, data: Dict[str, Any]) -> List[ValidationIssueSchema]:
        issues = []
        calculations = data.get("calculations", [])
        
        for calc in calculations:
            expected_unit = calc.get("expected_unit")
            value = calc.get("value")
            unit = calc.get("unit")
            
            if not unit or not expected_unit:
                issues.append(ValidationIssueSchema(
                    module="UNIT_VALIDATOR",
                    severity=Severity.HIGH,
                    description=f"Missing unit definition in calculation: {calc.get('name')}",
                    engineering_reasoning="Dimensional consistency cannot be verified without explicit units.",
                    recommendation="Define both input and output units using SI or imperial standards."
                ))
                continue

            try:
                qty = value * ureg(unit)
                expected_qty = 1 * ureg(expected_unit)
                if not qty.is_compatible_with(expected_qty):
                    issues.append(ValidationIssueSchema(
                        module="UNIT_VALIDATOR",
                        severity=Severity.CRITICAL,
                        description=f"Unit mismatch in {calc.get('name')}: got {unit}, expected {expected_unit}",
                        engineering_reasoning="Dimensional analysis failed. This will cause catastrophic system failure if deployed.",
                        recommendation=f"Convert output to {expected_unit} or verify the underlying formula."
                    ))
            except pint.UndefinedUnitError:
                issues.append(ValidationIssueSchema(
                    module="UNIT_VALIDATOR",
                    severity=Severity.HIGH,
                    description=f"Invalid unit '{unit}' used in {calc.get('name')}",
                    engineering_reasoning="Pint registry does not recognize this unit.",
                    recommendation="Use standard units (e.g., 'm', 'kg', 'N', 'V', 'W')."
                ))
            except Exception as e:
                issues.append(ValidationIssueSchema(
                    module="UNIT_VALIDATOR",
                    severity=Severity.MEDIUM,
                    description=f"Unit validation error: {str(e)}",
                    engineering_reasoning="Unexpected error during dimensional analysis.",
                    recommendation="Review calculation structure."
                ))
        return issues
