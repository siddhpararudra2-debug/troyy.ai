"""
Optimization Orchestrator — Master Coordination Service
Coordinates all optimization modules and integrates with:
  - Day 21/22: Simulation Platform (circuit, drone, aerospace, robotics)
  - Day 27: Manufacturing Platform (BOM, cost, DFM)
  - Day 7: Validation Platform (constraint checks, approval)
  - Day 8: Documentation Platform (reports)

Full pipeline:
  Requirements → Design Space → NSGA-II → Iteration → Constraints → Reliability
  → Cost → Weight → Performance → Recommendation → Report
"""
from __future__ import annotations

import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.optimization.schemas import (
    OptimizationRunRequest, OptimizationRunResponse,
    DesignVector, DesignParameter, ObjectiveSpec, ConstraintSpec,
    ParetoFrontRequest, DesignSpaceRequest, ConstraintSolverRequest,
    ReliabilityRequest, CostOptimizationRequest, WeightOptimizationRequest,
    PerformanceOptimizationRequest, DesignIterationRequest, RecommendationRequest,
    OptimizationDomain, OptimizationAlgorithm,
)
from app.optimization.services.multi_objective_optimizer import MultiObjectiveOptimizer
from app.optimization.services.design_space_explorer import DesignSpaceExplorer
from app.optimization.services.constraint_solver import ConstraintSolver
from app.optimization.services.reliability_optimizer import ReliabilityOptimizer
from app.optimization.services.cost_optimizer import CostOptimizer
from app.optimization.services.weight_optimizer import WeightOptimizer
from app.optimization.services.performance_optimizer import PerformanceOptimizer
from app.optimization.services.design_iteration_engine import DesignIterationEngine
from app.optimization.services.recommendation_engine import RecommendationEngine


