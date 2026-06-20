"""
Optimization Platform — FastAPI Routes
Day 28: Optimization & Engineering Intelligence Platform

Endpoints:
  POST /optimization/run               - Full multi-phase optimization
  POST /optimization/trade-study       - AHP trade study
  POST /optimization/constraints       - Constraint solving
  POST /optimization/design-space      - Design space exploration
  POST /optimization/recommendation    - Chief engineer recommendations
  POST /optimization/iterate           - Design iteration engine
  POST /optimization/pareto            - Multi-objective Pareto front
  POST /optimization/reliability       - Reliability optimization
  POST /optimization/cost              - Cost optimization
  POST /optimization/weight            - Weight optimization
  POST /optimization/performance       - Performance optimization
  GET  /optimization/health            - Health check
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.optimization.schemas import (
    OptimizationRunRequest, OptimizationRunResponse,
    ParetoFrontRequest, ParetoFrontResponse,
    DesignSpaceRequest, DesignSpaceResponse,
    TradeStudyRequest, TradeStudyResponse,
    ConstraintSolverRequest, ConstraintSolverResponse,
    ReliabilityRequest, ReliabilityResponse,
    CostOptimizationRequest, CostOptimizationResponse,
    WeightOptimizationRequest, WeightOptimizationResponse,
    PerformanceOptimizationRequest, PerformanceOptimizationResponse,
    DesignIterationRequest, DesignIterationResponse,
    RecommendationRequest, RecommendationResponse,
)
from app.optimization.services import (
    OptimizationOrchestrator,
    MultiObjectiveOptimizer,
    DesignSpaceExplorer,
    TradeStudyEngine,
    ConstraintSolver,
    ReliabilityOptimizer,
    CostOptimizer,
    WeightOptimizer,
    PerformanceOptimizer,
    DesignIterationEngine,
    RecommendationEngine,
)

router = APIRouter(
    prefix="/optimization",
    tags=["Optimization & Engineering Intelligence — Day 28"],
)


# ── Module 1: Full Optimization Run ─────────────────────────────────────────

@router.post(
    "/run",
    response_model=OptimizationRunResponse,
    summary="Run Full Multi-Phase Optimization",
    description=(
        "Executes the complete optimization pipeline: "
        "Design Space Exploration → NSGA-II → Iteration → "
        "Constraint Validation → Reliability → Cost → Weight → "
        "Performance → Recommendations. "
        "Integrates with Day 21/22 Simulation, Day 27 Manufacturing, "
        "Day 7 Validation platforms."
    ),
)
def run_optimization(request: OptimizationRunRequest):
    """Full autonomous optimization pipeline."""
    try:
        result = OptimizationOrchestrator.run_full_optimization(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization pipeline failed: {str(e)}",
        )


# ── Module 2: Multi-Objective Optimizer ──────────────────────────────────────

@router.post(
    "/pareto",
    response_model=ParetoFrontResponse,
    summary="Generate Pareto Front (NSGA-II)",
    description=(
        "Runs NSGA-II multi-objective optimization to generate the Pareto front. "
        "Supports 2–5 objectives with constraint handling via feasibility-rule dominance. "
        "Returns hypervolume indicator, tradeoff analysis, and objective ranges."
    ),
)
def run_pareto_optimization(request: ParetoFrontRequest):
    """NSGA-II multi-objective Pareto front generation."""
    try:
        return MultiObjectiveOptimizer.optimize(request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ── Module 3: Design Space Explorer ─────────────────────────────────────────

@router.post(
    "/design-space",
    response_model=DesignSpaceResponse,
    summary="Explore Design Space",
    description=(
        "Maps the design space using Latin Hypercube Sampling (LHS) or grid/random sampling. "
        "Returns performance landscape, sensitivity indices, feasible region fraction, "
        "parameter correlations, and optimal design regions. "
        "Supports up to 10,000 samples."
    ),
)
def explore_design_space(request: DesignSpaceRequest):
    """Design space exploration with LHS sampling."""
    try:
        return DesignSpaceExplorer.explore(request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ── Module 4: Trade Study Engine ─────────────────────────────────────────────

@router.post(
    "/trade-study",
    response_model=TradeStudyResponse,
    summary="Run Engineering Trade Study",
    description=(
        "Compares 2+ design options using AHP (Analytic Hierarchy Process) "
        "and weighted decision matrix. Generates: decision matrix, criteria weights, "
        "advantages/disadvantages, risk assessments, and engineering recommendations. "
        "Typical execution time: <2 seconds."
    ),
)
def run_trade_study(request: TradeStudyRequest):
    """AHP-based engineering trade study."""
    try:
        return TradeStudyEngine.run(request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ── Module 5: Constraint Solver ───────────────────────────────────────────────

@router.post(
    "/constraints",
    response_model=ConstraintSolverResponse,
    summary="Solve & Validate Design Constraints",
    description=(
        "Evaluates a design against engineering constraints: "
        "mass, power, thermal, cost, structural, safety, dimensional, performance. "
        "Returns violation details, severity classification, penalty scores, "
        "and engineering fix suggestions. "
        "Typical execution time: <1 second."
    ),
)
def solve_constraints(request: ConstraintSolverRequest):
    """Engineering constraint satisfaction check."""
    try:
        return ConstraintSolver.solve(request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ── Module 6: Reliability Optimizer ──────────────────────────────────────────

@router.post(
    "/reliability",
    response_model=ReliabilityResponse,
    summary="Optimize Design Reliability",
    description=(
        "Monte Carlo reliability analysis using MIL-HDBK-217F failure rates. "
        "Computes: system MTBF, component reliability, FMEA, redundancy recommendations, "
        "maintenance schedule, and reliability improvement plan."
    ),
)
def optimize_reliability(request: ReliabilityRequest):
    """Monte Carlo reliability optimization."""
    try:
        return ReliabilityOptimizer.optimize(request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ── Module 7: Cost Optimizer ──────────────────────────────────────────────────

@router.post(
    "/cost",
    response_model=CostOptimizationResponse,
    summary="Optimize Design Cost",
    description=(
        "Optimizes BOM and manufacturing costs via component substitution, "
        "manufacturing process selection, volume pricing curves, and supply chain analysis. "
        "Integrates with Day 27 Manufacturing Platform schemas."
    ),
)
def optimize_cost(request: CostOptimizationRequest):
    """BOM and manufacturing cost optimization."""
    try:
        return CostOptimizer.optimize(request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ── Module 8: Weight Optimizer ────────────────────────────────────────────────

@router.post(
    "/weight",
    response_model=WeightOptimizationResponse,
    summary="Optimize Design Weight / Mass",
    description=(
        "Minimizes structural and system mass using: material substitution "
        "(Al → CFRP → Ti ranked by specific strength), topology optimization proxy, "
        "thickness reduction, and PCB mass reduction. "
        "Maintains structural safety factor throughout."
    ),
)
def optimize_weight(request: WeightOptimizationRequest):
    """Mass minimization with structural validation."""
    try:
        return WeightOptimizer.optimize(request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ── Module 9: Performance Optimizer ──────────────────────────────────────────

@router.post(
    "/performance",
    response_model=PerformanceOptimizationResponse,
    summary="Optimize Engineering Performance KPIs",
    description=(
        "Domain-aware performance optimization using physics-based models: "
        "Drone (flight time, efficiency, T/W ratio), "
        "Aerospace (L/D, range, climb rate, stall margin), "
        "Robotics (torque utilization, repeatability, cycle time), "
        "Electronics (efficiency, ripple, bandwidth, thermal). "
        "Returns per-metric improvement and performance improvement plan."
    ),
)
def optimize_performance(request: PerformanceOptimizationRequest):
    """Physics-based domain performance optimization."""
    try:
        return PerformanceOptimizer.optimize(request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ── Module 10: Design Iteration Engine ───────────────────────────────────────

@router.post(
    "/iterate",
    response_model=DesignIterationResponse,
    summary="Run Autonomous Design Iteration",
    description=(
        "Runs the autonomous design improvement loop: "
        "Generate → Simulate → Evaluate → Optimize → Modify → Repeat. "
        "Supports 10–1000+ iterations with early stopping. "
        "Returns convergence history and best design."
    ),
)
def iterate_design(request: DesignIterationRequest):
    """Autonomous design iteration with convergence tracking."""
    try:
        return DesignIterationEngine.iterate(request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ── Module 11: Recommendation Engine ─────────────────────────────────────────

@router.post(
    "/recommendation",
    response_model=RecommendationResponse,
    summary="Generate Chief Engineer Recommendations",
    description=(
        "Synthesizes all optimization results and acts as chief engineering advisor. "
        "Answers: Why was this design selected? Why rejected alternatives? "
        "What are critical tradeoffs? Major risks? Remaining improvements? "
        "Typical execution time: <1 second."
    ),
)
def get_recommendations(request: RecommendationRequest):
    """Chief engineering advisor recommendations."""
    try:
        return RecommendationEngine.recommend(request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ── Health Check ──────────────────────────────────────────────────────────────

@router.get(
    "/health",
    summary="Optimization Platform Health",
)
def optimization_health():
    """Health check for the optimization platform."""
    return {
        "status": "healthy",
        "module": "Optimization & Engineering Intelligence Platform",
        "day": 28,
        "services": [
            "OptimizationOrchestrator",
            "MultiObjectiveOptimizer (NSGA-II)",
            "DesignSpaceExplorer (LHS)",
            "TradeStudyEngine (AHP)",
            "ConstraintSolver",
            "ReliabilityOptimizer (Monte Carlo)",
            "CostOptimizer",
            "WeightOptimizer",
            "PerformanceOptimizer",
            "DesignIterationEngine",
            "RecommendationEngine",
        ],
        "integrations": [
            "Day 21/22 — Simulation Platform",
            "Day 27 — Manufacturing Platform",
            "Day 7 — Validation Platform",
        ],
    }
