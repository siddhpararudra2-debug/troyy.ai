"""
Troy — Design Review Engine
Integrates the ValidationService into the Solver pipeline.
"""
from __future__ import annotations

from app.solver.engines.base import BaseEngine
from app.solver.models import SolverState, DesignReviewData
from app.validation.service import ValidationService

class DesignReviewEngine(BaseEngine):
    name = "DesignReviewEngine"

    async def _execute(self, state: SolverState) -> SolverState:
        service = ValidationService()
        report = await service.validate(state)
        
        review = DesignReviewData()
        
        for issue in report.issues:
            msg = f"[{issue.severity.upper()}] {issue.message}"
            if issue.category == "Requirements":
                review.missing_requirements.append(msg)
            elif issue.category == "Assumptions":
                review.dangerous_assumptions.append(msg)
            elif issue.category == "Safety":
                review.low_safety_margins.append(msg)
            elif issue.category == "Values":
                review.unrealistic_values.append(msg)
            else:
                review.design_weaknesses.append(msg)
                
        if report.is_approved:
            review.overall_assessment = "Design passed automated validation checks."
        else:
            review.overall_assessment = f"Design review failed with {report.total_errors} errors and {report.total_warnings} warnings."
            
        state.design_review = review
        self.logger.info(f"Design Review Complete: {review.overall_assessment}")
        return state
