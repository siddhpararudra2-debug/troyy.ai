"""
Troy — Approval Service
Evaluates validation runs and risk assessments to issue the final engineering gate approval decision.
"""

from __future__ import annotations

import logging
from typing import Dict, Any
from app.validation.schemas.validation_schemas import ValidationReportResponse

logger = logging.getLogger("validation.services.approval")


class ApprovalService:
    """Gatekeeper approval engine that issues the final design sign-off or rejection."""

    async def evaluate_approval(
        self,
        report: Dict[str, Any],  # ValidationReportResponse dict or fields
        risk_assessment: Dict[str, Any],  # RiskAssessmentResponse dict or fields
        review: Dict[str, Any],  # EngineeringReviewResponse dict or fields
    ) -> Dict[str, Any]:
        logger.info("Evaluating engineering approval status")

        total_errors = report.get("total_errors", 0)
        total_warnings = report.get("total_warnings", 0)
        overall_risk = risk_assessment.get("overall_risk_level", "LOW")

        # ── 1. Determine Status ──────────────────────────────────────────────
        # REJECTED: CRITICAL risks, safety factor < 1.0, or unphysical values
        # REQUIRES REVISION: HIGH risks or errors
        # APPROVED WITH CONCERNS: MEDIUM risks or warnings
        # APPROVED: 0 issues, LOW risk

        if overall_risk == "CRITICAL" or any("DANGEROUS" in issue.get("message", "") for issue in report.get("issues", [])):
            status = "REJECTED"
            reasoning = "The design has been REJECTED by the engineering gatekeeper due to critical safety factor violations, physical impossibilities (e.g. 100% efficiency), or catastrophic hazard risks."
        elif overall_risk == "HIGH" or total_errors > 0:
            status = "REQUIRES REVISION"
            reasoning = "The design REQUIRES REVISION. Critical engineering requirements are missing, or calculation recomputations failed, indicating structural instability or mathematical errors."
        elif overall_risk == "MEDIUM" or total_warnings > 0:
            status = "APPROVED WITH CONCERNS"
            reasoning = "The design is APPROVED WITH CONCERNS. All critical calculations match and safety factors meet minimum standards, but warnings (e.g. low safety margins, questionable assumptions) must be monitored during field testing."
        else:
            status = "APPROVED"
            reasoning = "The design is APPROVED. The calculations are mathematically verified, units are dimensionally consistent, safety factors satisfy regulatory limits, and all assumptions are validated."

        # ── 2. Build summaries ────────────────────────────────────────────────
        val_summary = f"Validation completed with {total_errors} errors and {total_warnings} warnings."
        
        risks_count = len(risk_assessment.get("risks", []))
        risk_summary = f"Risk assessment classified overall risk as {overall_risk} with {risks_count} total risks flagged."

        return {
            "status": status,
            "engineering_reasoning": reasoning,
            "risk_summary": risk_summary,
            "validation_summary": val_summary,
        }