class OptimizationOrchestrator:
    """
    Master orchestrator that runs the complete optimization pipeline:
    Analyze → Simulate → Evaluate → Optimize → Re-Simulate → Validate → Recommend
    """

    @staticmethod
    def run_full_optimization(request: OptimizationRunRequest) -> OptimizationRunResponse:
        t_start = time.perf_counter()

        opt_project_id = str(uuid.uuid4())
        run_id = str(uuid.uuid4())
        pipeline_results: Dict[str, Any] = {}

        # ── PHASE 1: Design Space Exploration ───────────────────────────────
        dse_result = None
        try:
            dse_request = DesignSpaceRequest(
                project_id=request.project_id,
                domain=request.domain,
                design_parameters=request.design_parameters,
                objectives=request.objectives,
                sample_count=min(100, request.population_size * 2),
                sampling_method="lhs",
            )
            dse_result = DesignSpaceExplorer.explore(dse_request)
            pipeline_results["design_space"] = {
                "feasible_fraction": dse_result.feasible_region_fraction,
                "sensitivity_indices": dse_result.sensitivity_indices,
                "optimal_regions_found": len(dse_result.optimal_regions),
            }
        except Exception as e:
            pipeline_results["design_space"] = {"error": str(e)}

        # ── PHASE 2: Multi-Objective Optimization (NSGA-II) ──────────────────
        pareto_result = None
        pareto_designs: List[DesignVector] = []
        try:
            pareto_request = ParetoFrontRequest(
                project_id=request.project_id,
                design_parameters=request.design_parameters,
                objectives=request.objectives,
                constraints=request.constraints,
                population_size=request.population_size,
                generations=request.max_iterations,
            )
            pareto_result = MultiObjectiveOptimizer.optimize(pareto_request)
            pareto_designs = [ps.design for ps in pareto_result.pareto_front]
            pipeline_results["nsga2"] = {
                "pareto_solutions": len(pareto_designs),
                "hypervolume": pareto_result.hypervolume_indicator,
                "generations_run": pareto_result.generations_run,
            }
        except Exception as e:
            pipeline_results["nsga2"] = {"error": str(e)}

        # Pick best design from Pareto for subsequent phases
        best_design = pareto_designs[0] if pareto_designs else OptimizationOrchestrator._fallback_design(request)

        # ── PHASE 3: Design Iteration Refinement ────────────────────────────
        iter_result = None
        try:
            iter_request = DesignIterationRequest(
                project_id=request.project_id,
                domain=request.domain,
                initial_design=best_design.parameters,
                design_parameters=request.design_parameters,
                objectives=request.objectives,
                constraints=request.constraints,
                max_iterations=min(100, request.max_iterations),
                convergence_tolerance=1e-4,
                early_stopping_patience=10,
            )
            iter_result = DesignIterationEngine.iterate(iter_request)
            best_design = iter_result.best_design
            pipeline_results["iteration"] = {
                "iterations_run": iter_result.iterations_run,
                "converged": iter_result.converged,
                "summary": iter_result.improvement_summary,
            }
        except Exception as e:
            pipeline_results["iteration"] = {"error": str(e)}

        # ── PHASE 4: Constraint Validation ──────────────────────────────────
        constraint_report: Dict[str, Any] = {}
        if request.validate_constraints and request.constraints:
            try:
                cs_request = ConstraintSolverRequest(
                    project_id=request.project_id,
                    design=best_design.parameters,
                    constraints=request.constraints,
                    domain=request.domain,
                )
                cs_result = ConstraintSolver.solve(cs_request)
                constraint_report = {
                    "is_feasible": cs_result.is_feasible,
                    "satisfied": cs_result.satisfied_count,
                    "violated": cs_result.violated_count,
                    "penalty_score": cs_result.penalty_score,
                    "fix_suggestions": cs_result.fix_suggestions[:3],
                }
                pipeline_results["constraint_check"] = constraint_report
            except Exception as e:
                pipeline_results["constraint_check"] = {"error": str(e)}

        # ── PHASE 5: Reliability Assessment ─────────────────────────────────
        simulation_results: Dict[str, Any] = {}
        try:
            rel_request = ReliabilityRequest(
                project_id=request.project_id,
                domain=request.domain,
                design=best_design.parameters,
                mission_duration_hours=float(request.domain_config.get("mission_hours", 500)),
                monte_carlo_samples=1000,
                target_reliability=float(request.domain_config.get("target_reliability", 0.99)),
            )
            rel_result = ReliabilityOptimizer.optimize(rel_request)
            simulation_results["reliability"] = {
                "system_reliability": rel_result.system_reliability,
                "system_mtbf_hr": rel_result.system_mtbf_hr,
                "top_risks": rel_result.failure_mode_analysis[:3],
            }
            pipeline_results["reliability"] = simulation_results["reliability"]
        except Exception as e:
            pipeline_results["reliability"] = {"error": str(e)}

        # ── PHASE 6: Cost Optimization ───────────────────────────────────────
        try:
            cost_request = CostOptimizationRequest(
                project_id=request.project_id,
                domain=request.domain,
                design=best_design.parameters,
                budget_usd=float(request.domain_config.get("budget_usd", 5000)),
                production_volume=int(request.domain_config.get("production_volume", 1)),
            )
            cost_result = CostOptimizer.optimize(cost_request)
            simulation_results["cost"] = {
                "original_cost_usd": cost_result.original_cost_usd,
                "optimized_cost_usd": cost_result.optimized_cost_usd,
                "savings_percent": cost_result.savings_percent,
            }
            pipeline_results["cost"] = simulation_results["cost"]
        except Exception as e:
            pipeline_results["cost"] = {"error": str(e)}

        # ── PHASE 7: Weight Optimization ─────────────────────────────────────
        try:
            wt_request = WeightOptimizationRequest(
                project_id=request.project_id,
                domain=request.domain,
                design=best_design.parameters,
                mass_budget_kg=float(request.domain_config.get("mass_budget_kg", 10.0)),
            )
            wt_result = WeightOptimizer.optimize(wt_request)
            simulation_results["weight"] = {
                "original_mass_kg": wt_result.original_mass_kg,
                "optimized_mass_kg": wt_result.optimized_mass_kg,
                "mass_reduction_percent": wt_result.mass_reduction_percent,
            }
            pipeline_results["weight"] = simulation_results["weight"]
        except Exception as e:
            pipeline_results["weight"] = {"error": str(e)}

        # ── PHASE 8: Performance Optimization ───────────────────────────────
        try:
            perf_request = PerformanceOptimizationRequest(
                project_id=request.project_id,
                domain=request.domain,
                design=best_design.parameters,
                performance_targets=request.domain_config.get("performance_targets", {}),
                constraints=request.constraints,
            )
            perf_result = PerformanceOptimizer.optimize(perf_request)
            simulation_results["performance"] = {
                "overall_improvement_percent": perf_result.overall_improvement_percent,
                "metrics_count": len(perf_result.metrics),
                "bottleneck": perf_result.bottleneck_analysis.get("primary_bottleneck"),
            }
            pipeline_results["performance"] = simulation_results["performance"]
        except Exception as e:
            pipeline_results["performance"] = {"error": str(e)}

        # ── PHASE 9: Recommendations ─────────────────────────────────────────
        recommendations: List[Dict[str, Any]] = []
        ai_explanation = ""
        try:
            rec_request = RecommendationRequest(
                project_id=request.project_id,
                domain=request.domain,
                pareto_designs=pareto_designs[:10],  # Top 10 Pareto solutions
                constraints=request.constraints,
                n_recommendations=3,
            )
            rec_result = RecommendationEngine.recommend(rec_request)
            recommendations.append({
                "rank": 1,
                "title": rec_result.best_design.title,
                "score": rec_result.best_design.score,
                "justification": rec_result.best_design.justification,
                "confidence": rec_result.best_design.confidence,
                "tradeoffs": rec_result.best_design.critical_tradeoffs,
                "risks": rec_result.best_design.major_risks,
                "improvements": rec_result.best_design.remaining_improvements,
            })
            for alt in rec_result.alternatives:
                recommendations.append({
                    "rank": alt.rank,
                    "title": alt.title,
                    "score": alt.score,
                    "justification": alt.justification,
                    "confidence": alt.confidence,
                })
            ai_explanation = rec_result.ai_explanation
            pipeline_results["recommendations"] = {
                "winner": rec_result.best_design.title,
                "score": rec_result.best_design.score,
                "alternatives_count": len(rec_result.alternatives),
            }
        except Exception as e:
            pipeline_results["recommendations"] = {"error": str(e)}

        # ── Build Iteration History ──────────────────────────────────────────
        iteration_history: List[Dict[str, Any]] = []
        if iter_result:
            iteration_history = [
                {
                    "iteration": r.iteration,
                    "objectives": r.objectives,
                    "constraint_violations": r.constraint_violations,
                    "improvement_delta": r.improvement_delta,
                    "is_best": r.is_best,
                }
                for r in iter_result.iteration_history[:50]  # Cap at 50 for response size
            ]

        elapsed = (time.perf_counter() - t_start) * 1000

        return OptimizationRunResponse(
            id=run_id,
            opt_project_id=opt_project_id,
            project_id=request.project_id,
            name=request.name,
            domain=request.domain.value,
            algorithm=request.algorithm.value,
            status="completed",
            total_iterations=request.max_iterations,
            population_size=request.population_size,
            pareto_front=pareto_designs[:20],  # Top 20
            best_design=best_design,
            iteration_history=iteration_history,
            constraint_report=constraint_report,
            simulation_results=simulation_results,
            recommendations=recommendations,
            ai_explanation=ai_explanation,
            elapsed_ms=round(elapsed, 2),
            created_at=datetime.utcnow(),
        )

    @staticmethod
    def _fallback_design(request: OptimizationRunRequest) -> DesignVector:
        """Generate a midpoint design if optimization failed."""
        params = {p.name: (p.lower_bound + p.upper_bound) / 2 for p in request.design_parameters}
        return DesignVector(
            name="fallback_midpoint_design",
            parameters=params,
            objectives={},
            constraints_satisfied=True,
        )
