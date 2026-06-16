"""
Troy — Orchestration Service
Chains together all individual services (Phases 1-10) to run the full
Engineering Solver & Reasoning Engine pipeline.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.calculations.schemas import CalculationRequest
from app.calculations.service import execute_calculation
from app.solver.models.domain_models import SolverState
from app.solver.repositories.solver_repository import SolverRepository
from app.solver.services.requirements_service import RequirementsService
from app.solver.services.assumptions_service import AssumptionsService
from app.solver.services.constraints_service import ConstraintsService
from app.solver.services.variable_service import VariableService
from app.solver.services.formula_selection_service import FormulaSelectionService
from app.solver.services.interpretation_service import InterpretationService
from app.solver.services.recommendation_service import RecommendationService
from app.solver.services.memory_service import MemoryService
from app.solver.services.documentation_service import DocumentationService
from app.validation.service import ValidationService
from app.validation.services.design_review_service import DesignReviewService
from app.validation.services.risk_assessment_service import RiskAssessmentService
from app.validation.services.approval_service import ApprovalService
from app.validation.repositories.validation_repository import ValidationRepository

logger = logging.getLogger("solver.services.orchestration")


class OrchestrationService:
    """Orchestrates the 10 phases of the Engineering Solver pipeline."""

    def __init__(self) -> None:
        self.requirements_service = RequirementsService()
        self.assumptions_service = AssumptionsService()
        self.constraints_service = ConstraintsService()
        self.variable_service = VariableService()
        self.formula_selection_service = FormulaSelectionService()
        self.interpretation_service = InterpretationService()
        self.recommendation_service = RecommendationService()
        self.memory_service = MemoryService()
        self.documentation_service = DocumentationService()

    async def solve(
        self,
        session_id: str,
        project_id: str,
        user_query: str,
        db: AsyncSession,
    ) -> SolverState:
        """
        Execute the full solver pipeline:
        1. Requirements Extraction
        2. Assumption Generation
        3. Constraint Identification
        4. Variable Extraction
        5. Formula Selection
        6. Calculation Core Execution
        7. Results Interpretation
        8. Actionable Recommendations
        9. Project Memory Persistence
        10. Report Generation & Persistence
        """
        overall_start = time.perf_counter()
        run_id = f"run_{str(uuid.uuid4())[:8]}"

        state = SolverState(
            session_id=session_id,
            project_id=project_id,
            user_query=user_query,
        )

        repo = SolverRepository(db)
        await repo.get_or_create_session(session_id, project_id, user_query)
        await repo.update_session_status(session_id, "running")

        # ── Phase 1: Requirements Extraction ─────────────────────
        try:
            start = time.perf_counter()
            state.requirements = await self.requirements_service.extract_requirements(user_query)
            state.domain = state.requirements.raw_extracted.get("domain_inferred", "multi")
            state.step_latencies_ms["RequirementsExtraction"] = (time.perf_counter() - start) * 1000
        except Exception as e:
            logger.error(f"Phase 1 (Requirements) failed: {e}")
            state.errors.append(f"Requirements: {e}")

        # ── Phase 2: Assumptions Generation ──────────────────────
        if not state.errors:
            try:
                start = time.perf_counter()
                state.assumptions = await self.assumptions_service.generate_assumptions(
                    state.domain, state.requirements
                )
                state.step_latencies_ms["AssumptionsGeneration"] = (time.perf_counter() - start) * 1000
            except Exception as e:
                logger.error(f"Phase 2 (Assumptions) failed: {e}")
                state.errors.append(f"Assumptions: {e}")

        # ── Phase 3: Constraints Identification ──────────────────
        if not state.errors:
            try:
                start = time.perf_counter()
                state.constraints = await self.constraints_service.identify_constraints(
                    state.domain, state.requirements, state.assumptions
                )
                state.step_latencies_ms["ConstraintsIdentification"] = (time.perf_counter() - start) * 1000
            except Exception as e:
                logger.error(f"Phase 3 (Constraints) failed: {e}")
                state.errors.append(f"Constraints: {e}")

        # ── Phase 4: Variable Extraction ─────────────────────────
        if not state.errors:
            try:
                start = time.perf_counter()
                state.variables = await self.variable_service.extract_variables(
                    state.domain, state.requirements, state.assumptions
                )
                state.step_latencies_ms["VariableExtraction"] = (time.perf_counter() - start) * 1000
            except Exception as e:
                logger.error(f"Phase 4 (Variables) failed: {e}")
                state.errors.append(f"Variables: {e}")

        # ── Phase 5: Formula Selection ───────────────────────────
        if not state.errors:
            try:
                start = time.perf_counter()
                state.selected_formulas = await self.formula_selection_service.select_formulas(
                    state.domain, state.variables
                )
                state.step_latencies_ms["FormulaSelection"] = (time.perf_counter() - start) * 1000
            except Exception as e:
                logger.error(f"Phase 5 (Formula Selection) failed: {e}")
                state.errors.append(f"Formulas: {e}")

        # ── Phase 6: Calculation Execution (Chained Workflow) ────
        if not state.errors and state.selected_formulas:
            try:
                start = time.perf_counter()
                await self._execute_chained_calculations(state, db)
                state.step_latencies_ms["CalculationCore"] = (time.perf_counter() - start) * 1000
            except Exception as e:
                logger.error(f"Phase 6 (Calculation Execution) failed: {e}")
                state.errors.append(f"CalculationCore: {e}")

        # ── Phase 6.5: Engineering Validation & Review ────────────
        if not state.errors:
            try:
                start_val = time.perf_counter()
                
                # 1. Run Validation
                val_service = ValidationService()
                val_issues = await val_service.validate(state)
                
                # 2. Populate state.design_review
                from app.solver.models.domain_models import DesignReviewData
                review_data = DesignReviewData()
                
                for issue in val_issues:
                    msg = f"[{issue.severity.upper()}] {issue.message}"
                    if issue.category == "Requirements":
                        review_data.missing_requirements.append(msg)
                    elif issue.category == "Assumptions":
                        review_data.dangerous_assumptions.append(msg)
                    elif issue.category == "Safety":
                        review_data.low_safety_margins.append(msg)
                    elif issue.category in ["Values", "Calculations"]:
                        review_data.unrealistic_values.append(msg)
                    else:
                        review_data.design_weaknesses.append(msg)
                
                # 3. Run Design Review board
                review_service = DesignReviewService()
                review_res = await review_service.review_design(state)
                review_data.overall_assessment = review_res["overall_assessment"]
                state.design_review = review_data
                
                # 4. Risk Assessment
                risk_service = RiskAssessmentService()
                risk_res = await risk_service.assess_risks(val_issues)
                
                # 5. Approval Decision
                approval_service = ApprovalService()
                report_mock = {
                    "total_errors": sum(1 for i in val_issues if i.severity == "error"),
                    "total_warnings": sum(1 for i in val_issues if i.severity == "warning"),
                    "issues": [i.model_dump() for i in val_issues],
                }
                approval_res = await approval_service.evaluate_approval(report_mock, risk_res, review_res)
                
                # Save validation run, review, risks, and approvals using ValidationRepository
                val_repo = ValidationRepository(db)
                val_run_id = f"val_{uuid.uuid4().hex[:8]}"
                await val_repo.save_validation_run(
                    run_id=val_run_id,
                    project_id=project_id,
                    solver_run_id=run_id,
                    domain=state.domain,
                    total_errors=report_mock["total_errors"],
                    total_warnings=report_mock["total_warnings"],
                    is_approved=report_mock["total_errors"] == 0,
                    execution_time_ms=(time.perf_counter() - start_val) * 1000,
                    issues=val_issues,
                )
                
                await val_repo.save_engineering_review(
                    review_id=f"rev_{uuid.uuid4().hex[:8]}",
                    run_id=val_run_id,
                    checks=review_res["checks"],
                    overall_assessment=review_res["overall_assessment"],
                )
                
                await val_repo.save_risk_assessment(
                    assessment_id=f"risk_{uuid.uuid4().hex[:8]}",
                    run_id=val_run_id,
                    overall_risk_level=risk_res["overall_risk_level"],
                    risks=risk_res["risks"],
                )
                
                await val_repo.save_approval_decision(
                    decision_id=f"appr_{uuid.uuid4().hex[:8]}",
                    run_id=val_run_id,
                    status=approval_res["status"],
                    engineering_reasoning=approval_res["engineering_reasoning"],
                    risk_summary=approval_res["risk_summary"],
                    validation_summary=approval_res["validation_summary"],
                )
                
                # Save to Audit Log
                await val_repo.save_audit_log(
                    log_id=f"log_{uuid.uuid4().hex[:8]}",
                    project_id=project_id,
                    action=f"Orchestration Validation Run - Decision: {approval_res['status']}",
                    user_id="orchestrator",
                    details=approval_res["engineering_reasoning"],
                )
                
                # Also save validation and approval results in Project Memory (lessons learned)
                if approval_res["status"] in ["REJECTED", "REQUIRES REVISION"]:
                    try:
                        from app.memory.schemas import MemoryCreate
                        from app.memory.service import add_memory_entry
                        
                        mem_entry = MemoryCreate(
                            project_id=project_id,
                            entry_type="decision",
                            content=f"Design validation failed for query '{user_query}' with status {approval_res['status']}. Reasoning: {approval_res['engineering_reasoning']}",
                            context=f"Failed validation run: {val_run_id}. Issues: {[{'category': i.category, 'message': i.message} for i in val_issues if i.severity == 'error']}",
                            tags=["validation_failure", state.domain],
                        )
                        await add_memory_entry(mem_entry, db)
                    except Exception as mem_ex:
                        logger.error(f"Failed to record validation failure memory: {mem_ex}")
                
                state.step_latencies_ms["EngineeringValidation"] = (time.perf_counter() - start_val) * 1000
                logger.info(f"Phase 6.5 (Engineering Validation) complete: {approval_res['status']}")
            except Exception as e:
                logger.error(f"Phase 6.5 (Engineering Validation) failed: {e}", exc_info=True)
                state.errors.append(f"ValidationEngine: {e}")

        # ── Phase 7: Interpretation ──────────────────────────────
        if not state.errors:
            try:
                start = time.perf_counter()
                state.interpretation = await self.interpretation_service.interpret_results(state)
                state.step_latencies_ms["Interpretation"] = (time.perf_counter() - start) * 1000
            except Exception as e:
                logger.error(f"Phase 7 (Interpretation) failed: {e}")
                state.errors.append(f"Interpretation: {e}")

        # ── Phase 8: Recommendations ─────────────────────────────
        if not state.errors:
            try:
                start = time.perf_counter()
                state.recommendations = await self.recommendation_service.generate_recommendations(state)
                state.step_latencies_ms["Recommendations"] = (time.perf_counter() - start) * 1000
            except Exception as e:
                logger.error(f"Phase 8 (Recommendations) failed: {e}")
                state.errors.append(f"Recommendations: {e}")

        # ── Phase 9: Memory Integration ──────────────────────────
        if not state.errors:
            try:
                start = time.perf_counter()
                await self.memory_service.save_to_memory(state, db)
                state.step_latencies_ms["MemoryPersistence"] = (time.perf_counter() - start) * 1000
            except Exception as e:
                logger.error(f"Phase 9 (Memory Persistence) failed: {e}")
                # Don't fail the entire run if memory persistence fails

        # ── Phase 10: Documentation / Report ──────────────────────
        if not state.errors:
            try:
                start = time.perf_counter()
                report_id = await self.documentation_service.generate_report(state, db)
                state.generated_report_id = report_id
                state.step_latencies_ms["ReportGeneration"] = (time.perf_counter() - start) * 1000
            except Exception as e:
                logger.error(f"Phase 10 (Report Generation) failed: {e}")
                # Don't fail the entire run if report generation fails

        # ── Final Persistence & Status update ─────────────────────
        total_time_ms = (time.perf_counter() - overall_start) * 1000
        status = "error" if state.errors else "completed"
        
        try:
            await repo.save_run(
                run_id=run_id,
                session_id=session_id,
                domain=state.domain,
                status=status,
                execution_time_ms=total_time_ms,
                error_message="; ".join(state.errors) if state.errors else None,
                state=state,
            )
            await repo.update_session_status(session_id, status)
        except Exception as e:
            logger.error(f"Failed to persist solver run record: {e}")

        logger.info(f"Solver pipeline execution finished in {total_time_ms:.2f}ms with status={status}")
        return state

    async def _execute_chained_calculations(self, state: SolverState, db: AsyncSession) -> None:
        """
        Sequentially runs selected formulas. The outputs of each formula are
        merged into the parameter pool for subsequent calculations.
        """
        # Pool to hold all currently resolved variable values
        resolved_values: Dict[str, float] = {}

        # Initialize parameter pool with variables extracted in Phase 4
        for name, data in state.variables.known.items():
            if "value" in data and data["value"] is not None:
                resolved_values[name] = float(data["value"])

        for name, data in state.variables.derived.items():
            if "value" in data and data["value"] is not None:
                resolved_values[name] = float(data["value"])

        for name, data in state.variables.constants.items():
            if "value" in data and data["value"] is not None:
                resolved_values[name] = float(data["value"])

        # Mapping dictionary to resolve symbol / alias discrepancies between different domain formulas
        # (e.g. matching 'T' in momentum theory to 'T_total' from hover thrust calculation)
        alias_map = {
            "T": "T_total",
            "m": "m_total",
            "P_hover": "P",
        }

        for select_def in state.selected_formulas:
            formula_id = select_def.formula_id
            
            # Build parameter mapping for this formula
            params: Dict[str, float] = {}
            
            # Fetch required inputs from our resolved pool
            for input_name in select_def.required_inputs:
                val = self._find_value(input_name, resolved_values, alias_map)
                if val is not None:
                    params[input_name] = val
                else:
                    logger.debug(f"Input '{input_name}' for formula '{formula_id}' not found in resolved pool. Relying on default.")

            # Run calculation
            logger.info(f"Executing formula calculation: {formula_id} with inputs: {params}")
            req = CalculationRequest(
                project_id=state.project_id,
                formula_id=formula_id,
                parameters=params,
                unit_system="SI",
            )
            
            res = await execute_calculation(req, db)
            
            if res.error:
                logger.warning(f"Formula {formula_id} returned error: {res.error}")
                state.errors.append(f"Calculation formula {formula_id}: {res.error}")
                # Continue executing other formulas anyway
                continue

            # Merge results back into the resolved pool
            for out_name, out_val in res.results.items():
                resolved_values[out_name] = float(out_val)
                state.calculation_results[out_name] = float(out_val)

    @staticmethod
    def _find_value(name: str, pool: Dict[str, float], alias_map: Dict[str, str]) -> float | None:
        """Helper to find parameter value in the pool, accounting for aliases."""
        if name in pool:
            return pool[name]
        
        # Check reverse aliases or direct alias
        if name in alias_map and alias_map[name] in pool:
            return pool[alias_map[name]]
        
        for k, v in alias_map.items():
            if v == name and k in pool:
                return pool[k]

        # Check prefixes/suffixes if there are m_payload or m_total vs m
        if name == "m":
            if "m_total" in pool:
                return pool["m_total"]
            if "m_payload" in pool:
                return pool["m_payload"]
        if name == "T":
            if "T_total" in pool:
                return pool["T_total"]

        return None
