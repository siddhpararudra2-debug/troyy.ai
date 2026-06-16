"""
Troy — Requirements Validator
Detects missing critical engineering inputs required for safe domain operations.
"""

from __future__ import annotations

from typing import List
from app.solver.models.domain_models import SolverState
from app.validation.schemas.validation_schemas import ValidationIssueSchema
from app.validation.services.base import AsyncBaseValidator


class RequirementsValidator(AsyncBaseValidator):
    """Verifies that all domain-required operational specifications have been specified."""

    name = "RequirementsValidator"

    async def validate(self, state: SolverState) -> List[ValidationIssueSchema]:
        issues: List[ValidationIssueSchema] = []
        reqs = state.requirements
        domain = (state.domain or "").lower()

        # Gather what we know from variables to avoid duplicate warnings
        known_vars = {name.lower() for name in state.variables.known.keys()}

        # Rule helper
        def add_missing(parameter: str, is_critical: bool, reason: str, recommendation: str):
            severity = "error" if is_critical else "warning"
            issues.append(
                ValidationIssueSchema(
                    severity=severity,
                    category="Requirements",
                    message=f"Missing requirement: {parameter}",
                    validator_name=self.name,
                    engineering_reasoning=reason,
                    recommendation=recommendation,
                )
            )

        # ── Domain-Specific Checks ───────────────────────────────────────────
        if domain in ["drones", "aerospace"]:
            # Drone requirements: payload, flight time, range, environment, safety factor
            has_payload = reqs.payload or "payload" in known_vars or "m_payload" in known_vars
            has_flight_time = reqs.flight_time or "flight_time" in known_vars or "t_flight" in known_vars
            has_range = "range" in known_vars or "R" in known_vars or "dist" in known_vars
            has_env = reqs.environment and reqs.environment != "Unknown"
            has_safety = reqs.safety_factor or "n_safety" in known_vars or "sf" in known_vars

            if not has_payload:
                add_missing(
                    "Payload Weight",
                    True,
                    "Payload weight directly affects the Max Takeoff Weight (MTOW) and power budgets of aerial vehicles.",
                    "Provide a payload weight parameter (e.g. m_payload = 1.5 kg).",
                )
            if not has_flight_time:
                add_missing(
                    "Flight Time",
                    True,
                    "Flight time dictates the required battery energy density and total battery capacity.",
                    "Specify a target flight time duration (e.g., flight_time = 30 min).",
                )
            if not has_range:
                add_missing(
                    "Range",
                    False,
                    "Target operating range is necessary to check datalink and energy consumption boundaries.",
                    "Specify the desired target operational range (e.g. range = 5000 m).",
                )
            if not has_env:
                add_missing(
                    "Operational Environment",
                    False,
                    "Operating altitude, temperature, and wind speed affect air density and power usage.",
                    "Describe the environment (e.g. environment = sea_level or temperature = 25C).",
                )
            if not has_safety:
                add_missing(
                    "Safety Factor",
                    True,
                    "Aerospace systems require explicit structural safety margins to comply with airworthiness rules.",
                    "Provide a design safety factor (e.g. n_safety = 1.5).",
                )

        elif domain == "robotics":
            # Robotics: payload, reach, accuracy, degrees of freedom
            has_payload = reqs.payload or "payload" in known_vars or "m_payload" in known_vars or "load" in known_vars
            has_reach = "reach" in known_vars or "L" in known_vars or "max_reach" in known_vars
            has_accuracy = "accuracy" in known_vars or "precision" in known_vars or "tol" in known_vars
            has_dof = "dof" in known_vars or "joints" in known_vars

            if not has_payload:
                add_missing(
                    "End-effector Payload Capacity",
                    True,
                    "Manipulator link lengths and joint actuators are sized based on end-effector payload loading.",
                    "Define the payload weight (e.g. payload = 5 kg).",
                )
            if not has_reach:
                add_missing(
                    "Maximum Reach Distance",
                    True,
                    "Reach determines link sizing and torque requirements at baseline joint positions.",
                    "Provide maximum manipulator reach (e.g. reach = 1.2 m).",
                )
            if not has_accuracy:
                add_missing(
                    "Positioning Accuracy / Tolerance",
                    False,
                    "Joint encoder resolution and gear backlash limits are derived from accuracy constraints.",
                    "Define required placement tolerance (e.g. accuracy = 0.5 mm).",
                )
            if not has_dof:
                add_missing(
                    "Degrees of Freedom (DoF)",
                    False,
                    "Degrees of Freedom dictate kinematics calculation methods and joint coordinate matrices.",
                    "Specify joint count or degrees of freedom (e.g. dof = 6).",
                )

        elif domain == "electronics":
            # Electronics: voltage, current, power, environment
            has_voltage = "voltage" in known_vars or "v" in known_vars or "v_in" in known_vars
            has_current = "current" in known_vars or "i" in known_vars or "i_out" in known_vars
            has_power = "power" in known_vars or "p" in known_vars or "p_max" in known_vars
            has_env = reqs.environment and reqs.environment != "Unknown"

            if not has_voltage:
                add_missing(
                    "Operating Voltage",
                    True,
                    "Voltage limits specify component dielectric breakdown thresholds and isolation gaps.",
                    "Specify the input or operating voltage (e.g. V_in = 12 V).",
                )
            if not has_current:
                add_missing(
                    "Maximum Operating Current",
                    True,
                    "Current levels determine conductor cross-sectional sizing to prevent overheating.",
                    "Specify expected current load (e.g. I_max = 5 A).",
                )
            if not has_power:
                add_missing(
                    "Power Budget / Consumption Limit",
                    False,
                    "Power dissipation limits the safe thermal operating envelope of IC and PCB designs.",
                    "Define max power consumption (e.g. power = 60 W).",
                )
            if not has_env:
                add_missing(
                    "Thermal / Operating Environment",
                    False,
                    "Ambient operating temperature dictates thermal resistance and active cooling needs.",
                    "Specify temperature limits (e.g. environment = industrial or temp_ambient = 50C).",
                )

        # Log any missing requirements list items extracted during solver phase
        if reqs.missing_requirements:
            for item in reqs.missing_requirements:
                issues.append(
                    ValidationIssueSchema(
                        severity="error",
                        category="Requirements",
                        message=f"Missing requirement: {item}",
                        validator_name=self.name,
                        engineering_reasoning="This requirement was flagged as unresolved by the initial solver parsing step.",
                        recommendation=f"Please specify the value for '{item}' in your design parameters.",
                    )
                )

        return issues
