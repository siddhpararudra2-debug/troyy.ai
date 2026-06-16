"""
Troy — Solver API Router
Endpoints for interacting with the Engineering Solver & Reasoning Engine.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.solver.models.domain_models import (
    AssumptionData,
    ConstraintData,
    InterpretationData,
    RecommendationData,
    RequirementData,
    SolverState,
    VariableData,
)
from app.solver.repositories.solver_repository import SolverRepository
from app.solver.schemas import (
    AssumptionsRequest,
    ConstraintsRequest,
    InterpretationRequest,
    RecommendationsRequest,
    RequirementsRequest,
    SolverRequest,
    SolverResponse,
    VariablesRequest,
)
from app.solver.services.requirements_service import RequirementsService
from app.solver.services.assumptions_service import AssumptionsService
from app.solver.services.constraints_service import ConstraintsService
from app.solver.services.variable_service import VariableService
from app.solver.services.interpretation_service import InterpretationService
from app.solver.services.recommendation_service import RecommendationService
from app.solver.services.orchestration_service import OrchestrationService

router = APIRouter(prefix="/solver", tags=["solver"])


# ── Full Solve ───────────────────────────────────────────────────
@router.post("/solve", response_model=SolverResponse, status_code=status.HTTP_200_OK)
async def solve_engineering_problem(
    request: SolverRequest,
    db: AsyncSession = Depends(get_db),
):
    """Submit an engineering problem to the Reasoning Engine pipeline."""
    session_id = f"solver_{uuid.uuid4().hex[:8]}"
    
    orchestrator = OrchestrationService()
    state = await orchestrator.solve(
        session_id=session_id,
        project_id=request.project_id,
        user_query=request.user_query,
        db=db,
    )
    
    if state.errors:
        return SolverResponse(
            session_id=session_id,
            project_id=request.project_id,
            status="error",
            state=state.model_dump(),
        )
        
    return SolverResponse(
        session_id=session_id,
        project_id=request.project_id,
        status="completed",
        state=state.model_dump(),
    )


# ── Granular Endpoints ───────────────────────────────────────────
@router.post("/requirements", response_model=RequirementData, status_code=status.HTTP_200_OK)
async def extract_requirements(request: RequirementsRequest):
    """Extract structured engineering requirements from natural language."""
    service = RequirementsService()
    return await service.extract_requirements(request.user_query)


@router.post("/assumptions", response_model=List[AssumptionData], status_code=status.HTTP_200_OK)
async def generate_assumptions(request: AssumptionsRequest):
    """Generate engineering assumptions for missing requirements."""
    service = AssumptionsService()
    return await service.generate_assumptions(request.domain, request.requirements)


@router.post("/constraints", response_model=List[ConstraintData], status_code=status.HTTP_200_OK)
async def identify_constraints(request: ConstraintsRequest):
    """Identify physical, operational, and regulatory constraints."""
    service = ConstraintsService()
    return await service.identify_constraints(
        request.domain, request.requirements, request.assumptions
    )


@router.post("/variables", response_model=VariableData, status_code=status.HTTP_200_OK)
async def extract_variables(request: VariablesRequest):
    """Extract known, unknown, derived, and constant variables."""
    service = VariableService()
    return await service.extract_variables(
        request.domain, request.requirements, request.assumptions
    )


@router.post("/recommendations", response_model=RecommendationData, status_code=status.HTTP_200_OK)
async def generate_recommendations(request: RecommendationsRequest):
    """Generate actionable recommendations from calculation results."""
    service = RecommendationService()
    # Mock a minimal solver state to pass to the service
    state = SolverState(
        session_id="api_temp",
        project_id="temp",
        user_query="temp",
        domain=request.domain,
        constraints=request.constraints,
    )
    state.calculation_results = request.calculation_results
    return await service.generate_recommendations(state)


@router.post("/interpretation", response_model=InterpretationData, status_code=status.HTTP_200_OK)
async def interpret_results(request: InterpretationRequest):
    """Interpret calculation results in the context of constraints."""
    service = InterpretationService()
    # Mock a minimal solver state to pass to the service
    state = SolverState(
        session_id="api_temp",
        project_id="temp",
        user_query="temp",
        domain=request.domain,
        constraints=request.constraints,
    )
    state.calculation_results = request.calculation_results
    return await service.interpret_results(state)


# ── Session Retrieval ────────────────────────────────────────────
@router.get("/sessions/{session_id}", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def get_solver_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve the full state of a completed solver session."""
    repo = SolverRepository(db)
    session_state = await repo.get_latest_session_state(session_id)
    if not session_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solver session '{session_id}' not found.",
        )
    return session_state


@router.get("/sessions/project/{project_id}", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def list_project_sessions(project_id: str, db: AsyncSession = Depends(get_db)):
    """List solver sessions associated with a project."""
    repo = SolverRepository(db)
    return await repo.get_project_solver_history(project_id)
