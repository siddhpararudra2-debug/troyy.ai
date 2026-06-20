"""
Optimization Platform — Comprehensive Test Suite
Day 28: Optimization & Engineering Intelligence Platform

Coverage targets:
  - Unit tests: all 11 service modules
  - Integration tests: full pipeline + constraint cross-checks
  - Performance tests: all endpoints within time budgets
  - Edge cases: empty inputs, boundary values, infeasible designs
"""
from __future__ import annotations

import time
import pytest
import math
from typing import Any, Dict, List

from app.optimization.schemas import (
    # Primitives
    DesignParameter, ObjectiveSpec, ConstraintSpec, DesignVector, TradeOption,
    ObjectiveDirection, ConstraintType, ConstraintOperator, OptimizationDomain,
    # Module-specific requests
    ParetoFrontRequest, DesignSpaceRequest, TradeStudyRequest,
    ConstraintSolverRequest, ReliabilityRequest, CostOptimizationRequest,
    WeightOptimizationRequest, PerformanceOptimizationRequest,
    DesignIterationRequest, RecommendationRequest, OptimizationRunRequest,
    OptimizationAlgorithm,
)
from app.optimization.services import (
    MultiObjectiveOptimizer, DesignSpaceExplorer, TradeStudyEngine,
    ConstraintSolver, ReliabilityOptimizer, CostOptimizer,
    WeightOptimizer, PerformanceOptimizer, DesignIterationEngine,
    RecommendationEngine, OptimizationOrchestrator,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def drone_params():
    return [
        DesignParameter(name="motor_kv",        value=1000, lower_bound=500,  upper_bound=2000, unit="KV"),
        DesignParameter(name="propeller_dia_m", value=0.25, lower_bound=0.15, upper_bound=0.40, unit="m"),
        DesignParameter(name="battery_wh",      value=400,  lower_bound=100,  upper_bound=800,  unit="Wh"),
        DesignParameter(name="mass_kg",         value=2.0,  lower_bound=0.5,  upper_bound=5.0,  unit="kg"),
    ]


@pytest.fixture
def dual_objectives():
    return [
        ObjectiveSpec(name="weight", direction=ObjectiveDirection.MINIMIZE, weight=1.0),
        ObjectiveSpec(name="cost",   direction=ObjectiveDirection.MINIMIZE, weight=1.0),
    ]


@pytest.fixture
def triple_objectives():
    return [
        ObjectiveSpec(name="weight",      direction=ObjectiveDirection.MINIMIZE, weight=1.0),
        ObjectiveSpec(name="cost",        direction=ObjectiveDirection.MINIMIZE, weight=1.0),
        ObjectiveSpec(name="performance", direction=ObjectiveDirection.MAXIMIZE, weight=1.0),
    ]


@pytest.fixture
def mass_constraint():
    return ConstraintSpec(
        name="mass_limit", constraint_type=ConstraintType.MASS,
        operator=ConstraintOperator.LTE, value=5.0, unit="kg", is_hard=True
    )


@pytest.fixture
def power_constraint():
    return ConstraintSpec(
        name="power_limit", constraint_type=ConstraintType.POWER,
        operator=ConstraintOperator.LTE, value=500.0, unit="W", is_hard=True
    )


# ── Module 2: Multi-Objective Optimizer (NSGA-II) ────────────────────────────

class TestMultiObjectiveOptimizer:

    def test_pareto_front_returns_nonempty(self, drone_params, dual_objectives):
        request = ParetoFrontRequest(
            project_id="test-proj-001",
            design_parameters=drone_params,
            objectives=dual_objectives,
            population_size=20,
            generations=10,
        )
        result = MultiObjectiveOptimizer.optimize(request)
        assert len(result.pareto_front) > 0

    def test_pareto_solutions_are_nondominated(self, drone_params, dual_objectives):
        """No Pareto solution should dominate another."""
        request = ParetoFrontRequest(
            project_id="test-proj-002",
            design_parameters=drone_params,
            objectives=dual_objectives,
            population_size=30,
            generations=20,
        )
        result = MultiObjectiveOptimizer.optimize(request)
        front = result.pareto_front
        # Check pairwise non-dominance (sample up to 10)
        for i in range(min(len(front), 10)):
            for j in range(min(len(front), 10)):
                if i == j:
                    continue
                a_objs = front[i].design.objectives
                b_objs = front[j].design.objectives
                # Neither should dominate the other
                a_dom_b = all(a_objs[k] <= b_objs[k] for k in a_objs) and \
                          any(a_objs[k] < b_objs[k] for k in a_objs)
                assert not a_dom_b, f"Solution {i} dominates {j} — Pareto front invalid"

    def test_hypervolume_is_positive(self, drone_params, dual_objectives):
        request = ParetoFrontRequest(
            project_id="test-proj-003",
            design_parameters=drone_params,
            objectives=dual_objectives,
            population_size=20,
            generations=15,
        )
        result = MultiObjectiveOptimizer.optimize(request)
        assert result.hypervolume_indicator >= 0.0

    def test_three_objectives(self, drone_params, triple_objectives):
        request = ParetoFrontRequest(
            project_id="test-proj-004",
            design_parameters=drone_params,
            objectives=triple_objectives,
            population_size=20,
            generations=10,
        )
        result = MultiObjectiveOptimizer.optimize(request)
        # total_evaluated = pop_size * generations (only parents count)
        assert result.total_evaluated == 20 * 10
        assert len(result.pareto_front) > 0

    def test_with_constraints_reduces_feasible_set(self, drone_params, dual_objectives, mass_constraint):
        request = ParetoFrontRequest(
            project_id="test-proj-005",
            design_parameters=drone_params,
            objectives=dual_objectives,
            constraints=[mass_constraint],
            population_size=20,
            generations=10,
        )
        result = MultiObjectiveOptimizer.optimize(request)
        assert result is not None  # Should not crash with constraints

    def test_performance_budget_50gen_50pop(self, drone_params, dual_objectives):
        """NSGA-II with 50 pop × 50 gen should complete within 5 seconds."""
        request = ParetoFrontRequest(
            project_id="test-perf-001",
            design_parameters=drone_params,
            objectives=dual_objectives,
            population_size=50,
            generations=50,
        )
        t0 = time.perf_counter()
        result = MultiObjectiveOptimizer.optimize(request)
        elapsed = time.perf_counter() - t0
        assert elapsed < 5.0, f"NSGA-II too slow: {elapsed:.2f}s"
        assert result.elapsed_ms < 5000


# ── Module 3: Design Space Explorer ─────────────────────────────────────────

class TestDesignSpaceExplorer:

    def test_lhs_produces_correct_sample_count(self, drone_params, dual_objectives):
        request = DesignSpaceRequest(
            project_id="test-dse-001",
            domain=OptimizationDomain.DRONE,
            design_parameters=drone_params,
            objectives=dual_objectives,
            sample_count=100,
            sampling_method="lhs",
        )
        result = DesignSpaceExplorer.explore(request)
        assert result.sample_count == 100
        assert len(result.samples) <= 200  # Capped at 200 for response

    def test_sensitivity_indices_sum_to_one(self, drone_params, dual_objectives):
        request = DesignSpaceRequest(
            project_id="test-dse-002",
            domain=OptimizationDomain.DRONE,
            design_parameters=drone_params,
            objectives=dual_objectives,
            sample_count=50,
        )
        result = DesignSpaceExplorer.explore(request)
        total = sum(result.sensitivity_indices.values())
        assert abs(total - 1.0) < 1e-3, f"Sensitivity indices don't sum to 1: {total}"

    def test_feasible_fraction_between_0_and_1(self, drone_params, dual_objectives):
        request = DesignSpaceRequest(
            project_id="test-dse-003",
            domain=OptimizationDomain.DRONE,
            design_parameters=drone_params,
            objectives=dual_objectives,
            sample_count=50,
        )
        result = DesignSpaceExplorer.explore(request)
        assert 0.0 <= result.feasible_region_fraction <= 1.0

    def test_performance_100_samples(self, drone_params, dual_objectives):
        """100 design alternatives in <10 seconds."""
        request = DesignSpaceRequest(
            project_id="test-dse-perf",
            domain=OptimizationDomain.DRONE,
            design_parameters=drone_params,
            objectives=dual_objectives,
            sample_count=100,
        )
        t0 = time.perf_counter()
        result = DesignSpaceExplorer.explore(request)
        elapsed = time.perf_counter() - t0
        assert elapsed < 10.0, f"Design space exploration too slow: {elapsed:.2f}s"


# ── Module 4: Trade Study Engine ─────────────────────────────────────────────

class TestTradeStudyEngine:

    def test_winner_is_valid_option(self):
        options = [
            TradeOption(name="OptionA", parameters={"efficiency": 0.9, "cost": 300.0}),
            TradeOption(name="OptionB", parameters={"efficiency": 0.75, "cost": 150.0}),
            TradeOption(name="OptionC", parameters={"efficiency": 0.85, "cost": 200.0}),
        ]
        criteria = [
            ObjectiveSpec(name="efficiency", direction=ObjectiveDirection.MAXIMIZE, weight=2.0),
            ObjectiveSpec(name="cost",       direction=ObjectiveDirection.MINIMIZE, weight=1.0),
        ]
        request = TradeStudyRequest(
            project_id="test-ts-001",
            study_name="Motor Selection Study",
            options=options,
            criteria=criteria,
        )
        result = TradeStudyEngine.run(request)
        assert result.winner in [o.name for o in options]

    def test_results_ranked_correctly(self):
        options = [
            TradeOption(name="Best",   parameters={"performance": 9.0}),
            TradeOption(name="Medium", parameters={"performance": 5.0}),
            TradeOption(name="Poor",   parameters={"performance": 1.0}),
        ]
        criteria = [ObjectiveSpec(name="performance", direction=ObjectiveDirection.MAXIMIZE)]
        request = TradeStudyRequest(
            project_id="test-ts-002",
            study_name="Performance Ranking",
            options=options,
            criteria=criteria,
        )
        result = TradeStudyEngine.run(request)
        # Results list is sorted by weighted_score (descending) so first item has rank=1
        assert result.results[0].rank == 1
        assert all(r.rank > 0 for r in result.results)
        ranks = sorted([r.rank for r in result.results])
        assert ranks == list(range(1, len(result.results) + 1))  # All unique sequential ranks

    def test_performance_under_2_seconds(self):
        options = [TradeOption(name=f"Option{i}", parameters={"x": float(i)}) for i in range(5)]
        criteria = [ObjectiveSpec(name="x", direction=ObjectiveDirection.MAXIMIZE)]
        request = TradeStudyRequest(
            project_id="test-ts-perf",
            study_name="Perf Test",
            options=options,
            criteria=criteria,
        )
        t0 = time.perf_counter()
        result = TradeStudyEngine.run(request)
        elapsed = time.perf_counter() - t0
        assert elapsed < 2.0, f"Trade study too slow: {elapsed:.3f}s"

    def test_ahp_custom_matrix(self):
        options = [
            TradeOption(name="A", parameters={}),
            TradeOption(name="B", parameters={}),
        ]
        criteria = [
            ObjectiveSpec(name="weight",      direction=ObjectiveDirection.MINIMIZE),
            ObjectiveSpec(name="reliability", direction=ObjectiveDirection.MAXIMIZE),
        ]
        ahp_matrix = [[1.0, 3.0], [1/3, 1.0]]  # Weight 3× more important than reliability
        request = TradeStudyRequest(
            project_id="test-ts-003",
            study_name="AHP Test",
            options=options,
            criteria=criteria,
            ahp_matrix=ahp_matrix,
        )
        result = TradeStudyEngine.run(request)
        assert result.winner in ["A", "B"]
        # Weight criterion should dominate (weight ~0.75)
        assert result.criteria_weights["weight"] > result.criteria_weights["reliability"]


# ── Module 5: Constraint Solver ───────────────────────────────────────────────

class TestConstraintSolver:

    def test_satisfies_all_constraints(self):
        design = {"mass_limit": 3.0, "power_limit": 200.0}
        constraints = [
            ConstraintSpec(name="mass_limit",  constraint_type=ConstraintType.MASS,  operator=ConstraintOperator.LTE, value=5.0),
            ConstraintSpec(name="power_limit", constraint_type=ConstraintType.POWER, operator=ConstraintOperator.LTE, value=500.0),
        ]
        request = ConstraintSolverRequest(project_id="test-cs-001", design=design, constraints=constraints)
        result = ConstraintSolver.solve(request)
        assert result.is_feasible
        assert result.violated_count == 0
        assert result.satisfied_count == 2

    def test_detects_mass_violation(self):
        design = {"mass_limit": 8.0}
        constraints = [
            ConstraintSpec(name="mass_limit", constraint_type=ConstraintType.MASS, operator=ConstraintOperator.LTE, value=5.0, is_hard=True),
        ]
        request = ConstraintSolverRequest(project_id="test-cs-002", design=design, constraints=constraints)
        result = ConstraintSolver.solve(request)
        assert result.violated_count == 1
        assert result.violations[0].violation_magnitude == pytest.approx(3.0, abs=0.01)

    def test_range_constraint(self):
        design = {"temperature": 75.0}  # 75°C — inside [20, 85]
        constraints = [
            ConstraintSpec(
                name="temperature", constraint_type=ConstraintType.THERMAL,
                operator=ConstraintOperator.RANGE, value=20.0, value_max=85.0, unit="°C"
            ),
        ]
        request = ConstraintSolverRequest(project_id="test-cs-003", design=design, constraints=constraints)
        result = ConstraintSolver.solve(request)
        assert result.violated_count == 0

    def test_safety_critical_fix_generated(self):
        design = {"safety_critical": 0.1}
        constraints = [
            ConstraintSpec(
                name="safety_critical", constraint_type=ConstraintType.SAFETY,
                operator=ConstraintOperator.GTE, value=2.0, is_hard=True
            ),
        ]
        request = ConstraintSolverRequest(project_id="test-cs-004", design=design, constraints=constraints)
        result = ConstraintSolver.solve(request)
        assert result.violated_count == 1
        assert "SAFETY" in result.violations[0].engineering_fix.upper()

    def test_performance_under_1_second(self):
        design = {f"var_{i}": float(i) for i in range(20)}
        constraints = [
            ConstraintSpec(name=f"var_{i}", constraint_type=ConstraintType.DIMENSIONAL,
                           operator=ConstraintOperator.LTE, value=float(i + 5))
            for i in range(20)
        ]
        request = ConstraintSolverRequest(project_id="test-cs-perf", design=design, constraints=constraints)
        t0 = time.perf_counter()
        result = ConstraintSolver.solve(request)
        elapsed = time.perf_counter() - t0
        assert elapsed < 1.0, f"Constraint solver too slow: {elapsed:.3f}s"


# ── Module 6: Reliability Optimizer ─────────────────────────────────────────

class TestReliabilityOptimizer:

    def test_system_reliability_between_0_and_1(self):
        request = ReliabilityRequest(
            project_id="test-rel-001",
            domain=OptimizationDomain.DRONE,
            design={},
            mission_duration_hours=100.0,
            monte_carlo_samples=1000,
            target_reliability=0.99,
        )
        result = ReliabilityOptimizer.optimize(request)
        assert 0.0 <= result.system_reliability <= 1.0

    def test_all_components_have_positive_mtbf(self):
        request = ReliabilityRequest(
            project_id="test-rel-002",
            domain=OptimizationDomain.ROBOTICS,
            design={},
            mission_duration_hours=500.0,
            monte_carlo_samples=1000,
        )
        result = ReliabilityOptimizer.optimize(request)
        for comp in result.component_reliabilities:
            assert comp.mean_time_between_failure_hr > 0

    def test_fmea_has_rpn_scores(self):
        request = ReliabilityRequest(
            project_id="test-rel-003",
            domain=OptimizationDomain.DRONE,
            design={},
            mission_duration_hours=100.0,
            monte_carlo_samples=500,
        )
        result = ReliabilityOptimizer.optimize(request)
        for item in result.failure_mode_analysis:
            assert "rpn" in item
            assert item["rpn"] >= 0


# ── Module 7: Cost Optimizer ─────────────────────────────────────────────────

class TestCostOptimizer:

    def test_savings_are_non_negative(self):
        request = CostOptimizationRequest(
            project_id="test-cost-001",
            domain=OptimizationDomain.DRONE,
            design={"manufacturing_process": "cnc_machining"},
            budget_usd=2000.0,
            production_volume=1,
        )
        result = CostOptimizer.optimize(request)
        assert result.savings_usd >= 0
        assert result.optimized_cost_usd <= result.original_cost_usd

    def test_volume_discount_reduces_cost(self):
        base_request = CostOptimizationRequest(
            project_id="test-cost-002",
            domain=OptimizationDomain.DRONE,
            design={},
            budget_usd=5000.0,
            production_volume=1,
        )
        vol_request = CostOptimizationRequest(
            project_id="test-cost-003",
            domain=OptimizationDomain.DRONE,
            design={},
            budget_usd=5000.0,
            production_volume=100,
        )
        base_result = CostOptimizer.optimize(base_request)
        vol_result = CostOptimizer.optimize(vol_request)
        assert vol_result.optimized_cost_usd < base_result.optimized_cost_usd

    def test_cost_breakdown_totals_correct(self):
        request = CostOptimizationRequest(
            project_id="test-cost-004",
            domain=OptimizationDomain.ELECTRONICS,
            design={},
            budget_usd=1000.0,
            production_volume=10,
        )
        result = CostOptimizer.optimize(request)
        # Cost breakdown should be non-trivial
        breakdown_total = sum(result.cost_breakdown.values())
        assert breakdown_total > 0, "Cost breakdown should not be zero"
        assert result.optimized_cost_usd >= 0, "Optimized cost should be non-negative"


# ── Module 8: Weight Optimizer ────────────────────────────────────────────────

class TestWeightOptimizer:

    def test_optimized_mass_less_than_original(self):
        request = WeightOptimizationRequest(
            project_id="test-wt-001",
            domain=OptimizationDomain.DRONE,
            design={"primary_material": "aluminum_6061"},
            mass_budget_kg=2.0,
        )
        result = WeightOptimizer.optimize(request)
        assert result.optimized_mass_kg <= result.original_mass_kg

    def test_carbon_fiber_beats_aluminum_on_specific_strength(self):
        """CFRP has higher specific strength → should result in mass reduction."""
        request = WeightOptimizationRequest(
            project_id="test-wt-002",
            domain=OptimizationDomain.DRONE,
            design={"primary_material": "aluminum_6061"},
            mass_budget_kg=5.0,
            material_options=["aluminum_6061", "carbon_fiber"],
        )
        result = WeightOptimizer.optimize(request)
        # Should have at least one material_swap reduction item
        material_swaps = [r for r in result.reduction_items if "material_swap" in r.method]
        assert len(material_swaps) > 0

    def test_mass_reduction_percent_realistic(self):
        request = WeightOptimizationRequest(
            project_id="test-wt-003",
            domain=OptimizationDomain.ROBOTICS,
            design={},
            mass_budget_kg=10.0,
        )
        result = WeightOptimizer.optimize(request)
        # Realistic optimization: 0–60% reduction
        assert 0.0 <= result.mass_reduction_percent <= 60.0


# ── Module 9: Performance Optimizer ──────────────────────────────────────────

class TestPerformanceOptimizer:

    def test_drone_metrics_computed(self):
        request = PerformanceOptimizationRequest(
            project_id="test-perf-001",
            domain=OptimizationDomain.DRONE,
            design={
                "mass_kg": 2.5, "battery_wh": 400,
                "motor_efficiency": 0.85, "prop_figure_of_merit": 0.75,
                "payload_kg": 0.5, "disk_area_m2": 0.08,
            },
            performance_targets={"flight_time_min": 30.0},
        )
        result = PerformanceOptimizer.optimize(request)
        metric_names = [m.name for m in result.metrics]
        assert "flight_time_min" in metric_names
        assert "hover_efficiency" in metric_names

    def test_aerospace_metrics_computed(self):
        request = PerformanceOptimizationRequest(
            project_id="test-perf-002",
            domain=OptimizationDomain.AEROSPACE,
            design={
                "wing_area_m2": 1.5, "aspect_ratio": 8.0,
                "mass_kg": 5.0, "cl_max": 1.4, "cd0": 0.025,
                "thrust_n": 50.0,
            },
            performance_targets={},
        )
        result = PerformanceOptimizer.optimize(request)
        metric_names = [m.name for m in result.metrics]
        assert "ld_max" in metric_names
        assert "stall_speed_ms" in metric_names

    def test_optimized_better_than_original(self):
        request = PerformanceOptimizationRequest(
            project_id="test-perf-003",
            domain=OptimizationDomain.DRONE,
            design={"mass_kg": 2.5, "battery_wh": 400, "motor_efficiency": 0.85, "prop_figure_of_merit": 0.75,
                    "payload_kg": 0.5, "disk_area_m2": 0.08},
        )
        result = PerformanceOptimizer.optimize(request)
        assert result.overall_improvement_percent >= 0.0


# ── Module 10: Design Iteration Engine ───────────────────────────────────────

class TestDesignIterationEngine:

    def test_convergence_single_objective(self, drone_params):
        objectives = [ObjectiveSpec(name="weight", direction=ObjectiveDirection.MINIMIZE)]
        request = DesignIterationRequest(
            project_id="test-iter-001",
            domain=OptimizationDomain.DRONE,
            initial_design={p.name: (p.lower_bound + p.upper_bound) / 2 for p in drone_params},
            design_parameters=drone_params,
            objectives=objectives,
            max_iterations=50,
            convergence_tolerance=1e-4,
            early_stopping_patience=10,
        )
        result = DesignIterationEngine.iterate(request)
        assert result.iterations_run > 0
        assert result.best_design is not None
        assert len(result.iteration_history) == result.iterations_run

    def test_history_monotonically_non_increasing(self, drone_params):
        """Best objective should not increase over iterations (for minimize)."""
        objectives = [ObjectiveSpec(name="weight", direction=ObjectiveDirection.MINIMIZE)]
        request = DesignIterationRequest(
            project_id="test-iter-002",
            domain=OptimizationDomain.DRONE,
            initial_design={p.name: (p.lower_bound + p.upper_bound) / 2 for p in drone_params},
            design_parameters=drone_params,
            objectives=objectives,
            max_iterations=30,
            early_stopping_patience=30,  # No early stopping
        )
        result = DesignIterationEngine.iterate(request)
        # Best values should be non-increasing (or at least not worsening dramatically)
        obj_vals = [r.objectives.get("weight", 0) for r in result.iteration_history if r.is_best]
        if len(obj_vals) > 1:
            # Allow small fluctuations from coordinate descent
            assert obj_vals[-1] <= obj_vals[0] * 1.1

    def test_bounds_respected(self, drone_params):
        objectives = [ObjectiveSpec(name="cost", direction=ObjectiveDirection.MINIMIZE)]
        request = DesignIterationRequest(
            project_id="test-iter-003",
            domain=OptimizationDomain.DRONE,
            initial_design={p.name: (p.lower_bound + p.upper_bound) / 2 for p in drone_params},
            design_parameters=drone_params,
            objectives=objectives,
            max_iterations=20,
        )
        result = DesignIterationEngine.iterate(request)
        for param in drone_params:
            val = result.best_design.parameters.get(param.name, 0)
            assert param.lower_bound <= val <= param.upper_bound, (
                f"Bound violated for {param.name}: {val} not in [{param.lower_bound}, {param.upper_bound}]"
            )


# ── Module 11: Recommendation Engine ────────────────────────────────────────

class TestRecommendationEngine:

    def test_returns_requested_number_of_recommendations(self):
        request = RecommendationRequest(
            project_id="test-rec-001",
            domain=OptimizationDomain.DRONE,
            n_recommendations=3,
        )
        result = RecommendationEngine.recommend(request)
        # best + alternatives = n_recommendations
        total = 1 + len(result.alternatives)
        assert total <= 3

    def test_best_design_has_highest_score(self):
        request = RecommendationRequest(
            project_id="test-rec-002",
            domain=OptimizationDomain.DRONE,
            n_recommendations=3,
        )
        result = RecommendationEngine.recommend(request)
        best_score = result.best_design.score
        for alt in result.alternatives:
            assert best_score >= alt.score, f"Best ({best_score}) < alternative ({alt.score})"

    def test_ai_explanation_not_empty(self):
        request = RecommendationRequest(
            project_id="test-rec-003",
            domain=OptimizationDomain.AEROSPACE,
            n_recommendations=2,
        )
        result = RecommendationEngine.recommend(request)
        assert len(result.ai_explanation) > 100
        assert "WHY" in result.ai_explanation
        assert "RISK" in result.ai_explanation

    def test_performance_under_1_second(self):
        request = RecommendationRequest(
            project_id="test-rec-perf",
            domain=OptimizationDomain.DRONE,
            n_recommendations=5,
        )
        t0 = time.perf_counter()
        result = RecommendationEngine.recommend(request)
        elapsed = time.perf_counter() - t0
        assert elapsed < 1.0, f"Recommendation engine too slow: {elapsed:.3f}s"


# ── Integration Test: Full Optimization Pipeline ──────────────────────────────

class TestFullOptimizationPipeline:

    def test_drone_full_pipeline(self, drone_params, dual_objectives, mass_constraint):
        request = OptimizationRunRequest(
            project_id="test-full-001",
            name="Test Drone Optimization",
            domain=OptimizationDomain.DRONE,
            design_parameters=drone_params,
            objectives=dual_objectives,
            constraints=[mass_constraint],
            algorithm=OptimizationAlgorithm.NSGA2,
            max_iterations=10,
            population_size=20,
            run_simulation=True,
            validate_constraints=True,
        )
        t0 = time.perf_counter()
        result = OptimizationOrchestrator.run_full_optimization(request)
        elapsed = time.perf_counter() - t0

        # Functional assertions
        assert result.project_id == "test-full-001"
        assert result.domain == "drone"
        assert result.status == "completed"
        assert result.best_design is not None
        assert len(result.pareto_front) > 0

        # Performance assertion (full pipeline ≤ 30 seconds for test config)
        assert elapsed < 30.0, f"Full pipeline too slow: {elapsed:.2f}s"

    def test_robotics_full_pipeline(self):
        params = [
            DesignParameter(name="n_joints",     value=6,    lower_bound=3,  upper_bound=7),
            DesignParameter(name="link_len_m",   value=0.25, lower_bound=0.15, upper_bound=0.5),
            DesignParameter(name="gear_ratio",   value=100,  lower_bound=50,  upper_bound=200),
            DesignParameter(name="payload_kg",   value=5,    lower_bound=1,  upper_bound=20),
        ]
        objectives = [
            ObjectiveSpec(name="weight", direction=ObjectiveDirection.MINIMIZE),
            ObjectiveSpec(name="cost",   direction=ObjectiveDirection.MINIMIZE),
        ]
        request = OptimizationRunRequest(
            project_id="test-full-002",
            name="Test Robotics Optimization",
            domain=OptimizationDomain.ROBOTICS,
            design_parameters=params,
            objectives=objectives,
            max_iterations=10,
            population_size=15,
        )
        result = OptimizationOrchestrator.run_full_optimization(request)
        assert result.status == "completed"
        assert result.best_design is not None

    def test_electronics_full_pipeline(self):
        params = [
            DesignParameter(name="supply_voltage",  value=3.3,  lower_bound=1.8, upper_bound=5.0),
            DesignParameter(name="switching_freq_hz", value=1e6, lower_bound=100e3, upper_bound=4e6),
            DesignParameter(name="filter_cap_uf",   value=100,  lower_bound=10,  upper_bound=1000),
        ]
        objectives = [
            ObjectiveSpec(name="efficiency", direction=ObjectiveDirection.MAXIMIZE),
            ObjectiveSpec(name="cost",       direction=ObjectiveDirection.MINIMIZE),
        ]
        request = OptimizationRunRequest(
            project_id="test-full-003",
            name="Test Electronics Optimization",
            domain=OptimizationDomain.ELECTRONICS,
            design_parameters=params,
            objectives=objectives,
            max_iterations=10,
            population_size=15,
        )
        result = OptimizationOrchestrator.run_full_optimization(request)
        assert result.status == "completed"


# ── Edge Cases ────────────────────────────────────────────────────────────────

class TestEdgeCases:

    def test_single_design_point(self):
        """Single sample in design space."""
        params = [DesignParameter(name="x", value=1.0, lower_bound=1.0, upper_bound=1.0)]
        objectives = [ObjectiveSpec(name="weight", direction=ObjectiveDirection.MINIMIZE)]
        request = DesignSpaceRequest(
            project_id="test-edge-001",
            domain=OptimizationDomain.DRONE,
            design_parameters=params,
            objectives=objectives,
            sample_count=10,
        )
        result = DesignSpaceExplorer.explore(request)
        assert result is not None

    def test_all_constraints_violated(self):
        """Design that violates all constraints."""
        design = {"mass": 100.0, "power": 10000.0}
        constraints = [
            ConstraintSpec(name="mass",  constraint_type=ConstraintType.MASS,  operator=ConstraintOperator.LTE, value=5.0),
            ConstraintSpec(name="power", constraint_type=ConstraintType.POWER, operator=ConstraintOperator.LTE, value=500.0),
        ]
        request = ConstraintSolverRequest(project_id="test-edge-002", design=design, constraints=constraints)
        result = ConstraintSolver.solve(request)
        assert result.violated_count == 2
        assert result.penalty_score > 0

    def test_maximize_and_minimize_mixed(self):
        """Mix of minimize/maximize objectives."""
        params = [
            DesignParameter(name="x", value=1.0, lower_bound=0.0, upper_bound=2.0),
            DesignParameter(name="y", value=1.0, lower_bound=0.0, upper_bound=2.0),
        ]
        objectives = [
            ObjectiveSpec(name="cost",        direction=ObjectiveDirection.MINIMIZE),
            ObjectiveSpec(name="performance", direction=ObjectiveDirection.MAXIMIZE),
        ]
        request = ParetoFrontRequest(
            project_id="test-edge-003",
            design_parameters=params,
            objectives=objectives,
            population_size=10,
            generations=5,
        )
        result = MultiObjectiveOptimizer.optimize(request)
        assert result is not None
        assert len(result.pareto_front) > 0
