"""
Troy — Requirements Extraction Service
Converts natural language engineering requests into structured
RequirementData objects.

Performance target: <100 ms per extraction.

Supported domains:
  - Drones / UAVs
  - Aerospace / Aerodynamics
  - Robotics / Kinematics
  - Electronics / Circuit Analysis
"""

from __future__ import annotations

import logging
import re
from typing import List, Optional, Tuple

from app.solver.models.domain_models import RequirementData

logger = logging.getLogger("solver.services.requirements")


# ── Domain keyword mappings ──────────────────────────────────────
_DOMAIN_KEYWORDS: dict[str, List[str]] = {
    "drones": [
        "drone", "quadcopter", "uav", "multirotor", "hexacopter",
        "octocopter", "fpv", "rotorcraft", "copter",
    ],
    "aerospace": [
        "wing", "aircraft", "airplane", "aerodynamic", "aerofoil",
        "airfoil", "lift", "fuselage", "glider",
    ],
    "robotics": [
        "robot", "arm", "joint", "torque", "kinematics", "actuator",
        "servo", "gripper", "manipulator", "dof",
    ],
    "electronics": [
        "circuit", "pcb", "voltage", "current", "resistor", "ohm",
        "ampere", "capacitor", "inductor", "transistor", "mosfet",
    ],
}

_MISSION_KEYWORDS: List[str] = [
    "surveillance", "racing", "delivery", "inspection",
    "military", "commercial", "mapping", "photography",
    "agriculture", "search and rescue",
]

# ── Numeric extraction patterns ──────────────────────────────────
_PAYLOAD_PATTERNS = [
    re.compile(
        r"(?:carry|carrying|carries|payload|load)\s+(?:of\s+)?"
        r"([\d\.]+)\s*(kg|g|lbs?|pounds?)",
        re.IGNORECASE,
    ),
    re.compile(
        r"([\d\.]+)\s*(kg|g|lbs?|pounds?)\s+(?:payload|load|cargo)",
        re.IGNORECASE,
    ),
]

_TIME_PATTERNS = [
    re.compile(
        r"(?:for|endurance|time|duration|flight\s*time)\s+(?:of\s+)?"
        r"([\d\.]+)\s*(minutes?|mins?|hours?|hrs?|seconds?|secs?|s)",
        re.IGNORECASE,
    ),
    re.compile(
        r"([\d\.]+)\s*(minutes?|mins?|hours?|hrs?)\s+(?:flight|endurance|hover)",
        re.IGNORECASE,
    ),
]

_RANGE_PATTERNS = [
    re.compile(
        r"(?:range|distance|radius)\s+(?:of\s+)?([\d\.]+)\s*(km|m|mi|miles?|ft|feet)",
        re.IGNORECASE,
    ),
]

_SPEED_PATTERNS = [
    re.compile(
        r"(?:speed|velocity)\s+(?:of\s+)?([\d\.]+)\s*(m/s|km/h|mph|kts?|knots?)",
        re.IGNORECASE,
    ),
]

_ALTITUDE_PATTERNS = [
    re.compile(
        r"(?:altitude|height|ceiling)\s+(?:of\s+)?([\d\.]+)\s*(m|ft|feet|km)",
        re.IGNORECASE,
    ),
]


class RequirementsService:
    """Extracts structured engineering requirements from user queries."""

    async def extract_requirements(self, user_query: str) -> RequirementData:
        """
        Parse *user_query* and return a ``RequirementData`` object.

        The method uses compiled regex patterns so that extraction stays
        well under the 100 ms budget even for long queries.
        """
        query = user_query.strip()
        query_lower = query.lower()

        # ── Domain detection ─────────────────────────────────────
        domain = self._detect_domain(query_lower)

        # ── Project type ─────────────────────────────────────────
        project_type = {
            "drones": "drone",
            "aerospace": "aircraft",
            "robotics": "robot",
            "electronics": "circuit",
        }.get(domain, "general")

        # ── Mission type ─────────────────────────────────────────
        mission_type = self._detect_mission(query_lower)

        # ── Numeric extractions ──────────────────────────────────
        payload = self._extract_first(query, _PAYLOAD_PATTERNS)
        flight_time = self._extract_first(query, _TIME_PATTERNS)
        range_val = self._extract_first(query, _RANGE_PATTERNS)
        speed_val = self._extract_first(query, _SPEED_PATTERNS)
        altitude_val = self._extract_first(query, _ALTITUDE_PATTERNS)

        # ── Missing requirements ─────────────────────────────────
        missing = self._identify_missing(
            domain, payload, flight_time, range_val, speed_val, altitude_val
        )

        raw_extracted = {
            "domain_inferred": domain,
            "range": range_val,
            "speed": speed_val,
            "altitude": altitude_val,
        }

        result = RequirementData(
            project_type=project_type,
            mission_type=mission_type,
            payload=payload,
            flight_time=flight_time,
            environment="Unknown",
            safety_factor=None,
            missing_requirements=missing,
            raw_extracted=raw_extracted,
        )

        logger.info(
            f"Extracted requirements: domain={domain} "
            f"mission={mission_type} payload={payload} "
            f"flight_time={flight_time} missing={len(missing)}"
        )
        return result

    # ── Private helpers ───────────────────────────────────────────

    @staticmethod
    def _detect_domain(query_lower: str) -> str:
        """Return the best-matching domain or 'multi'."""
        scores: dict[str, int] = {}
        for domain, keywords in _DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                scores[domain] = score
        if not scores:
            return "multi"
        return max(scores, key=scores.get)  # type: ignore[arg-type]

    @staticmethod
    def _detect_mission(query_lower: str) -> str:
        """Return the first matching mission keyword or 'general'."""
        for m in _MISSION_KEYWORDS:
            if m in query_lower:
                return m
        return "general"

    @staticmethod
    def _extract_first(
        text_input: str,
        patterns: List[re.Pattern[str]],
    ) -> Optional[str]:
        """Return the first match from a list of compiled regex patterns."""
        for pat in patterns:
            match = pat.search(text_input)
            if match:
                return f"{match.group(1)}{match.group(2)}"
        return None

    @staticmethod
    def _identify_missing(
        domain: str,
        payload: Optional[str],
        flight_time: Optional[str],
        range_val: Optional[str],
        speed_val: Optional[str],
        altitude_val: Optional[str],
    ) -> List[str]:
        """Determine which requirements are still unspecified."""
        missing: List[str] = []

        if domain in ("drones", "aerospace"):
            if not payload:
                missing.append("payload")
            if not flight_time:
                missing.append("flight_time")
            if not range_val:
                missing.append("range")
            if not altitude_val:
                missing.append("altitude")
            missing.append("environment")
            missing.append("safety_factor")

        elif domain == "robotics":
            if not payload:
                missing.append("payload")
            missing.extend(["dof", "joint_count", "reach", "safety_factor"])

        elif domain == "electronics":
            missing.extend([
                "input_voltage", "max_current", "operating_temp", "safety_factor"
            ])

        else:
            missing.append("safety_factor")

        return missing
