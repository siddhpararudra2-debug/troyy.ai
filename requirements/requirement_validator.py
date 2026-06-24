"""
Requirement Validator - Validates requirements against quality criteria and standards.

Capabilities:
- Requirement Quality Validation
- Completeness Checks
- Consistency Checks
- Testability Validation
- Validation Reports
"""

import re
from enum import Enum
from typing import Optional, List, Dict, Any, Set, Tuple
from datetime import datetime

from requirements.requirement_manager import (
    Requirement,
    RequirementType,
    RequirementStatus,
    RequirementManager,
)


class ValidationSeverity(str, Enum):
    """Severity levels for validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationRule:
    """A validation rule for checking requirement quality."""

    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        severity: ValidationSeverity = ValidationSeverity.WARNING,
        category: str = "general",
    ):
        self.id = rule_id
        self.name = name
        self.description = description
        self.severity = severity
        self.category = category

    def check(self, requirement: Requirement) -> Optional[Dict[str, Any]]:
        """Check a requirement against this rule. Return issue if found."""
        raise NotImplementedError


class ValidationIssue:
    """A validation issue found during requirement validation."""

    def __init__(
        self,
        rule_id: str,
        rule_name: str,
        severity: ValidationSeverity,
        message: str,
        requirement_id: str,
        location: Optional[str] = None,
        suggestion: Optional[str] = None,
    ):
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.severity = severity
        self.message = message
        self.requirement_id = requirement_id
        self.location = location
        self.suggestion = suggestion

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "message": self.message,
            "requirement_id": self.requirement_id,
            "location": self.location,
            "suggestion": self.suggestion,
        }


class LengthRule(ValidationRule):
    """Check requirement has appropriate length."""

    def __init__(self, min_words: int = 5, max_words: int = 200):
        super().__init__(
            rule_id="LEN-001",
            name="Requirement Length",
            description="Requirement should have between {min_words} and {max_words} words",
            severity=ValidationSeverity.WARNING,
            category="structure",
        )
        self.min_words = min_words
        self.max_words = max_words

    def check(self, requirement: Requirement) -> Optional[ValidationIssue]:
        word_count = len(requirement.description.split())
        if word_count < self.min_words:
            return ValidationIssue(
                rule_id=self.id,
                rule_name=self.name,
                severity=self.severity,
                message=f"Requirement too short ({word_count} words, minimum {self.min_words})",
                requirement_id=requirement.id,
                suggestion="Add more detail to the requirement description",
            )
        if word_count > self.max_words:
            return ValidationIssue(
                rule_id=self.id,
                rule_name=self.name,
                severity=ValidationSeverity.INFO,
                message=f"Requirement very long ({word_count} words), consider splitting",
                requirement_id=requirement.id,
                suggestion="Split into multiple focused requirements",
            )
        return None


class ImperativeMoodRule(ValidationRule):
    """Check requirement uses imperative mood (shall, must, will)."""

    def __init__(self):
        super().__init__(
            rule_id="IMP-001",
            name="Imperative Mood",
            description="Requirement should use 'shall' for mandatory requirements",
            severity=ValidationSeverity.ERROR,
            category="grammar",
        )

    def check(self, requirement: Requirement) -> Optional[ValidationIssue]:
        if requirement.req_type in [RequirementType.FUNCTIONAL, RequirementType.PERFORMANCE]:
            if not re.search(r'\bs(hall|hould|hall not)\b', requirement.description, re.IGNORECASE):
                return ValidationIssue(
                    rule_id=self.id,
                    rule_name=self.name,
                    severity=self.severity,
                    message="Functional/performance requirements should use 'shall'",
                    requirement_id=requirement.id,
                    suggestion="Use 'The system shall ...' or 'The requirement shall ...'",
                )
        return None


class TestabilityRule(ValidationRule):
    """Check requirement is testable/verifiable."""

    def __init__(self):
        super().__init__(
            rule_id="TST-001",
            name="Testability",
            description="Requirement should have testable/verifiable criteria",
            severity=ValidationSeverity.WARNING,
            category="quality",
        )

    def check(self, requirement: Requirement) -> Optional[ValidationIssue]:
        if not requirement.verification_method:
            # Check for measurable criteria
            has_measurement = bool(re.search(r'\b\d+\.?\d*\s*[a-zA-Z%°]+\b', requirement.description))
            has_quantifiable = bool(re.search(
                r'\b(?:within|less than|greater than|at least|up to|between|not to exceed)\b',
                requirement.description, re.IGNORECASE
            ))
            if not has_measurement and not has_quantifiable and requirement.req_type != RequirementType.FUNCTIONAL:
                return ValidationIssue(
                    rule_id=self.id,
                    rule_name=self.name,
                    severity=self.severity,
                    message="Requirement lacks testable/measurable criteria",
                    requirement_id=requirement.id,
                    suggestion="Add measurable criteria or specify verification method",
                )
        return None


class UniquenessRule(ValidationRule):
    """Check for duplicate requirements."""

    def __init__(self, manager: RequirementManager):
        super().__init__(
            rule_id="UNQ-001",
            name="Uniqueness",
            description="Requirement should not be a duplicate of another requirement",
            severity=ValidationSeverity.WARNING,
            category="consistency",
        )
        self._manager = manager

    def check(self, requirement: Requirement) -> Optional[ValidationIssue]:
        for other in self._manager.get_all_requirements():
            if other.id != requirement.id:
                similarity = self._text_similarity(
                    requirement.description.lower(),
                    other.description.lower()
                )
                if similarity > 0.85:
                    return ValidationIssue(
                        rule_id=self.id,
                        rule_name=self.name,
                        severity=self.severity,
                        message=f"Requirement appears to duplicate '{other.title}' (similarity: {similarity:.0%})",
                        requirement_id=requirement.id,
                        suggestion="Merge with existing requirement or clarify the difference",
                    )
        return None

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Simple Jaccard similarity on word sets."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        if not words1 or not words2:
            return 0.0
        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / len(union)


class RequirementValidator:
    """
    Validates requirements against quality criteria.
    Provides comprehensive validation with severity levels.
    """

    def __init__(self, requirement_manager: Optional[RequirementManager] = None):
        self._manager = requirement_manager or RequirementManager()
        self._rules: List[ValidationRule] = self._default_rules()

    def _default_rules(self) -> List[ValidationRule]:
        """Create default validation rules."""
        return [
            LengthRule(),
            ImperativeMoodRule(),
            TestabilityRule(),
        ]

    def set_requirement_manager(self, manager: RequirementManager):
        """Set the requirement manager and update rules."""
        self._manager = manager
        self._rules = self._default_rules()
        self._rules.append(UniquenessRule(manager))

    def add_rule(self, rule: ValidationRule):
        """Add a custom validation rule."""
        self._rules.append(rule)

    def validate(self, requirement: Requirement) -> List[ValidationIssue]:
        """Validate a single requirement against all rules."""
        issues = []
        for rule in self._rules:
            try:
                issue = rule.check(requirement)
                if issue:
                    issues.append(issue)
            except Exception as e:
                issues.append(ValidationIssue(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    severity=ValidationSeverity.ERROR,
                    message=f"Validation error: {str(e)}",
                    requirement_id=requirement.id,
                ))
        return issues

    def validate_all(self) -> Dict[str, Any]:
        """Validate all requirements."""
        all_issues: List[ValidationIssue] = []
        requirements_checked = 0
        requirements_with_issues = 0

        for req in self._manager.get_all_requirements():
            issues = self.validate(req)
            if issues:
                requirements_with_issues += 1
            all_issues.extend(issues)
            requirements_checked += 1

        # Count by severity
        severity_counts: Dict[str, int] = {}
        for issue in all_issues:
            severity_counts[issue.severity.value] = severity_counts.get(issue.severity.value, 0) + 1

        # Issues by category
        category_counts: Dict[str, int] = {}
        for rule in self._rules:
            category_counts[rule.category] = 0
        for issue in all_issues:
            for rule in self._rules:
                if rule.id == issue.rule_id:
                    category_counts[rule.category] = category_counts.get(rule.category, 0) + 1
                    break

        return {
            "total_requirements": requirements_checked,
            "requirements_with_issues": requirements_with_issues,
            "total_issues": len(all_issues),
            "by_severity": severity_counts,
            "by_category": category_counts,
            "issues": [issue.to_dict() for issue in all_issues],
            "validated_at": datetime.utcnow().isoformat(),
        }

    def validate_batch(self, requirement_ids: List[str]) -> List[ValidationIssue]:
        """Validate a specific set of requirements."""
        issues = []
        for rid in requirement_ids:
            req = self._manager.get_requirement(rid)
            if req:
                issues.extend(self.validate(req))
        return issues

    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate a comprehensive validation report."""
        validation = self.validate_all()

        report = {
            "report_type": "Requirement Validation Report",
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_requirements": validation["total_requirements"],
                "requirements_with_issues": validation["requirements_with_issues"],
                "total_issues": validation["total_issues"],
                "error_count": validation["by_severity"].get("error", 0),
                "warning_count": validation["by_severity"].get("warning", 0),
                "info_count": validation["by_severity"].get("info", 0),
                "pass_rate": (
                    (validation["total_requirements"] - validation["requirements_with_issues"])
                    / validation["total_requirements"] * 100
                    if validation["total_requirements"] > 0 else 0
                ),
            },
            "severity_breakdown": validation["by_severity"],
            "category_breakdown": validation["by_category"],
            "issues": validation["issues"],
            "recommendations": self._generate_recommendations(validation),
        }
        return report

    def _generate_recommendations(self, validation: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations based on validation results."""
        recommendations = []

        if validation["by_severity"].get("error", 0) > 0:
            recommendations.append(
                f"Fix {validation['by_severity']['error']} error(s) that violate mandatory quality criteria"
            )
        if validation["by_severity"].get("warning", 0) > 0:
            recommendations.append(
                f"Address {validation['by_severity']['warning']} warning(s) to improve requirement quality"
            )
        if validation["by_severity"].get("info", 0) > 5:
            recommendations.append("Consider simplifying or splitting very long requirements")

        # Category-specific recommendations
        if validation["by_category"].get("testability", 0) > 0:
            recommendations.append("Add measurable criteria or verification methods to improve testability")

        if validation["by_category"].get("consistency", 0) > 0:
            recommendations.append("Resolve duplicate or conflicting requirements")

        return recommendations

    def check_completeness(self, requirement: Requirement) -> List[str]:
        """Check if a requirement is complete (has all necessary attributes)."""
        missing = []
        if not requirement.title:
            missing.append("Title is missing")
        if not requirement.description:
            missing.append("Description is missing")
        if not requirement.owner:
            missing.append("Owner is not assigned")
        if not requirement.verification_method:
            missing.append("Verification method is not specified")
        if requirement.priority is None:
            missing.append("Priority is not assigned")
        if requirement.status == RequirementStatus.DRAFT:
            missing.append("Requirement is still in DRAFT status")
        return missing