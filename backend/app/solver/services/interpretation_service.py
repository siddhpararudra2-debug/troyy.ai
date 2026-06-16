"""
Troy — Engineering Interpretation Service
Compares calculation results against constraints and generates structured
engineering interpretations.
"""

from __future__ import annotations

import logging
import re
from typing import List

from app.solver.models.domain_models import (
    ConstraintData,
    InterpretationData,
    SolverState,
)

logger = logging.getLogger("solver.services.interpretation")


class InterpretationService:
    """Interprets calculation results in the context of engineering constraints."""

    async def interpret_results(self, state: SolverState) -> InterpretationData:
        """
        Analyze results, run threshold checks, and generate a markdown interpretation.
        """
        logger.info(f"Interpreting results for solver session {state.session_id}")

        results = state.calculation_results
        constraints = state.constraints
        domain = state.domain

        # If no calculation was run or no results exist
        if not results:
            return InterpretationData(
                interpretation="No calculation results were generated to interpret."
            )

        interpretations: List[str] = []

        # ── Domain-specific template introduction ─────────────────
        if domain == "drones":
            interpretations.append(
                "### Multirotor Drone Sizing Analysis\n"
                "The preliminary sizing calculation has evaluated hover performance and lift requirements."
            )
        elif domain == "aerospace":
            interpretations.append(
                "### Aerodynamic Sizing Analysis\n"
                "The aerodynamic evaluation has computed lift/drag forces and flow regimes."
            )
        elif domain == "robotics":
            interpretations.append(
                "### Robotic Kinematics & Sizing Analysis\n"
                "The joint-space dynamic analysis has computed peak torque requirements."
            )
        elif domain == "electronics":
            interpretations.append(
                "### Electronic Thermal & Power Analysis\n"
                "The circuit simulation has assessed junction temperatures and passive cooling limits."
            )
        else:
            interpretations.append(
                "### Engineering Sizing Analysis\n"
                "The system sizing calculation has evaluated performance parameters."
            )

        # ── Threshold Check / Margin Analysis ────────────────────
        violations = []
        passed_checks = []

        # Try to match variables to constraint limits
        # e.g., if a constraint limit is "Max Takeoff Weight (MTOW) <= 7.00 kg"
        # and we calculated a weight/AUW or MTOW of 8.0 kg, we flag it.
        for c in constraints:
            limit_str = c.limit
            # Parse limits like: "<= 7.00" or ">= 150" or "peak torque <= 10.0"
            match = re.search(r"(<=|>=|<|>)\s*([\d\.]+)", limit_str)
            if not match:
                continue
            
            operator, limit_val_str = match.groups()
            limit_val = float(limit_val_str)

            # Find a matching result key
            matched_key = None
            matched_val = None

            # Look for keys like: T_motor, m, P, DL, L, D, torque_req, I
            # Let's map constraint category/limit to result keys
            lower_limit = limit_str.lower()
            if "takeoff weight" in lower_limit or "mtow" in lower_limit or "weight" in lower_limit:
                # MTOW
                matched_key = "m_total" if "m_total" in results else ("m" if "m" in results else None)
            elif "thrust" in lower_limit:
                matched_key = "T_total" if "T_total" in results else None
            elif "power" in lower_limit or "watt" in lower_limit:
                matched_key = "P" if "P" in results else None
            elif "torque" in lower_limit:
                matched_key = "torque_req" if "torque_req" in results else None
            elif "current" in lower_limit:
                matched_key = "I" if "I" in results else None
            elif "temperature" in lower_limit:
                matched_key = "T_junction" if "T_junction" in results else None

            if matched_key and matched_key in results:
                matched_val = float(results[matched_key])

            if matched_val is not None:
                is_violated = False
                if operator == "<=" and matched_val > limit_val:
                    is_violated = True
                elif operator == ">=" and matched_val < limit_val:
                    is_violated = True
                elif operator == "<" and matched_val >= limit_val:
                    is_violated = True
                elif operator == ">" and matched_val <= limit_val:
                    is_violated = True

                margin = abs(matched_val - limit_val)
                margin_percent = (margin / limit_val) * 100 if limit_val != 0 else 0
                
                if is_violated:
                    violations.append(
                        f"❌ **Constraint Violated:** {c.category} limit of `{limit_str}` exceeded. "
                        f"Calculated `{matched_key}` is `{matched_val:.2f}` (Violation margin of {margin:.2f} / {margin_percent:.1f}%)."
                    )
                else:
                    passed_checks.append(
                        f"✅ **Constraint Passed:** {c.category} limit of `{limit_str}` is satisfied. "
                        f"Calculated `{matched_key}` is `{matched_val:.2f}` (Safety margin of {margin:.2f} / {margin_percent:.1f}%)."
                    )

        # ── Append findings ──────────────────────────────────────
        interpretations.append("#### Constraint Compliance & Sizing Margin")
        if violations:
            interpretations.extend(violations)
        if passed_checks:
            interpretations.extend(passed_checks)
        if not violations and not passed_checks:
            interpretations.append("All calculated outputs are within acceptable baseline bounds.")

        # ── Domain-specific feedback ──────────────────────────────
        interpretations.append("#### Engineering Assessment")
        if domain == "drones":
            if "t_flight_min" in results:
                t_flight = results["t_flight_min"]
                target_t = 20.0
                if "t_endurance" in state.variables.known:
                    target_t = float(state.variables.known["t_endurance"]["value"])
                
                if t_flight < target_t:
                    interpretations.append(
                        f"⚠️ **Endurance Deficit:** The estimated flight time of **{t_flight:.1f} minutes** is below the target endurance of **{target_t:.1f} minutes**. "
                        "Consider reducing payload weight or increasing battery capacity."
                    )
                else:
                    interpretations.append(
                        f"✨ **Endurance Target Met:** The estimated flight time of **{t_flight:.1f} minutes** satisfies the target of **{target_t:.1f} minutes**."
                    )
        
        elif domain == "electronics":
            if "P" in results and results["P"] > 5.0:
                interpretations.append(
                    "⚠️ **Thermal Advisory:** Power dissipation exceeds 5.0 W. Active cooling (fan or oversized heatsink) is highly recommended."
                )

        full_text = "\n\n".join(interpretations)
        return InterpretationData(interpretation=full_text)
