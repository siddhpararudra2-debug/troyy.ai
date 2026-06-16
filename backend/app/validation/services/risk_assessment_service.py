"""
Troy — Risk Assessment Service
Compiles validation issues into structured hazard risk items and evaluates overall risk.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any
from app.validation.schemas.validation_schemas import ValidationIssueSchema, RiskItem

logger = logging.getLogger("validation.services.risk_assessment")


class RiskAssessmentService:
    """Evaluates design and calculation failures to score overall project risk levels."""

    async def assess_risks(self, issues: List[ValidationIssueSchema]) -> Dict[str, Any]:
        logger.info(f"Assessing risk levels across {len(issues)} validation issues")

        risk_items: List[RiskItem] = []
        overall_risk = "LOW"

        for issue in issues:
            desc = issue.message
            cause = issue.engineering_reasoning or "Unresolved parameter or design configuration gap."
            rec_fix = issue.recommendation or "Define the parameter in inputs."

            # Determine risk attributes based on issue parameters
            if issue.severity == "error":
                # Critical calculations or safety factors
                if issue.category in ["Safety", "Calculations"]:
                    severity = "CRITICAL"
                    probability = "MEDIUM"
                    impact = "CATASTROPHIC"
                else:
                    severity = "HIGH"
                    probability = "HIGH"
                    impact = "HIGH"
            elif issue.severity == "warning":
                severity = "MEDIUM"
                probability = "MEDIUM"
                impact = "MEDIUM"
            else:
                severity = "LOW"
                probability = "LOW"
                impact = "LOW"

            risk_items.append(
                RiskItem(
                    description=desc,
                    cause=cause,
                    severity=severity,
                    probability=probability,
                    impact=impact,
                    recommended_fix=rec_fix,
                )
            )

        # ── Compute Overall Risk Level ───────────────────────────────────────
        severities = {r.severity for r in risk_items}
        impacts = {r.impact for r in risk_items}

        if "CRITICAL" in severities or "CATASTROPHIC" in impacts:
            overall_risk = "CRITICAL"
        elif "HIGH" in severities or "HIGH" in impacts:
            overall_risk = "HIGH"
        elif "MEDIUM" in severities or "MEDIUM" in impacts:
            overall_risk = "MEDIUM"
        else:
            overall_risk = "LOW"

        return {
            "overall_risk_level": overall_risk,
            "risks": risk_items,
        }
