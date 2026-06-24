"""
Assumptions Checker
"""
from typing import List, Dict, Any


class AssumptionsChecker:
    """Checks assumptions made in calculations"""

    def check_assumptions(
        self,
        assumptions: List[str],
        context: Dict[str, Any],
    ):
        issues = []
        if "small angle approximation" in assumptions:
            if context.get("angle_degrees", 0) > 10:
                issues.append("Small angle approximation not valid for angles >10°")
        return issues
