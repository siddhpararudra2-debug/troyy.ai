"""
Troy — Variable Extraction Service
Converts requirements and assumptions into structured engineering
variables — known, unknown, derived, and physical constants.

Performance target: <100 ms.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from app.solver.models.domain_models import (
    AssumptionData,
    RequirementData,
    VariableData,
)

logger = logging.getLogger("solver.services.variables")


class VariableService:
    """Transforms requirements + assumptions into a VariableData map."""

    async def extract_variables(
        self,
        domain: str,
        requirements: RequirementData,
        assumptions: List[AssumptionData],
    ) -> VariableData:
        """
        Build a ``VariableData`` object containing known values,
        unknowns to be solved, derived parameters, and physical
        constants relevant to *domain*.
        """
        known: Dict[str, Any] = {}
        unknown: List[str] = []
        dependent: List[str] = []
        derived: Dict[str, Any] = {}
        constants: Dict[str, Any] = {
            "g": {
                "value": 9.80665,
                "unit": "m/s²",
                "description": "Gravitational acceleration",
            },
            "rho": {
                "value": 1.225,
                "unit": "kg/m³",
                "description": "Standard sea-level air density",
            },
        }

        # ── Parse payload → known ────────────────────────────────
        payload_kg = self._parse_mass(requirements.payload, assumptions, "payload")
        if payload_kg is not None:
            known["m_payload"] = {
                "value": payload_kg,
                "unit": "kg",
                "description": "Payload mass",
            }

        # ── Parse endurance → known ──────────────────────────────
        endurance_min = self._parse_time(requirements.flight_time, assumptions, "flight_time")
        if endurance_min is not None:
            known["t_endurance"] = {
                "value": endurance_min,
                "unit": "minutes",
                "description": "Target flight time / endurance",
            }

        # ── Parse safety factor → known ──────────────────────────
        sf = self._parse_scalar(requirements.safety_factor, assumptions, "safety_factor")
        if sf is not None:
            known["f_safety"] = {
                "value": sf,
                "unit": "dimensionless",
                "description": "Safety factor",
            }
        else:
            known["f_safety"] = {
                "value": 1.5,
                "unit": "dimensionless",
                "description": "Safety factor (assumed)",
            }

        # ── Domain-specific variables ────────────────────────────
        if domain == "drones":
            self._extract_drone_variables(known, unknown, dependent, derived, constants)
        elif domain == "aerospace":
            self._extract_aerospace_variables(known, unknown, dependent, derived, constants)
        elif domain == "robotics":
            self._extract_robotics_variables(known, unknown, dependent, derived, constants)
        elif domain == "electronics":
            self._extract_electronics_variables(known, unknown, dependent, derived, constants)

        result = VariableData(
            known=known,
            unknown=unknown,
            dependent=dependent,
            derived=derived,
            constants=constants,
        )
        logger.info(
            f"Variables: {len(known)} known, {len(unknown)} unknown, "
            f"{len(derived)} derived, {len(constants)} constants"
        )
        return result

    # ── Drone variables ──────────────────────────────────────────
    @staticmethod
    def _extract_drone_variables(
        known: Dict, unknown: List, dependent: List,
        derived: Dict, constants: Dict,
    ) -> None:
        unknown.extend(["T_motor", "T_motor_g", "T_total", "P", "v_i", "disc_loading"])
        dependent.extend(["Battery capacity", "Motor Kv", "Propeller diameter"])

        payload_kg = known.get("m_payload", {}).get("value", 0.5)
        m_total = payload_kg * 3.5
        sf = known.get("f_safety", {}).get("value", 1.5)

        derived["m"] = {
            "value": m_total,
            "unit": "kg",
            "description": "Estimated all-up weight (AUW) — 3.5× payload",
        }
        derived["n"] = {
            "value": 4.0,
            "unit": "-",
            "description": "Number of motors",
        }
        # Rotor disc area: assume 10″ prop ≈ 0.254 m diameter each
        prop_diam = 0.254
        single_area = 3.14159 * (prop_diam / 2) ** 2
        total_area = single_area * 4
        derived["A"] = {
            "value": round(total_area, 6),
            "unit": "m²",
            "description": "Total rotor disc area (4 × 10″ props)",
        }
        # Battery defaults for flight-time formula
        derived["capacity_mah"] = {
            "value": 5000.0,
            "unit": "mAh",
            "description": "Assumed battery capacity",
        }
        derived["voltage"] = {
            "value": 22.2,
            "unit": "V",
            "description": "Assumed battery voltage (6S LiPo nominal)",
        }
        derived["eta"] = {
            "value": 0.8,
            "unit": "-",
            "description": "Battery discharge efficiency",
        }

    # ── Aerospace variables ──────────────────────────────────────
    @staticmethod
    def _extract_aerospace_variables(
        known: Dict, unknown: List, dependent: List,
        derived: Dict, constants: Dict,
    ) -> None:
        unknown.extend(["L", "D", "C_D"])
        dependent.extend(["Stall speed", "Endurance speed"])

        derived["S"] = {"value": 0.5, "unit": "m²", "description": "Wing area"}
        derived["v"] = {"value": 15.0, "unit": "m/s", "description": "Cruise velocity"}
        derived["C_L"] = {"value": 0.6, "unit": "-", "description": "Lift coefficient"}

    # ── Robotics variables ───────────────────────────────────────
    @staticmethod
    def _extract_robotics_variables(
        known: Dict, unknown: List, dependent: List,
        derived: Dict, constants: Dict,
    ) -> None:
        unknown.extend(["torque_req", "power_req"])
        dependent.extend(["Motor selection", "Gear ratio"])

        derived["arm_length"] = {
            "value": 0.5,
            "unit": "m",
            "description": "Effective arm / link length",
        }

    # ── Electronics variables ────────────────────────────────────
    @staticmethod
    def _extract_electronics_variables(
        known: Dict, unknown: List, dependent: List,
        derived: Dict, constants: Dict,
    ) -> None:
        unknown.extend(["I", "P", "V_drop"])
        dependent.extend(["Heat sink sizing", "Trace width"])

        derived["V"] = {"value": 5.0, "unit": "V", "description": "Supply voltage"}
        derived["R"] = {"value": 10.0, "unit": "Ω", "description": "Load resistance"}

    # ── Parsing helpers ──────────────────────────────────────────
    @staticmethod
    def _parse_mass(
        raw: Optional[str],
        assumptions: List[AssumptionData],
        assumption_key: str,
    ) -> Optional[float]:
        source = raw
        if not source:
            for a in assumptions:
                if a.missing_information == assumption_key:
                    source = a.user_override or a.assumption
                    break
        if not source:
            return None
        match = re.search(r"([\d\.]+)", source)
        if not match:
            return None
        val = float(match.group(1))
        lower = source.lower()
        if "g" in lower and "kg" not in lower:
            val /= 1000.0
        elif "lb" in lower:
            val *= 0.453592
        return val

    @staticmethod
    def _parse_time(
        raw: Optional[str],
        assumptions: List[AssumptionData],
        assumption_key: str,
    ) -> Optional[float]:
        source = raw
        if not source:
            for a in assumptions:
                if a.missing_information == assumption_key:
                    source = a.user_override or a.assumption
                    break
        if not source:
            return None
        match = re.search(r"([\d\.]+)", source)
        if not match:
            return None
        val = float(match.group(1))
        lower = source.lower()
        if "hr" in lower or "hour" in lower:
            val *= 60.0
        return val

    @staticmethod
    def _parse_scalar(
        raw: Optional[str],
        assumptions: List[AssumptionData],
        assumption_key: str,
    ) -> Optional[float]:
        source = raw
        if not source:
            for a in assumptions:
                if a.missing_information == assumption_key:
                    source = a.user_override or a.assumption
                    break
        if not source:
            return None
        match = re.search(r"([\d\.]+)", source)
        return float(match.group(1)) if match else None
