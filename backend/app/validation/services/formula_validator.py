"""
Troy — Formula Validator
Checks that selected engineering formulas match the target domain, meet applicability boundaries, and have satisfied variables.
"""

from __future__ import annotations

from typing import List
from app.solver.models.domain_models import SolverState
from app.validation.schemas.validation_schemas import ValidationIssueSchema
from app.validation.services.base import AsyncBaseValidator


class FormulaValidator(AsyncBaseValidator):
    """Verifies formula scope limitations, domain alignments, and input variable completeness."""

    name = "FormulaValidator"

    async def validate(self, state: SolverState) -> List[ValidationIssueSchema]:
        issues: List[ValidationIssueSchema] = []
        domain = (state.domain or "").lower()

        # Build a set of all variables defined in the state
        available_vars = set()
        for name in state.variables.known.keys():
            available_vars.add(name.lower())
        for name in state.variables.derived.keys():
            available_vars.add(name.lower())
        for name in state.variables.constants.keys():
            available_vars.add(name.lower())

        for f in state.selected_formulas:
            formula_id = f.formula_id
            fid_lower = formula_id.lower()

            # ── 1. Check Parameter Dependency Satisfaction ───────────────────
            missing_inputs = []
            for req_input in f.required_inputs:
                if req_input.lower() not in available_vars:
                    # Check common aliases
                    aliases = [req_input.lower(), f"m_{req_input.lower()}", f"t_{req_input.lower()}"]
                    if not any(a in available_vars for a in aliases):
                        missing_inputs.append(req_input)

            if missing_inputs:
                issues.append(
                    ValidationIssueSchema(
                        severity="error",
                        category="Formulas",
                        message=f"Formula '{f.name}' ({formula_id}) missing inputs: {', '.join(missing_inputs)}",
                        validator_name=self.name,
                        engineering_reasoning=f"The selected formula requires variables {f.required_inputs} to compute outputs {f.expected_outputs}.",
                        recommendation=f"Add values for the missing inputs: {missing_inputs} to design variables.",
                    )
                )

            # ── 2. Check Domain Compatibility ─────────────────────────────────
            # Basic check: do formula naming or metadata align with the solver domain?
            is_aero_formula = "aero" in fid_lower or "thrust" in fid_lower or "prop" in fid_lower or "wing" in fid_lower or "lift" in fid_lower or "drag" in fid_lower
            is_elec_formula = "circuit" in fid_lower or "ohm" in fid_lower or "battery" in fid_lower or "power" in fid_lower or "resistor" in fid_lower or "voltage" in fid_lower
            is_robot_formula = "kinematics" in fid_lower or "torque" in fid_lower or "dof" in fid_lower or "joint" in fid_lower or "link" in fid_lower

            if domain == "electronics" and is_aero_formula:
                issues.append(
                    ValidationIssueSchema(
                        severity="warning",
                        category="Formulas",
                        message=f"Domain mismatch for formula '{f.name}': Aerodynamics formula selected in Electronics domain.",
                        validator_name=self.name,
                        engineering_reasoning="Aerodynamics formulas are generally not applicable to solid-state electrical circuits.",
                        recommendation="Review if an electronic thermal dissipation or electrical current formula should be used instead.",
                    )
                )
            elif domain == "drones" and is_robot_formula and "torque" not in fid_lower:
                issues.append(
                    ValidationIssueSchema(
                        severity="info",
                        category="Formulas",
                        message=f"Multi-domain reference: Robotic arm kinematics formula selected in Drone domain.",
                        validator_name=self.name,
                        engineering_reasoning="This might be acceptable if the drone has an onboard manipulator arm.",
                        recommendation="Verify that the robotic kinematics applies to a subsystem and not flight dynamics.",
                    )
                )

            # ── 3. Check Formula Applicability and Limitations ───────────────
            if "momentum" in fid_lower or "hover_thrust" in fid_lower:
                issues.append(
                    ValidationIssueSchema(
                        severity="info",
                        category="Formulas",
                        message=f"Formula limitation: Momentum Theory hover estimation has limited scope.",
                        validator_name=self.name,
                        engineering_reasoning="Momentum theory provides a theoretical upper-bound limit. It ignores 3D flow tip losses, blade twist, and ground effect.",
                        recommendation="Valid for concept design. For detailed flight certification, transition to Blade Element Momentum (BEM) or CFD simulation.",
                    )
                )

            elif "battery" in fid_lower or "discharge" in fid_lower:
                issues.append(
                    ValidationIssueSchema(
                        severity="warning",
                        category="Formulas",
                        message=f"Formula limitation: Simple capacity-divided-by-current battery model selected.",
                        validator_name=self.name,
                        engineering_reasoning="Simple discharge models ignore Peukert's effect (capacity decreases at higher discharge rates) and voltage sag.",
                        recommendation="Apply a discharge rate derating factor (e.g. 0.85) to represent battery energy capability under heavy loads.",
                    )
                )

            elif "euler" in fid_lower or "beam" in fid_lower:
                issues.append(
                    ValidationIssueSchema(
                        severity="info",
                        category="Formulas",
                        message=f"Formula limitation: Static Euler-Bernoulli beam theory.",
                        validator_name=self.name,
                        engineering_reasoning="Neglects shear deformations (Timonshenko correction) and dynamic resonance peaks under cyclic loading.",
                        recommendation="Use for primary structural sizing, but perform FEA vibration analysis for dynamic environments.",
                    )
                )

        return issues
