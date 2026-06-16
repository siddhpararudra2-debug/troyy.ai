"""
Troy — Assumptions Engine Service
Generates engineering assumptions when information is missing.

Every assumption includes:
  - The gap it fills (missing_information)
  - The assumed value (assumption)
  - Why that value was chosen (reasoning)
  - A confidence score (High / Medium / Low)
  - Whether the user may override it (editable)

Performance target: <100 ms.
"""

from __future__ import annotations

import logging
from typing import List

from app.solver.models.domain_models import AssumptionData, RequirementData

logger = logging.getLogger("solver.services.assumptions")


# ── Domain-specific assumption templates ─────────────────────────
# Each entry: (missing_information, assumption, reasoning, confidence)
_COMMON_ASSUMPTIONS: List[tuple[str, str, str, str]] = [
    (
        "safety_factor",
        "1.5 minimum safety factor",
        "Industry-standard engineering margin for preliminary sizing "
        "of unmanned and general-purpose systems (FAR/CS references).",
        "High",
    ),
    (
        "environment",
        "Standard Sea Level (SSL) conditions — 15 °C, 1.225 kg/m³",
        "ISA baseline atmosphere model used for all preliminary "
        "aerodynamic and propulsion calculations.",
        "High",
    ),
]

_DRONE_ASSUMPTIONS: List[tuple[str, str, str, str]] = [
    (
        "payload",
        "0.5 kg payload",
        "Average weight of an action camera or lightweight sensor "
        "package typical for recreational / mapping drones.",
        "Medium",
    ),
    (
        "flight_time",
        "20 minutes",
        "Typical LiPo-powered multirotor hover endurance for "
        "mid-range consumer and industrial quadcopters.",
        "Medium",
    ),
    (
        "wind_conditions",
        "Calm weather — wind speed < 5 m/s",
        "Hover power estimates assume negligible crosswind component "
        "to avoid variable aerodynamic drag penalties.",
        "Medium",
    ),
    (
        "motor_count",
        "4 motors (quadcopter configuration)",
        "Quadcopter is the baseline multirotor layout offering the "
        "best balance of simplicity, redundancy, and control authority.",
        "High",
    ),
    (
        "battery_type",
        "LiPo 6S (22.2 V nominal)",
        "6S LiPo is the most common high-performance multirotor "
        "battery configuration for 3-10 kg class drones.",
        "Medium",
    ),
]

_AEROSPACE_ASSUMPTIONS: List[tuple[str, str, str, str]] = [
    (
        "wingspan",
        "2.0 m wingspan",
        "Reference dimension for small UAV / RC-scale fixed-wing aircraft.",
        "Medium",
    ),
    (
        "cruise_speed",
        "15.0 m/s cruise velocity",
        "Typical endurance speed for lightweight fixed-wing platforms.",
        "Medium",
    ),
    (
        "altitude",
        "Sea-level operation (0 m MSL)",
        "Conservative baseline — air density is highest at sea level.",
        "High",
    ),
]

_ROBOTICS_ASSUMPTIONS: List[tuple[str, str, str, str]] = [
    (
        "payload",
        "1.0 kg payload",
        "Standard test mass for tabletop manipulator arm sizing.",
        "Medium",
    ),
    (
        "joint_friction",
        "Frictionless joints (ideal)",
        "First-pass sizing ignores friction to determine minimum "
        "torque requirements before adding safety margins.",
        "Medium",
    ),
    (
        "arm_length",
        "0.5 m effective arm length",
        "Compact manipulator reach suitable for desktop or "
        "light-industrial applications.",
        "Medium",
    ),
]

_ELECTRONICS_ASSUMPTIONS: List[tuple[str, str, str, str]] = [
    (
        "input_voltage",
        "5.0 V DC supply",
        "Standard USB / logic-level voltage for microcontroller "
        "and sensor circuits.",
        "High",
    ),
    (
        "ambient_temperature",
        "25 °C ambient",
        "Standard laboratory temperature for thermal derating "
        "calculations.",
        "High",
    ),
    (
        "max_current",
        "1.0 A maximum draw",
        "Typical current budget for single-board prototypes.",
        "Medium",
    ),
]


class AssumptionsService:
    """Generates engineering assumptions for missing information."""

    async def generate_assumptions(
        self,
        domain: str,
        requirements: RequirementData,
    ) -> List[AssumptionData]:
        """
        Build a list of assumptions relevant to *domain* and the
        gaps identified in *requirements*.
        """
        assumptions: List[AssumptionData] = []
        already_filled: set[str] = set()

        # ── Common assumptions ───────────────────────────────────
        for mi, ass, reason, conf in _COMMON_ASSUMPTIONS:
            # Skip if the requirement was explicitly provided
            if mi == "safety_factor" and requirements.safety_factor:
                continue
            if mi == "environment" and requirements.environment != "Unknown":
                continue
            assumptions.append(
                AssumptionData(
                    missing_information=mi,
                    assumption=ass,
                    reasoning=reason,
                    confidence_score=conf,
                    editable=True,
                )
            )
            already_filled.add(mi)

        # ── Domain-specific assumptions ──────────────────────────
        templates = _get_domain_templates(domain)
        for mi, ass, reason, conf in templates:
            if mi in already_filled:
                continue
            # Skip assumptions whose gap is already covered by user input
            if mi == "payload" and requirements.payload:
                continue
            if mi == "flight_time" and requirements.flight_time:
                continue

            assumptions.append(
                AssumptionData(
                    missing_information=mi,
                    assumption=ass,
                    reasoning=reason,
                    confidence_score=conf,
                    editable=True,
                )
            )

        logger.info(
            f"Generated {len(assumptions)} assumptions for domain={domain}"
        )
        return assumptions


def _get_domain_templates(domain: str) -> List[tuple[str, str, str, str]]:
    """Return the assumption template list for *domain*."""
    return {
        "drones": _DRONE_ASSUMPTIONS,
        "aerospace": _AEROSPACE_ASSUMPTIONS,
        "robotics": _ROBOTICS_ASSUMPTIONS,
        "electronics": _ELECTRONICS_ASSUMPTIONS,
    }.get(domain, [])
