"""
Troy — Safety Factor Validator
Evaluates structural, operational, and electrical safety factors against engineering standards.
"""

from __future__ import annotations

from typing import List
from app.solver.models.domain_models import SolverState
from app.validation.schemas.validation_schemas import ValidationIssueSchema
from app.validation.services.base import AsyncBaseValidator


class SafetyFactorValidator(AsyncBaseValidator):
    """Checks for existence and magnitude of safety factors (e.g. n_safety) across domains."""

    name = "SafetyFactorValidator"

    async def validate(self, state: SolverState) -> List[ValidationIssueSchema]:
        issues: List[ValidationIssueSchema] = []
        domain = (state.domain or "").lower()

        # Find safety factor variable in our variables pool
        safety_factor = None
        sf_name = None

        search_keys = ["n_safety", "sf", "safety_factor", "fos", "margin_of_safety"]
        
        # Check known variables
        for key in search_keys:
            # check exact or substring
            for name, data in state.variables.known.items():
                if key == name.lower() or name.lower().startswith("n_safety") or name.lower() == "sf":
                    if "value" in data and data["value"] is not None:
                        safety_factor = float(data["value"])
                        sf_name = name
                        break
            if safety_factor is not None:
                break

        # Check derived variables if not in known
        if safety_factor is None:
            for key in search_keys:
                for name, data in state.variables.derived.items():
                    if key == name.lower() or name.lower().startswith("n_safety") or name.lower() == "sf":
                        if "value" in data and data["value"] is not None:
                            safety_factor = float(data["value"])
                            sf_name = name
                            break
                if safety_factor is not None:
                    break

        # ── 1. Check if safety factor is completely missing ──
        if safety_factor is None:
            # Aerospace, UAV, and Robotics require mandatory safety factors
            if domain in ["aerospace", "drones", "robotics"]:
                issues.append(
                    ValidationIssueSchema(
                        severity="error",
                        category="Safety",
                        message="Missing explicit safety factor (n_safety)",
                        validator_name=self.name,
                        engineering_reasoning=f"Critical {domain} structural calculations require an explicit factor of safety to determine allowable stress limits.",
                        recommendation="Define a design safety factor variable (e.g. n_safety = 1.5).",
                    )
                )
            else:
                issues.append(
                    ValidationIssueSchema(
                        severity="warning",
                        category="Safety",
                        message="Missing safety factor (n_safety)",
                        validator_name=self.name,
                        engineering_reasoning="A general safety factor is recommended to protect against physical material tolerances and environmental loading variations.",
                        recommendation="Define a safety factor variable (e.g. n_safety = 1.25).",
                    )
                )
            return issues

        # ── 2. Check safety factor values against standards ──
        if safety_factor < 1.0:
            issues.append(
                ValidationIssueSchema(
                    severity="error",
                    category="Safety",
                    message=f"DANGEROUS: Safety factor '{sf_name}' is below 1.0 ({safety_factor})",
                    validator_name=self.name,
                    engineering_reasoning="A safety factor below 1.0 indicates that peak design loads exceed ultimate material limits, leading to immediate mechanical failure or electrical breakdown.",
                    recommendation="Increase component rating or structural size so that the safety factor exceeds 1.0.",
                )
            )
            return issues

        # Domain specific minimum checks
        if domain == "aerospace":
            if safety_factor < 1.5:
                issues.append(
                    ValidationIssueSchema(
                        severity="error",
                        category="Safety",
                        message=f"Aerospace safety factor '{sf_name}' ({safety_factor}) is below certification minimum (1.5)",
                        validator_name=self.name,
                        engineering_reasoning="FAA/EASA standards (such as Federal Aviation Regulations FAR 25.303) mandate a minimum safety factor of 1.5 for primary structures.",
                        recommendation="Redesign elements to achieve a factor of safety of at least 1.5.",
                    )
                )
        elif domain == "drones":
            if safety_factor < 1.2:
                issues.append(
                    ValidationIssueSchema(
                        severity="warning",
                        category="Safety",
                        message=f"Low UAV safety margin: '{sf_name}' = {safety_factor}",
                        validator_name=self.name,
                        engineering_reasoning="Small UAVs can accept safety factors as low as 1.2 for flight structures to conserve weight, but it reduces the wind gust hover stability threshold.",
                        recommendation="Aim for a safety factor of 1.2 to 1.5 for non-critical parts, and 1.5+ for rotor mounts.",
                    )
                )
        elif domain == "robotics":
            if safety_factor < 1.5:
                issues.append(
                    ValidationIssueSchema(
                        severity="warning",
                        category="Safety",
                        message=f"Low robotic safety margin: '{sf_name}' = {safety_factor}",
                        validator_name=self.name,
                        engineering_reasoning="ISO 10218 standards for industrial and collaborative robots suggest safety factors of 1.5 to 2.0+ to prevent joint gearbox failure under emergency braking.",
                        recommendation="Set safety factor to 1.5 for static payloads or 2.0+ for high-acceleration dynamic movements.",
                    )
                )
        elif domain == "electronics":
            if safety_factor < 1.25:
                issues.append(
                    ValidationIssueSchema(
                        severity="warning",
                        category="Safety",
                        message=f"Low electrical component safety margin: '{sf_name}' = {safety_factor}",
                        validator_name=self.name,
                        engineering_reasoning="Power supplies, capacitor voltage ratings, and PCB traces should have at least a 25% margin (safety factor 1.25) to survive line surges and thermal spikes.",
                        recommendation="Ensure components are rated for at least 1.25 times peak operating voltage/current.",
                    )
                )

        return issues
