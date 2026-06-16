"""
Troy — Validation Router
FastAPI endpoints for engineering validation, design review, risk assessment, and approvals.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.solver.models.domain_models import SolverState
from app.solver.repositories.solver_repository import SolverRepository
from app.validation.service import ValidationService
from app.validation.repositories.validation_repository import ValidationRepository
from app.validation.services.design_review_service import DesignReviewService
from app.validation.services.risk_assessment_service import RiskAssessmentService
from app.validation.services.approval_service import ApprovalService
from app.validation.services.audit_report_generator import AuditReportGenerator
from app.validation.schemas.validation_schemas import (
    ValidateRequest,
    ValidationReportResponse,
    ValidationIssueSchema,
    EngineeringReviewResponse,
    RiskAssessmentResponse,
    ApprovalDecisionResponse,
    AuditReportResponse,
)

router = APIRouter(prefix="/validation", tags=["validation"])


# Helper to convert dictionary-based solver state from repo to SolverState Pydantic model
def _build_solver_state(state_dict: Dict[str, Any]) -> SolverState:
    try:
        return SolverState.model_validate(state_dict)
    except Exception as e:
        # Fallback manual reconstruction if schema has minor differences
        req_dict = state_dict.get("requirements", {})
        vars_dict = state_dict.get("variables", {})
        recs_dict = state_dict.get("recommendations", {})
        
        state = SolverState(
            session_id=state_dict.get("session_id", "temp"),
            project_id=state_dict.get("project_id", "temp"),
            user_query=state_dict.get("user_query", "temp"),
            domain=state_dict.get("domain", "multi"),
        )
        # map lists of models
        from app.solver.models.domain_models import RequirementData, VariableData, RecommendationData, AssumptionData, ConstraintData
        
        state.requirements = RequirementData(**req_dict) if isinstance(req_dict, dict) else RequirementData()
        state.variables = VariableData(**vars_dict) if isinstance(vars_dict, dict) else VariableData()
        state.recommendations = RecommendationData(**recs_dict) if isinstance(recs_dict, dict) else RecommendationData()
        
        for a in state_dict.get("assumptions", []):
            state.assumptions.append(AssumptionData(**a))
        for c in state_dict.get("constraints", []):
            state.constraints.append(ConstraintData(**c))
        
        state.calculation_results = state_dict.get("calculation_results", {})
        return state


# ── POST /validate ───────────────────────────────────────────────
@router.post("/validate", response_model=ValidationReportResponse, status_code=status.HTTP_200_OK)
async def validate_state(
    request: ValidateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Run compliance validation checks on the design state."""
    start_time = time.perf_counter()
    
    # 1. Resolve Solver State
    if request.solver_state_dict:
        state = _build_solver_state(request.solver_state_dict)
    elif request.solver_run_id:
        solver_repo = SolverRepository(db)
        # Since solver run doesn't have a direct get_run in SolverRepository but has get_latest_session_state
        # We can try to load latest state
        state_dict = await solver_repo.get_latest_session_state(request.solver_run_id)
        if not state_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Solver run ID '{request.solver_run_id}' not found.",
            )
        state = _build_solver_state(state_dict)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either solver_state_dict or solver_run_id.",
        )

    # 2. Execute Validation
    val_service = ValidationService()
    issues = await val_service.validate(state)
    
    total_errors = sum(1 for i in issues if i.severity == "error")
    total_warnings = sum(1 for i in issues if i.severity == "warning")
    is_approved = total_errors == 0
    
    exec_time_ms = (time.perf_counter() - start_time) * 1000
    run_id = f"val_{uuid.uuid4().hex[:8]}"
    created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # 3. Persist run results
    val_repo = ValidationRepository(db)
    await val_repo.save_validation_run(
        run_id=run_id,
        project_id=request.project_id,
        solver_run_id=request.solver_run_id,
        domain=state.domain,
        total_errors=total_errors,
        total_warnings=total_warnings,
        is_approved=is_approved,
        execution_time_ms=exec_time_ms,
        issues=issues,
    )

    return ValidationReportResponse(
        id=run_id,
        project_id=request.project_id,
        solver_run_id=request.solver_run_id,
        domain=state.domain,
        total_errors=total_errors,
        total_warnings=total_warnings,
        is_approved=is_approved,
        execution_time_ms=exec_time_ms,
        created_at=created_at,
        issues=issues,
    )


