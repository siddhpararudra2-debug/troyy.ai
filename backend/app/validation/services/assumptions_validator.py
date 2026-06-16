"""
Troy — Assumptions Validator
Analyzes engineering assumptions to check for physical limits, safety margins, and risks.
"""

from __future__ import annotations

import re
from typing import List
from app.solver.models.domain_models import SolverState
from app.validation.schemas.validation_schemas import ValidationIssueSchema
from app.validation.services.base import AsyncBaseValidator


class AssumptionsValidator(AsyncBaseValidator):
    """Reviews assumptions and flags unphysical limits (e.g. 100% efficiency) or risky omissions."""

    name = "AssumptionsValidator"

    async def validate(self, state: SolverState) -> List[ValidationIssueSchema]:
        issues: List[ValidationIssueSchema] = []

        for a in state.assumptions:
            assumption_text = a.assumption
            text_lower = assumption_text.lower()

            classification = "SAFE"
            severity = "info"
            explanation = "Standard baseline engineering assumption."
            risk_level = "LOW"
            suggested_alternative = "None required."

            # ── 1. Check for DANGEROUS assumptions (Physically unrealistic) ──
            
            # Check for 100% efficiency / perfect energy conversion
            efficiency_match = re.search(r"(\d+)%\s*efficiency|efficiency\s*=\s*(1\.0|100)", text_lower)
            if efficiency_match and ("battery" in text_lower or "motor" in text_lower or "gear" in text_lower or "propeller" in text_lower or "transmission" in text_lower):
                classification = "DANGEROUS"
                severity = "error"
                risk_level = "CRITICAL"
                explanation = "A perfect 100% efficiency ignores thermodynamic losses (thermal dissipation, friction, copper losses) which violates physical laws."
                suggested_alternative = "Apply a realistic efficiency factor: 85-90% for brushless motors, 95% for lithium batteries, 90-95% for gearing."

            elif "no drag" in text_lower or "zero drag" in text_lower or "drag coefficient = 0" in text_lower:
                classification = "DANGEROUS"
                severity = "error"
                risk_level = "HIGH"
                explanation = "Assuming zero aerodynamic drag is unrealistic for aerial vehicles and leads to massive underestimations of propulsion requirements."
                suggested_alternative = "Use a baseline drag coefficient (e.g., Cd = 0.05 to 0.15 for multirotors, Cd = 0.02 to 0.04 for clean wings)."

            elif "no friction" in text_lower or "zero friction" in text_lower or "frictionless" in text_lower:
                classification = "DANGEROUS"
                severity = "error"
                risk_level = "HIGH"
                explanation = "Assuming zero friction ignores mechanical resistance and starting torque, causing actuator stalls."
                suggested_alternative = "Incorporate bearing friction and gear mesh efficiency losses (typically 2-5% per mesh)."

            # ── 2. Check for QUESTIONABLE assumptions ──
            
            elif "calm weather" in text_lower or "no wind" in text_lower or "zero wind" in text_lower:
                if state.domain in ["drones", "aerospace", "multi"]:
                    classification = "QUESTIONABLE"
                    severity = "warning"
                    risk_level = "MEDIUM"
                    explanation = "Assuming calm weather or zero wind is unsafe for outdoor UAV flight operations. Gusts increase motor loading and battery depletion."
                    suggested_alternative = "Add a wind tolerance safety margin of at least 5-10 m/s for hover power calculations."

            elif "neglect thermal" in text_lower or "no thermal loss" in text_lower or "ignore heating" in text_lower:
                classification = "QUESTIONABLE"
                severity = "warning"
                risk_level = "MEDIUM"
                explanation = "Neglecting thermal dissipation could result in overheating of motor coils, electronics, or batteries during peak current draw."
                suggested_alternative = "Estimate a convective cooling coefficient or verify thermal steady-state limits."

            elif "ignore wire" in text_lower or "neglect cabling" in text_lower or "zero connector weight" in text_lower:
                classification = "QUESTIONABLE"
                severity = "warning"
                risk_level = "MEDIUM"
                explanation = "Cabling and connectors typically account for 5% to 15% of empty structural mass in small UAVs or electronics enclosures."
                suggested_alternative = "Include a 10% weight penalty allocation for cabling, solder, and structural fasteners."

            # ── 3. Check for SAFE standard scientific assumptions ──
            elif "9.81" in text_lower or "gravity" in text_lower or "1.225" in text_lower or "density of air" in text_lower:
                classification = "SAFE"
                severity = "info"
                risk_level = "LOW"
                explanation = "Standard constant baseline for physical environments."
                suggested_alternative = "Continue using default gravity (9.81 m/s^2) or standard sea-level air density (1.225 kg/m^3)."

            issues.append(
                ValidationIssueSchema(
                    severity=severity,
                    category="Assumptions",
                    message=f"[{classification}] Assumption: '{assumption_text}'",
                    validator_name=self.name,
                    engineering_reasoning=f"Risk Level: {risk_level}. Explanation: {explanation}",
                    recommendation=suggested_alternative,
                )
            )

        return issues
