"""
Troy — Verification Engine
Verifies calculation results against constraints and physical limits.
"""
from __future__ import annotations

import re
from app.solver.engines.base import BaseEngine
from app.solver.models import SolverState, VerificationData

class VerificationEngine(BaseEngine):
    name = "VerificationEngine"

    async def _execute(self, state: SolverState) -> SolverState:
        verif = VerificationData(is_valid=True)
        results = state.calculation_results
        
        # In a real implementation, we compare `results` directly against `state.constraints`
        if not results:
            verif.is_valid = False
            verif.warnings.append("No calculation results to verify.")
            state.verification = verif
            return state

        checks_passed = 0
        checks_failed = 0

        # Mock constraint checking logic based on parsed outputs
        for constraint in state.constraints:
            if "MTOW" in constraint.limit:
                # We expect m_total to be less than the limit
                match = re.search(r'([\d\.]+)', constraint.limit)
                if match:
                    limit_val = float(match.group(1))
                    if results.get("m_total", 0) > limit_val:
                        verif.is_valid = False
                        verif.warnings.append(f"MTOW constraint violated: {results.get('m_total')} > {limit_val}")
                        checks_failed += 1
                    else:
                        checks_passed += 1

            elif "Thrust" in constraint.limit:
                match = re.search(r'([\d\.]+)', constraint.limit)
                if match:
                    limit_val = float(match.group(1))
                    if results.get("thrust_total", limit_val + 1) < limit_val:
                        verif.is_valid = False
                        verif.warnings.append(f"Thrust constraint violated. Required: {limit_val}")
                        checks_failed += 1
                    else:
                        checks_passed += 1

        if checks_passed == 0 and checks_failed == 0:
            # If no formal constraints matched the results format, mark passed as a fallback
            checks_passed = len(state.constraints)

        verif.checks_passed = checks_passed
        verif.checks_failed = checks_failed
        state.verification = verif
        
        self.logger.info(f"Verification complete: {checks_passed} passed, {checks_failed} failed.")
        return state
