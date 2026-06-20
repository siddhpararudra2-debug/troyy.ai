"""
Constraint Solver — Engineering Constraint Satisfaction
Evaluates all engineering constraints against a design:
  - Mass, Power, Thermal, Cost, Structural, Safety, Dimensional, Performance
  - Hard constraint violation detection
  - Penalty scoring for soft constraints
  - Engineering fix suggestions
  - Severity classification (warning/error/critical)
"""
from __future__ import annotations

import time
import uuid
from datetime import datetime
from typing import Any, Dict, List

import numpy as np

from app.optimization.schemas import (
    ConstraintSolverRequest, ConstraintSolverResponse, ConstraintViolation,
    ConstraintSpec, ConstraintOperator, ConstraintType,
)


class ConstraintSolver:
    """
    Checks a design vector against a list of engineering constraints.
    Uses domain-aware severity classification and fix generation.
    """

    # Severity thresholds: violation_ratio → severity
    _SEVERITY_THRESHOLDS = {
        "warning":  0.05,   # ≤5% over limit
        "error":    0.20,   # ≤20% over limit
        "critical": float("inf"),  # >20% or hard constraint
    }

    @staticmethod
    def solve(request: ConstraintSolverRequest) -> ConstraintSolverResponse:
        t_start = time.perf_counter()

        design = request.design
        violations: List[ConstraintViolation] = []
        penalty_score = 0.0
        satisfied_count = 0
        violated_count = 0

        for con in request.constraints:
            # Get actual value from design (use 0 if not present)
            actual = design.get(con.name, design.get(f"{con.constraint_type}_{con.name}", 0.0))
            actual = float(actual)

            violation_mag, is_violated = ConstraintSolver._compute_violation(actual, con)

            if is_violated:
                violated_count += 1
                severity = ConstraintSolver._classify_severity(violation_mag, con)
                penalty = violation_mag ** 2 if not con.is_hard else violation_mag ** 2 * 10
                penalty_score += penalty
                fix = ConstraintSolver._generate_fix(con, actual, violation_mag)
                violations.append(ConstraintViolation(
                    constraint_name=con.name,
                    constraint_type=con.constraint_type.value,
                    actual_value=actual,
                    limit_value=con.value,
                    violation_magnitude=round(violation_mag, 4),
                    severity=severity,
                    engineering_fix=fix,
                ))
            else:
                satisfied_count += 1

        is_feasible = (
            violated_count == 0
            or all(not v.severity == "critical" for v in violations)
        )

        # Constraint report
        report: Dict[str, Any] = {
            "total_constraints": len(request.constraints),
            "satisfied": satisfied_count,
            "violated": violated_count,
            "hard_violated": sum(1 for v in violations if v.severity == "critical"),
            "penalty_score": round(penalty_score, 4),
            "by_type": ConstraintSolver._summarize_by_type(violations),
        }

        fix_suggestions = list({v.engineering_fix for v in violations})
        if not fix_suggestions:
            fix_suggestions = ["All constraints satisfied — design is feasible."]

        elapsed = (time.perf_counter() - t_start) * 1000
        return ConstraintSolverResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            is_feasible=is_feasible,
            violations=violations,
            satisfied_count=satisfied_count,
            violated_count=violated_count,
            penalty_score=round(penalty_score, 4),
            constraint_report=report,
            fix_suggestions=fix_suggestions,
            elapsed_ms=round(elapsed, 2),
            created_at=datetime.utcnow(),
        )

    @staticmethod
    def _compute_violation(actual: float, con: ConstraintSpec):
        if con.operator == ConstraintOperator.LTE:
            mag = max(0.0, actual - con.value)
            return mag, mag > 0
        elif con.operator == ConstraintOperator.GTE:
            mag = max(0.0, con.value - actual)
            return mag, mag > 0
        elif con.operator == ConstraintOperator.EQ:
            mag = abs(actual - con.value)
            return mag, mag > 1e-6
        elif con.operator == ConstraintOperator.RANGE:
            lo, hi = con.value, (con.value_max or con.value)
            if actual < lo:
                return lo - actual, True
            if actual > hi:
                return actual - hi, True
            return 0.0, False
        return 0.0, False

    @staticmethod
    def _classify_severity(violation_mag: float, con: ConstraintSpec) -> str:
        if con.is_hard and violation_mag > 0:
            ratio = violation_mag / (abs(con.value) + 1e-12)
            if ratio > 0.20:
                return "critical"
            elif ratio > 0.05:
                return "error"
            return "warning"
        ratio = violation_mag / (abs(con.value) + 1e-12)
        if ratio > 0.20:
            return "error"
        return "warning"

    @staticmethod
    def _generate_fix(con: ConstraintSpec, actual: float, violation: float) -> str:
        ctype = con.constraint_type
        excess = round(violation, 3)
        if ctype == ConstraintType.MASS:
            return (
                f"Mass constraint violated by {excess}{con.unit or 'kg'}. "
                "Consider: (1) Carbon fiber substitution for aluminum, "
                "(2) Topology optimization of structural members, "
                "(3) Reduce non-structural component mass."
            )
        elif ctype == ConstraintType.POWER:
            return (
                f"Power budget exceeded by {excess}{con.unit or 'W'}. "
                "Consider: (1) Switch to more efficient motor/actuator, "
                "(2) Reduce sensor polling rate, "
                "(3) Add power gating for idle subsystems."
            )
        elif ctype == ConstraintType.THERMAL:
            return (
                f"Thermal limit exceeded by {excess}{con.unit or '°C'}. "
                "Consider: (1) Increase heatsink area, "
                "(2) Add forced-air cooling, "
                "(3) Derate operating point, "
                "(4) Use higher-rated thermal interface material."
            )
        elif ctype == ConstraintType.COST:
            return (
                f"Cost constraint exceeded by {excess}{con.unit or 'USD'}. "
                "Consider: (1) Source alternative suppliers, "
                "(2) Reduce specification to commercial grade, "
                "(3) Increase production volume for economies of scale."
            )
        elif ctype == ConstraintType.STRUCTURAL:
            return (
                f"Structural limit exceeded by {excess}{con.unit or 'N'}. "
                "Consider: (1) Increase cross-sectional area, "
                "(2) Add reinforcement gussets, "
                "(3) Switch to higher-strength alloy."
            )
        elif ctype == ConstraintType.SAFETY:
            return (
                f"SAFETY CRITICAL: margin violated by {excess}. "
                "Immediate action required: (1) Redesign to restore safety margins, "
                "(2) Add redundant safety systems, "
                "(3) Reduce operating envelope."
            )
        else:
            return (
                f"Constraint '{con.name}' violated by {excess}{con.unit or ''}. "
                "Review design parameter and adjust to satisfy constraint."
            )

    @staticmethod
    def _summarize_by_type(violations: List[ConstraintViolation]) -> Dict[str, int]:
        summary: Dict[str, int] = {}
        for v in violations:
            summary[v.constraint_type] = summary.get(v.constraint_type, 0) + 1
        return summary