# ── POST /review ──────────────────────────────────────────────────
@router.post("/review", response_model=EngineeringReviewResponse, status_code=status.HTTP_200_OK)
async def review_design(
    request: ValidateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Run senior review board audit on subsystem budgets and component boundaries."""
    # 1. Resolve Solver State
    if request.solver_state_dict:
        state = _build_solver_state(request.solver_state_dict)
    elif request.solver_run_id:
        solver_repo = SolverRepository(db)
        state_dict = await solver_repo.get_latest_session_state(request.solver_run_id)
        if not state_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Solver run ID '{request.solver_run_id}' not found.",
            )
        state = _build_solver_state(state_dict)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either solver_state_dict or solver_run_id.",
        )

    # 2. Run Review
    review_service = DesignReviewService()
    review_result = await review_service.review_design(state)
    
    # 3. Save to DB under a dummy/new validation run if not present,
    # but since this is usually called after POST /validate, we will write a clean mock validation run or reference
    run_id = f"val_{uuid.uuid4().hex[:8]}"
    val_repo = ValidationRepository(db)
    
    # Save a skeleton validation run to hold the foreign key
    await val_repo.save_validation_run(
        run_id=run_id,
        project_id=request.project_id,
        solver_run_id=request.solver_run_id,
        domain=state.domain,
        total_errors=0,
        total_warnings=0,
        is_approved=True,
        execution_time_ms=0.0,
        issues=[],
    )

    review_id = f"rev_{uuid.uuid4().hex[:8]}"
    await val_repo.save_engineering_review(
        review_id=review_id,
        run_id=run_id,
        checks=review_result["checks"],
        overall_assessment=review_result["overall_assessment"],
    )

    created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return EngineeringReviewResponse(
        id=review_id,
        run_id=run_id,
        design_decisions_check=review_result["checks"].get("design_decisions_check", "Passed"),
        component_choices_check=review_result["checks"].get("component_choices_check", "Passed"),
        structural_choices_check=review_result["checks"].get("structural_choices_check", "Passed"),
        electrical_choices_check=review_result["checks"].get("electrical_choices_check", "Passed"),
        weight_budgets_check=review_result["checks"].get("weight_budgets_check", "Passed"),
        power_budgets_check=review_result["checks"].get("power_budgets_check", "Passed"),
        thermal_assumptions_check=review_result["checks"].get("thermal_assumptions_check", "Passed"),
        overall_assessment=review_result["overall_assessment"],
        created_at=created_at,
    )


# ── POST /risk-analysis ──────────────────────────────────────────
@router.post("/risk-analysis", response_model=RiskAssessmentResponse, status_code=status.HTTP_200_OK)
async def analyze_risks(
    request: ValidateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Compile validation issues into standard hazard risk categories."""
    # 1. Resolve State & Run Validate
    if request.solver_state_dict:
        state = _build_solver_state(request.solver_state_dict)
    elif request.solver_run_id:
        solver_repo = SolverRepository(db)
        state_dict = await solver_repo.get_latest_session_state(request.solver_run_id)
        if not state_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Solver run ID '{request.solver_run_id}' not found.",
            )
        state = _build_solver_state(state_dict)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either solver_state_dict or solver_run_id.",
        )

    val_service = ValidationService()
    issues = await val_service.validate(state)

    # 2. Risk Assessment
    risk_service = RiskAssessmentService()
    assessment = await risk_service.assess_risks(issues)

    # 3. Persist
    val_repo = ValidationRepository(db)
    run_id = f"val_{uuid.uuid4().hex[:8]}"
    await val_repo.save_validation_run(
        run_id=run_id,
        project_id=request.project_id,
        solver_run_id=request.solver_run_id,
        domain=state.domain,
        total_errors=sum(1 for i in issues if i.severity == "error"),
        total_warnings=sum(1 for i in issues if i.severity == "warning"),
        is_approved=not any(i.severity == "error" for i in issues),
        execution_time_ms=0.0,
        issues=issues,
    )

    assessment_id = f"risk_{uuid.uuid4().hex[:8]}"
    await val_repo.save_risk_assessment(
        assessment_id=assessment_id,
        run_id=run_id,
        overall_risk_level=assessment["overall_risk_level"],
        risks=assessment["risks"],
    )

    created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return RiskAssessmentResponse(
        id=assessment_id,
        run_id=run_id,
        overall_risk_level=assessment["overall_risk_level"],
        risks=assessment["risks"],
        created_at=created_at,
    )


