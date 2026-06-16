"""
Troy — Constraint Identification Service
Identifies physical, operational, and regulatory engineering constraints
for a given domain and set of requirements / assumptions.

Supported constraint categories:
  - Weight limits
  - Power limits
  - Structural / thrust limits
  - Battery / energy limits
  - Thermal limits
  - Mechanical limits
"""

from __future__ import annotations

import logging
import re
from typing import List, Optional

from app.solver.models.domain_models import (
    AssumptionData,
    ConstraintData,
    RequirementData,
)

logger = logging.getLogger("solver.services.constraints")


class ConstraintsService:
    """Identifies engineering constraints from requirements and assumptions."""

    async def identify_constraints(
        self,
        domain: str,
        requirements: RequirementData,
        assumptions: List[AssumptionData],
    ) -> List[ConstraintData]:
        """
        Return a list of ``ConstraintData`` objects describing the
        physical / operational bounds for the problem.
        """
        constraints: List[ConstraintData] = []

        # ── Resolve key numeric values ───────────────────────────
        payload_kg = self._resolve_payload_kg(requirements, assumptions)
        safety_factor = self._resolve_safety_factor(requirements, assumptions)

        # ── Domain-specific constraint identification ─────────────
        if domain == "drones":
            constraints.extend(
                self._drone_constraints(payload_kg, safety_factor, requirements)
            )
        elif domain == "aerospace":
            constraints.extend(
                self._aerospace_constraints(payload_kg, safety_factor)
            )
        elif domain == "robotics":
            constraints.extend(
                self._robotics_constraints(payload_kg, safety_factor)
            )
        elif domain == "electronics":
            constraints.extend(self._electronics_constraints())

        # ── Universal physics constraints ─────────────────────────
        constraints.append(
            ConstraintData(
                category="Physical limits",
                limit="All computed values must be non-negative",
                source="Fundamental physics — negative mass/thrust/power is non-physical.",
            )
        )

        logger.info(f"Identified {len(constraints)} constraints for domain={domain}")
        return constraints

    # ── Drone constraints ────────────────────────────────────────
    @staticmethod
    def _drone_constraints(
        payload_kg: float,
        safety_factor: float,
        requirements: RequirementData,
    ) -> List[ConstraintData]:
        result: List[ConstraintData] = []

        # 1. Weight limit — MTOW ≈ 3.5 × payload
        mtow = payload_kg * 3.5
        if mtow > 0:
            result.append(
                ConstraintData(
                    category="Weight limits",
                    limit=f"Max Takeoff Weight (MTOW) <= {mtow:.2f} kg",
                    source="Payload-to-MTOW ratio heuristic (typical 25-30 % payload fraction).",
                )
            )

        # 2. Battery energy density
        result.append(
            ConstraintData(
                category="Battery limits",
                limit="Battery energy density >= 150 Wh/kg (LiPo minimum)",
                source="Required to achieve practical multirotor endurance targets.",
            )
        )

        # 3. Thrust requirement
        if mtow > 0:
            thrust_req = mtow * 9.80665 * safety_factor
            result.append(
                ConstraintData(
                    category="Structural/Thrust limits",
                    limit=f"Total system thrust >= {thrust_req:.2f} N",
                    source=f"Weight × g × safety factor ({safety_factor}) for hover + margin.",
                )
            )

        # 4. Motor count
        result.append(
            ConstraintData(
                category="Mechanical limits",
                limit="Minimum 4 motors for multirotor stability",
                source="Quadcopter is minimum viable rotor count for yaw control.",
            )
        )

        return result

    # ── Aerospace constraints ────────────────────────────────────
    @staticmethod
    def _aerospace_constraints(
        payload_kg: float,
        safety_factor: float,
    ) -> List[ConstraintData]:
        result: List[ConstraintData] = []

        result.append(
            ConstraintData(
                category="Structural limits",
                limit="Max wing loading <= 100 N/m²",
                source="Structural limits of composite / balsa constructions.",
            )
        )
        result.append(
            ConstraintData(
                category="Power limits",
                limit="Power-to-weight ratio >= 150 W/kg for adequate climb rate",
                source="Minimum power margin for stall recovery and climb.",
            )
        )
        if payload_kg > 0:
            max_weight = payload_kg * 4.0 * 9.80665
            result.append(
                ConstraintData(
                    category="Weight limits",
                    limit=f"Max gross weight <= {max_weight:.2f} N",
                    source="Structural sizing using 25 % payload fraction.",
                )
            )

        return result

    # ── Robotics constraints ─────────────────────────────────────
    @staticmethod
    def _robotics_constraints(
        payload_kg: float,
        safety_factor: float,
    ) -> List[ConstraintData]:
        result: List[ConstraintData] = []
        arm_length = 0.5  # default assumed
        torque_limit = payload_kg * 9.80665 * arm_length * safety_factor

        result.append(
            ConstraintData(
                category="Mechanical limits",
                limit=f"Joint 1 peak torque <= {torque_limit:.2f} Nm",
                source=f"Payload ({payload_kg} kg) × g × arm ({arm_length} m) × SF ({safety_factor}).",
            )
        )
        result.append(
            ConstraintData(
                category="Power limits",
                limit="Servo / stepper stall current <= rated driver capacity",
                source="Driver IC current rating must not be exceeded.",
            )
        )

        return result

    # ── Electronics constraints ──────────────────────────────────
    @staticmethod
    def _electronics_constraints() -> List[ConstraintData]:
        return [
            ConstraintData(
                category="Thermal limits",
                limit="Junction temperature < 125 °C",
                source="Standard silicon operating limit (commercial grade).",
            ),
            ConstraintData(
                category="Power limits",
                limit="Total power dissipation <= 5 W (passive cooling)",
                source="Max passive heatsink thermal dissipation for TO-220 / SOT packages.",
            ),
            ConstraintData(
                category="Electrical limits",
                limit="Trace current density <= 30 A/mm² (1 oz copper)",
                source="IPC-2221 PCB trace current capacity guidelines.",
            ),
        ]

    # ── Value resolution helpers ─────────────────────────────────
    @staticmethod
    def _resolve_payload_kg(
        requirements: RequirementData,
        assumptions: List[AssumptionData],
    ) -> float:
        """Extract a numeric payload in kg from requirements or assumptions."""
        source = requirements.payload
        if not source:
            for a in assumptions:
                if a.missing_information == "payload":
                    source = a.user_override or a.assumption
                    break
        if not source:
            return 0.5  # hard default

        match = re.search(r"([\d\.]+)", source)
        if not match:
            return 0.5
        val = float(match.group(1))
        lower = source.lower()
        if "g" in lower and "kg" not in lower:
            val /= 1000.0
        elif "lb" in lower:
            val *= 0.453592
        return val

    @staticmethod
    def _resolve_safety_factor(
        requirements: RequirementData,
        assumptions: List[AssumptionData],
    ) -> float:
        """Extract the safety factor from requirements or assumptions."""
        source = requirements.safety_factor
        if not source:
            for a in assumptions:
                if a.missing_information == "safety_factor":
                    source = a.user_override or a.assumption
                    break
        if not source:
            return 1.5

        match = re.search(r"([\d\.]+)", source)
        return float(match.group(1)) if match else 1.5
