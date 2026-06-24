"""
Mission Analyzer - Analyzes missions for feasibility and performance.

Capabilities:
- Mission Feasibility Analysis
- Performance Verification
- Constraint Checking
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from mission.mission_planner import Mission, MissionConstraint, PerformanceTarget


class MissionAnalyzer:
    """Analyzes missions for feasibility and performance achievement."""

    def analyze_feasibility(self, mission: Mission) -> Dict[str, Any]:
        """Analyze mission feasibility based on constraints."""
        issues = []
        warnings = []

        if not mission.objectives:
            issues.append("Mission has no defined objectives")

        if not mission.constraints:
            warnings.append("Mission has no constraints defined")

        if not mission.performance_targets:
            warnings.append("Mission has no performance targets")

        feasibility_score = 1.0
        if issues:
            feasibility_score -= 0.3 * len(issues)
        if warnings:
            feasibility_score -= 0.1 * len(warnings)

        return {
            "mission_id": mission.id,
            "mission_name": mission.name,
            "feasible": len(issues) == 0,
            "feasibility_score": max(0.0, feasibility_score),
            "issues": issues,
            "warnings": warnings,
            "analyzed_at": datetime.utcnow().isoformat(),
        }

    def verify_performance(self, mission: Mission, achieved_values: Dict[str, float]) -> Dict[str, Any]:
        """Verify if performance targets are met."""
        results = []
        all_met = True
        for target in mission.performance_targets:
            achieved = achieved_values.get(target.name)
            if achieved is not None:
                met = achieved >= target.target_value if target.target_value > 0 else True
                if not met:
                    all_met = False
                results.append({
                    "target": target.name,
                    "required": target.target_value,
                    "achieved": achieved,
                    "unit": target.unit,
                    "met": met,
                    "gap": target.target_value - achieved if not met else 0,
                })
            else:
                results.append({
                    "target": target.name,
                    "required": target.target_value,
                    "achieved": None,
                    "unit": target.unit,
                    "met": False,
                    "gap": target.target_value,
                })
                all_met = False

        return {
            "mission_id": mission.id,
            "all_targets_met": all_met,
            "targets_met": sum(1 for r in results if r["met"]),
            "total_targets": len(results),
            "results": results,
            "verified_at": datetime.utcnow().isoformat(),
        }

    def check_constraints(self, mission: Mission, actual_values: Dict[str, Any]) -> Dict[str, Any]:
        """Check if constraints are satisfied."""
        results = []
        all_satisfied = True
        for constraint in mission.constraints:
            actual = actual_values.get(constraint.name)
            if actual is not None:
                satisfied = True
                if isinstance(constraint.value, (int, float)) and isinstance(actual, (int, float)):
                    satisfied = actual <= constraint.value
                results.append({
                    "constraint": constraint.name,
                    "type": constraint.type,
                    "required_max": constraint.value,
                    "actual": actual,
                    "unit": constraint.unit,
                    "satisfied": satisfied,
                })
                if not satisfied:
                    all_satisfied = False
            else:
                results.append({
                    "constraint": constraint.name,
                    "required": constraint.value,
                    "actual": None,
                    "satisfied": False,
                })
                all_satisfied = False

        return {
            "mission_id": mission.id,
            "all_constraints_satisfied": all_satisfied,
            "constraints_satisfied": sum(1 for r in results if r["satisfied"]),
            "total_constraints": len(results),
            "results": results,
            "checked_at": datetime.utcnow().isoformat(),
        }