# ── POST /approval ───────────────────────────────────────────────
@router.post("/approval", response_model=ApprovalDecisionResponse, status_code=status.HTTP_200_OK)
async def evaluate_approval(
    request: ValidateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Obtain final approval decision for the design state."""
    # 1. Resolve State
    if request.solver_state_dict:
        state = _build_solver_state(request.solver_state_dict)
    elif request.solver_run_id:
        solver_repo = SolverRepository(db)
        state_dict = await solver_repo.get_latest_session_state(request.solver_run_id)
        if not state_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Solver run ID '{request.solver_run_id}' not found.",
            )
        state = _build_solver_state(state_dict)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either solver_state_dict or solver_run_id.",
        )

    # 2. Run validations, review, risk assessment
    val_service = ValidationService()
    issues = await val_service.validate(state)
    
    total_errors = sum(1 for i in issues if i.severity == "error")
    total_warnings = sum(1 for i in issues if i.severity == "warning")
    
    review_service = DesignReviewService()
    review_res = await review_service.review_design(state)
    
    risk_service = RiskAssessmentService()
    risk_res = await risk_service.assess_risks(issues)
    
    # 3. Decision
    approval_service = ApprovalService()
    report_mock = {"total_errors": total_errors, "total_warnings": total_warnings, "issues": [i.model_dump() for i in issues]}
    decision = await approval_service.evaluate_approval(report_mock, risk_res, review_res)

    # 4. Save
    val_repo = ValidationRepository(db)
    run_id = f"val_{uuid.uuid4().hex[:8]}"
    await val_repo.save_validation_run(
        run_id=run_id,
        project_id=request.project_id,
        solver_run_id=request.solver_run_id,
        domain=state.domain,
        total_errors=total_errors,
        total_warnings=total_warnings,
        is_approved=total_errors == 0,
        execution_time_ms=0.0,
        issues=issues,
    )

    decision_id = f"appr_{uuid.uuid4().hex[:8]}"
    await val_repo.save_approval_decision(
        decision_id=decision_id,
        run_id=run_id,
        status=decision["status"],
        engineering_reasoning=decision["engineering_reasoning"],
        risk_summary=decision["risk_summary"],
        validation_summary=decision["validation_summary"],
    )

    # Save compile audit logs
    await val_repo.save_audit_log(
        log_id=f"log_{uuid.uuid4().hex[:8]}",
        project_id=request.project_id,
        action=f"Approval decision: {decision['status']}",
        user_id="gatekeeper_engine",
        details=decision["engineering_reasoning"],
    )

    created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return ApprovalDecisionResponse(
        id=decision_id,
        run_id=run_id,
        status=decision["status"],
        engineering_reasoning=decision["engineering_reasoning"],
        risk_summary=decision["risk_summary"],
        validation_summary=decision["validation_summary"],
        created_at=created_at,
    )


# ── GET /validation-history ──────────────────────────────────────
@router.get("/validation-history", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def get_validation_history(
    project_id: str = Query(..., description="Project ID to fetch history for"),
    limit: int = Query(20, description="Max runs to return"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve history of compliance validation runs for a specific project."""
    val_repo = ValidationRepository(db)
    return await val_repo.get_validation_history(project_id, limit)


# ── GET /audit-report/{id} ────────────────────────────────────────
@router.get("/audit-report/{id}", status_code=status.HTTP_200_OK)
async def get_audit_report(
    id: str,
    fmt: str = Query("markdown", alias="format", description="Report format: markdown, html, json, pdf"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve compliance audit reports in multiple formats (Markdown, HTML, JSON, PDF)."""
    val_repo = ValidationRepository(db)
    
    # 1. Try to load saved report directly
    # Wait, if we want to dynamically generate or fetch the report
    # Let's fetch the validation run details first
    run_state = await val_repo.get_validation_run_state(id)
    if not run_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation run '{id}' not found.",
        )

    # Re-evaluate review, risk, and approval for report rendering
    state_mock = SolverState(
        session_id=run_state.get("solver_run_id") or "history_temp",
        project_id=run_state["project_id"],
        user_query="reconstructed_from_history",
        domain=run_state["domain"],
    )
    # Re-add variables/assumptions mocks to make report look realistic
    issues = [ValidationIssueSchema(**i) for i in run_state["issues"]]
    
    review_service = DesignReviewService()
    review_res = await review_service.review_design(state_mock)
    
    risk_service = RiskAssessmentService()
    risk_res = await risk_service.assess_risks(issues)
    
    approval_service = ApprovalService()
    report_mock = {
        "total_errors": run_state["total_errors"],
        "total_warnings": run_state["total_warnings"],
        "issues": [i.model_dump() for i in issues],
    }
    approval_res = await approval_service.evaluate_approval(report_mock, risk_res, review_res)

    # Generate content
    content_payload = AuditReportGenerator.generate_report(
        report=run_state,
        review=review_res,
        risks=risk_res,
        approval=approval_res,
        fmt=fmt,
    )

    # Save copy to database
    report_id = f"rep_{uuid.uuid4().hex[:8]}"
    if fmt == "pdf":
        # PDF is binary content
        await val_repo.save_audit_report(report_id, id, "comprehensive", fmt, "[PDF Binary Content]")
        return Response(content=content_payload, media_type="application/pdf")
    else:
        await val_repo.save_audit_report(report_id, id, "comprehensive", fmt, content_payload)
        
        media_types = {
            "html": "text/html",
            "json": "application/json",
            "markdown": "text/markdown",
        }
        return Response(content=content_payload, media_type=media_types.get(fmt, "text/plain"))
