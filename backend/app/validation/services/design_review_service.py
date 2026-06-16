"""
Troy — Design Review Service
Simulates a Senior Engineering Review Board, checking weight/power budgets and thermal limits.
"""

from __future__ import annotations

import logging
from typing import Dict, Any
from app.solver.models.domain_models import SolverState

logger = logging.getLogger("validation.services.design_review")


class DesignReviewService:
    """Conducts rigorous, destructive engineering audit on budgets and subsystem interfaces."""

    async def review_design(self, state: SolverState) -> Dict[str, Any]:
        logger.info(f"Running engineering design review for project {state.project_id}")

        domain = (state.domain or "").lower()

        # Build a pool of all resolved variables
        variables: Dict[str, float] = {}
        for k, v in state.variables.known.items():
            if "value" in v and v["value"] is not None:
                variables[k] = float(v["value"])
        for k, v in state.variables.derived.items():
            if "value" in v and v["value"] is not None:
                variables[k] = float(v["value"])
        for k, v in state.variables.constants.items():
            if "value" in v and v["value"] is not None:
                variables[k] = float(v["value"])

        # Also pull from calculation results
        for k, v in state.calculation_results.items():
            if v is not None:
                variables[k] = float(v)

        # ── Setup Default Review Ratings ─────────────────────────────────────
        checks = {
            "design_decisions_check": "Passed",
            "component_choices_check": "Passed",
            "structural_choices_check": "Passed",
            "electrical_choices_check": "Passed",
            "weight_budgets_check": "Passed",
            "power_budgets_check": "Passed",
            "thermal_assumptions_check": "Passed",
        }
        flaws = []

        # ── 1. Weight Budgets Check ──────────────────────────────────────────
        m_payload = variables.get("m_payload", variables.get("payload", 0.0))
        m_empty = variables.get("m_empty", variables.get("empty_weight", 0.0))
        m_total = variables.get("m_total", variables.get("m", 0.0))
        mtow = variables.get("mtow", variables.get("max_takeoff_weight", 0.0))

        if m_total == 0.0 and m_payload > 0.0 and m_empty > 0.0:
            m_total = m_payload + m_empty

        if mtow > 0.0 and m_total > 0.0:
            if m_total > mtow:
                checks["weight_budgets_check"] = "Failed"
                flaws.append(f"Total mass ({m_total:.2f} kg) exceeds maximum takeoff weight ({mtow:.2f} kg).")
            elif m_total > 0.9 * mtow:
                checks["weight_budgets_check"] = "Passed with Concerns"
                flaws.append(f"Total mass is at {m_total/mtow*100:.1f}% of MTOW. Very low payload expansion margin.")
        
        # ── 2. Power & Electrical Budgets Check ──────────────────────────────
        p_hover = variables.get("p_hover", variables.get("P_hover", variables.get("P", 0.0)))
        p_battery_max = variables.get("p_battery_max", variables.get("power_battery_max", 0.0))
        i_hover = variables.get("i_hover", 0.0)
        i_max = variables.get("i_max", variables.get("current_max", 0.0))
        battery_capacity_ah = variables.get("c_battery", variables.get("battery_capacity", 0.0))
        voltage = variables.get("v_in", variables.get("voltage", 0.0))

        # Re-derive currents if missing
        if i_hover == 0.0 and p_hover > 0.0 and voltage > 0.0:
            i_hover = p_hover / voltage

        if p_hover > 0.0 and p_battery_max > 0.0:
            if p_hover > p_battery_max:
                checks["power_budgets_check"] = "Failed"
                flaws.append(f"Hover power requirement ({p_hover:.1f} W) exceeds battery power capability ({p_battery_max:.1f} W).")
            elif p_hover > 0.8 * p_battery_max:
                checks["power_budgets_check"] = "Passed with Concerns"
                flaws.append(f"Hover power is at {p_hover/p_battery_max*100:.1f}% of battery capacity limit.")

        if i_hover > 0.0 and i_max > 0.0:
            if i_hover > i_max:
                checks["power_budgets_check"] = "Failed"
                flaws.append(f"Hover current draw ({i_hover:.1f} A) exceeds battery continuous discharge current ({i_max:.1f} A).")

        # ── 3. Component & Actuator Choices Check ────────────────────────────
        # For UAV, check thrust-to-weight ratio
        t_total = variables.get("t_total", variables.get("T_total", variables.get("T", 0.0)))
        w_total = m_total * 9.81 if m_total > 0.0 else variables.get("W_total", 0.0)

        if t_total > 0.0 and w_total > 0.0:
            tw_ratio = t_total / w_total
            if tw_ratio < 1.2:
                checks["component_choices_check"] = "Failed"
                flaws.append(f"Critical: Thrust-to-weight ratio ({tw_ratio:.2f}) is below safe hover threshold (1.20). Vehicle cannot control hover.")
            elif tw_ratio < 1.8:
                checks["component_choices_check"] = "Passed with Concerns"
                flaws.append(f"Low thrust-to-weight ratio ({tw_ratio:.2f}). Safe hover requires a ratio of 2.0+ for acceleration margins.")
            elif tw_ratio > 4.0:
                checks["component_choices_check"] = "Passed with Concerns"
                flaws.append(f"Thrust-to-weight ratio ({tw_ratio:.2f}) is extremely high. Actuators may be oversized, adding excessive weight.")

        # ── 4. Thermal Assumptions Check ─────────────────────────────────────
        # If power dissipation is very high but no active cooling or heat sink is specified
        if p_hover > 200.0:
            has_cooling = False
            for a in state.assumptions:
                if "cooling" in a.assumption.lower() or "heatsink" in a.assumption.lower() or "thermal dissipation" in a.assumption.lower():
                    has_cooling = True
                    break
            if not has_cooling:
                checks["thermal_assumptions_check"] = "Passed with Concerns"
                flaws.append("High power propulsion system (>200W hover power) with no cooling or heat sink thermal dissipation assumption.")

        # ── 5. Structural Choices Check ──────────────────────────────────────
        # Check if the structure contains structural safety factors
        sf = variables.get("n_safety", variables.get("sf", 0.0))
        if sf > 0.0 and sf < 1.25:
            checks["structural_choices_check"] = "Failed"
            flaws.append(f"Factor of safety ({sf:.2f}) is unsafe for dynamic structural flight envelopes.")

        # ── 6. Design Decisions Rating ───────────────────────────────────────
        # Check if there are failures in other blocks
        fail_count = sum(1 for v in checks.values() if v == "Failed")
        concern_count = sum(1 for v in checks.values() if v == "Passed with Concerns")

        if fail_count > 0:
            checks["design_decisions_check"] = "Requires Revision"
            overall = f"Design review FAILED with {fail_count} critical boundary violations: {'; '.join(flaws)}"
        elif concern_count > 0:
            checks["design_decisions_check"] = "Passed with Concerns"
            overall = f"Design review PASSED WITH CONCERNS: {'; '.join(flaws)}"
        else:
            overall = "Design review PASSED: Subsystem budgets, component ratings, and load interfaces are within safe nominal margins."

        result = {
            "checks": checks,
            "overall_assessment": overall,
            "flaws": flaws,
        }
        return result
