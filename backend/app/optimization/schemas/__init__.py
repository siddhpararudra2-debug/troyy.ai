"""
Optimization Platform — Pydantic v2 Schemas
Covers all 11 optimization modules: orchestrator, NSGA-II, design space,
trade study, constraint solver, reliability, cost, weight, performance,
iteration engine, and recommendation engine.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field


# ── Enumerations ─────────────────────────────────────────────────────────────

class OptimizationDomain(str, Enum):
    DRONE       = "drone"
    AEROSPACE   = "aerospace"
    ROBOTICS    = "robotics"
    ELECTRONICS = "electronics"
    MECHANICAL  = "mechanical"
    PCB         = "pcb"
    FIRMWARE    = "firmware"
    MULTI       = "multi"


class OptimizationAlgorithm(str, Enum):
    NSGA2    = "nsga2"       # Non-dominated Sorting Genetic Algorithm II
    LHS      = "lhs"         # Latin Hypercube Sampling
    GRADIENT = "gradient"    # Gradient descent (single-objective)
    RANDOM   = "random"      # Random search baseline


class ObjectiveDirection(str, Enum):
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"


class ConstraintType(str, Enum):
    MASS        = "mass"
    POWER       = "power"
    THERMAL     = "thermal"
    COST        = "cost"
    STRUCTURAL  = "structural"
    SAFETY      = "safety"
    DIMENSIONAL = "dimensional"
    PERFORMANCE = "performance"


class ConstraintOperator(str, Enum):
    LTE   = "lte"    # ≤
    GTE   = "gte"    # ≥
    EQ    = "eq"     # =
    RANGE = "range"  # [min, max]


class OptimizationStatus(str, Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    COMPLETED = "completed"
    FAILED    = "failed"
    CONVERGED = "converged"


# ── Shared Primitives ────────────────────────────────────────────────────────

class ObjectiveSpec(BaseModel):
    """Single optimization objective definition."""
    name: str = Field(..., description="Objective name, e.g. 'weight', 'cost'")
    direction: ObjectiveDirection = ObjectiveDirection.MINIMIZE
    weight: float = Field(default=1.0, ge=0.0, le=10.0)
    unit: Optional[str] = None
    target_value: Optional[float] = None  # Optional ideal point


class ConstraintSpec(BaseModel):
    """Single engineering constraint definition."""
    name: str
    constraint_type: ConstraintType
    operator: ConstraintOperator
    value: float
    value_max: Optional[float] = None   # Used when operator == RANGE
    unit: Optional[str] = None
    is_hard: bool = True                # Hard constraint vs. soft penalty


class DesignParameter(BaseModel):
    """A single design variable with bounds."""
    name: str
    value: float
    lower_bound: float
    upper_bound: float
    unit: Optional[str] = None
    description: Optional[str] = None


class DesignVector(BaseModel):
    """A complete parameterized design."""
    name: str
    parameters: Dict[str, float] = Field(default_factory=dict)
    objectives: Dict[str, float] = Field(default_factory=dict)
    constraints_satisfied: bool = True
    constraint_violations: Dict[str, float] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ── Module 1: Optimization Orchestrator ─────────────────────────────────────

class OptimizationRunRequest(BaseModel):
    """Top-level request to run a full optimization cycle."""
    project_id: str
    name: str
    domain: OptimizationDomain
    design_parameters: List[DesignParameter] = Field(
        ..., description="Variable design parameters with bounds"
    )
    objectives: List[ObjectiveSpec] = Field(
        ..., min_length=1, description="Objectives to optimize"
    )
    constraints: List[ConstraintSpec] = Field(default_factory=list)
    algorithm: OptimizationAlgorithm = OptimizationAlgorithm.NSGA2
    max_iterations: int = Field(default=50, ge=1, le=1000)
    population_size: int = Field(default=50, ge=10, le=500)
    # Integration flags
    run_simulation: bool = True
    validate_constraints: bool = True
    generate_report: bool = True
    # Domain-specific config passthrough
    domain_config: Dict[str, Any] = Field(default_factory=dict)


class OptimizationRunResponse(BaseModel):
    """Full optimization run result."""
    id: str
    opt_project_id: str
    project_id: str
    name: str
    domain: str
    algorithm: str
    status: str
    total_iterations: int
    population_size: int
    pareto_front: List[DesignVector]
    best_design: Optional[DesignVector]
    iteration_history: List[Dict[str, Any]]
    constraint_report: Dict[str, Any]
    simulation_results: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    ai_explanation: str
    elapsed_ms: float
    created_at: datetime


# ── Module 2: Multi-Objective Optimizer ─────────────────────────────────────

class ParetoFrontRequest(BaseModel):
    project_id: str
    design_parameters: List[DesignParameter]
    objectives: List[ObjectiveSpec] = Field(..., min_length=2)
    constraints: List[ConstraintSpec] = Field(default_factory=list)
    population_size: int = Field(default=50, ge=10, le=500)
    generations: int = Field(default=50, ge=1, le=500)
    crossover_rate: float = Field(default=0.9, ge=0.0, le=1.0)
    mutation_rate: float = Field(default=0.1, ge=0.0, le=1.0)


class ParetoSolution(BaseModel):
    design: DesignVector
    front_rank: int
    crowding_distance: float
    hypervolume_contribution: Optional[float] = None
    dominates: List[int] = Field(default_factory=list)


class ParetoFrontResponse(BaseModel):
    id: str
    project_id: str
    pareto_front: List[ParetoSolution]
    total_evaluated: int
    generations_run: int
    hypervolume_indicator: float
    tradeoff_analysis: Dict[str, Any]
    objective_ranges: Dict[str, Dict[str, float]]
    elapsed_ms: float
    created_at: datetime


# ── Module 3: Design Space Explorer ─────────────────────────────────────────

class DesignSpaceRequest(BaseModel):
    project_id: str
    domain: OptimizationDomain
    design_parameters: List[DesignParameter]
    objectives: List[ObjectiveSpec]
    sample_count: int = Field(default=100, ge=10, le=10000)
    sampling_method: str = Field(default="lhs")  # lhs, random, grid
    # Domain-specific option catalogs
    motor_options: Optional[List[Dict[str, Any]]] = None
    battery_options: Optional[List[Dict[str, Any]]] = None
    wing_configs: Optional[List[Dict[str, Any]]] = None
    actuator_configs: Optional[List[Dict[str, Any]]] = None
    sensor_configs: Optional[List[Dict[str, Any]]] = None


class DesignSpaceResponse(BaseModel):
    id: str
    project_id: str
    sample_count: int
    samples: List[DesignVector]
    performance_landscape: Dict[str, Any]   # objective surface statistics
    design_space_map: Dict[str, Any]        # parameter correlation matrix
    sensitivity_indices: Dict[str, float]   # Sobol-like first-order indices
    feasible_region_fraction: float
    optimal_regions: List[Dict[str, Any]]
    elapsed_ms: float
    created_at: datetime


# ── Module 4: Trade Study Engine ─────────────────────────────────────────────

class TradeOption(BaseModel):
    name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = None


class TradeStudyRequest(BaseModel):
    project_id: str
    study_name: str
    options: List[TradeOption] = Field(..., min_length=2)
    criteria: List[ObjectiveSpec] = Field(..., min_length=1)
    constraints: List[ConstraintSpec] = Field(default_factory=list)
    # AHP pairwise comparison matrix (criteria × criteria); auto-computed if omitted
    ahp_matrix: Optional[List[List[float]]] = None


class TradeStudyResult(BaseModel):
    option_name: str
    weighted_score: float
    raw_scores: Dict[str, float]
    rank: int
    advantages: List[str]
    disadvantages: List[str]
    risk_level: str  # LOW / MEDIUM / HIGH / CRITICAL
    risk_items: List[str]
    engineering_recommendation: str


class TradeStudyResponse(BaseModel):
    id: str
    project_id: str
    study_name: str
    winner: str
    decision_matrix: List[List[float]]
    criteria_weights: Dict[str, float]
    results: List[TradeStudyResult]
    decision_justification: str
    sensitivity_to_weights: Dict[str, Any]
    elapsed_ms: float
    created_at: datetime


# ── Module 5: Constraint Solver ──────────────────────────────────────────────

class ConstraintSolverRequest(BaseModel):
    project_id: str
    design: Dict[str, float]   # parameter name → value
    constraints: List[ConstraintSpec]
    domain: OptimizationDomain = OptimizationDomain.MULTI


class ConstraintViolation(BaseModel):
    constraint_name: str
    constraint_type: str
    actual_value: float
    limit_value: float
    violation_magnitude: float
    severity: str   # warning / error / critical
    engineering_fix: str


class ConstraintSolverResponse(BaseModel):
    id: str
    project_id: str
    is_feasible: bool
    violations: List[ConstraintViolation]
    satisfied_count: int
    violated_count: int
    penalty_score: float
    constraint_report: Dict[str, Any]
    fix_suggestions: List[str]
    elapsed_ms: float
    created_at: datetime


# ── Module 6: Reliability Optimizer ─────────────────────────────────────────

class ReliabilityRequest(BaseModel):
    project_id: str
    domain: OptimizationDomain
    design: Dict[str, Any]
    mission_duration_hours: float = Field(default=1000.0, ge=1.0)
    monte_carlo_samples: int = Field(default=10000, ge=100, le=100000)
    target_reliability: float = Field(default=0.99, ge=0.0, le=1.0)
    redundancy_budget_kg: float = Field(default=0.5, ge=0.0)
    redundancy_budget_usd: float = Field(default=500.0, ge=0.0)


class ComponentReliability(BaseModel):
    name: str
    failure_rate_per_hour: float
    mean_time_between_failure_hr: float
    reliability_at_mission: float
    suggested_redundancy: Optional[str] = None


class ReliabilityResponse(BaseModel):
    id: str
    project_id: str
    system_reliability: float
    system_mtbf_hr: float
    component_reliabilities: List[ComponentReliability]
    failure_mode_analysis: List[Dict[str, Any]]
    redundancy_recommendations: List[str]
    safety_margins: Dict[str, float]
    maintenance_schedule: Dict[str, Any]
    reliability_improvement_plan: List[str]
    elapsed_ms: float
    created_at: datetime


# ── Module 7: Cost Optimizer ─────────────────────────────────────────────────

class CostOptimizationRequest(BaseModel):
    project_id: str
    domain: OptimizationDomain
    design: Dict[str, Any]
    budget_usd: float = Field(default=10000.0, ge=0.0)
    production_volume: int = Field(default=1, ge=1)
    optimize_for: str = Field(default="unit_cost")  # unit_cost, tooling, supply_chain


class CostOptimizationResponse(BaseModel):
    id: str
    project_id: str
    original_cost_usd: float
    optimized_cost_usd: float
    savings_usd: float
    savings_percent: float
    cost_breakdown: Dict[str, float]
    component_substitutions: List[Dict[str, Any]]
    manufacturing_savings: List[str]
    supply_chain_risks: List[str]
    cost_reduction_strategies: List[str]
    trade_off_notes: str
    elapsed_ms: float
    created_at: datetime


# ── Module 8: Weight Optimizer ───────────────────────────────────────────────

class WeightOptimizationRequest(BaseModel):
    project_id: str
    domain: OptimizationDomain
    design: Dict[str, Any]
    mass_budget_kg: float = Field(default=5.0, ge=0.01)
    structural_safety_factor: float = Field(default=2.5, ge=1.0)
    material_options: List[str] = Field(
        default_factory=lambda: ["aluminum_6061", "carbon_fiber", "titanium_grade5", "steel_304"]
    )


class MassReductionItem(BaseModel):
    component: str
    original_mass_kg: float
    optimized_mass_kg: float
    reduction_kg: float
    reduction_percent: float
    method: str        # material_swap, topology, thickness_reduction, geometry
    structural_impact: str


class WeightOptimizationResponse(BaseModel):
    id: str
    project_id: str
    original_mass_kg: float
    optimized_mass_kg: float
    mass_reduction_kg: float
    mass_reduction_percent: float
    mass_breakdown: Dict[str, float]
    reduction_items: List[MassReductionItem]
    structural_validation: Dict[str, Any]
    material_recommendations: List[str]
    mass_reduction_report: str
    elapsed_ms: float
    created_at: datetime


# ── Module 9: Performance Optimizer ──────────────────────────────────────────

class PerformanceOptimizationRequest(BaseModel):
    project_id: str
    domain: OptimizationDomain
    design: Dict[str, Any]
    performance_targets: Dict[str, float] = Field(
        default_factory=dict,
        description="Target KPIs, e.g. {'flight_time_min': 45, 'efficiency': 0.85}"
    )
    constraints: List[ConstraintSpec] = Field(default_factory=list)


class PerformanceMetric(BaseModel):
    name: str
    current_value: float
    optimized_value: float
    target_value: Optional[float]
    improvement_percent: float
    unit: Optional[str]
    achieved: bool


class PerformanceOptimizationResponse(BaseModel):
    id: str
    project_id: str
    domain: str
    metrics: List[PerformanceMetric]
    overall_improvement_percent: float
    bottleneck_analysis: Dict[str, Any]
    optimization_actions: List[str]
    performance_improvement_plan: str
    simulation_results: Dict[str, Any]
    elapsed_ms: float
    created_at: datetime


# ── Module 10: Design Iteration Engine ──────────────────────────────────────

class DesignIterationRequest(BaseModel):
    project_id: str
    domain: OptimizationDomain
    initial_design: Dict[str, Any]
    design_parameters: List[DesignParameter]
    objectives: List[ObjectiveSpec]
    constraints: List[ConstraintSpec] = Field(default_factory=list)
    max_iterations: int = Field(default=100, ge=1, le=1000)
    convergence_tolerance: float = Field(default=1e-4, gt=0.0)
    early_stopping_patience: int = Field(default=10, ge=1)


class IterationRecord(BaseModel):
    iteration: int
    design: Dict[str, float]
    objectives: Dict[str, float]
    constraint_violations: int
    improvement_delta: float
    is_best: bool
    elapsed_ms: float


class DesignIterationResponse(BaseModel):
    id: str
    project_id: str
    converged: bool
    iterations_run: int
    best_design: DesignVector
    iteration_history: List[IterationRecord]
    convergence_plot_data: Dict[str, List[float]]
    improvement_summary: str
    elapsed_ms: float
    created_at: datetime


# ── Module 11: Recommendation Engine ────────────────────────────────────────

class RecommendationRequest(BaseModel):
    project_id: str
    domain: OptimizationDomain
    optimization_run_id: Optional[str] = None
    # Inline results if not referencing a run
    pareto_designs: Optional[List[DesignVector]] = None
    trade_study_results: Optional[List[TradeStudyResult]] = None
    constraints: List[ConstraintSpec] = Field(default_factory=list)
    n_recommendations: int = Field(default=3, ge=1, le=10)


class DesignRecommendation(BaseModel):
    rank: int
    title: str
    design: DesignVector
    score: float          # 0–100 composite engineering score
    justification: str
    tradeoff_summary: str
    risk_summary: str
    why_selected: str
    why_alternatives_rejected: str
    critical_tradeoffs: List[str]
    major_risks: List[str]
    remaining_improvements: List[str]
    confidence: float     # 0–1


class RecommendationResponse(BaseModel):
    id: str
    project_id: str
    best_design: DesignRecommendation
    alternatives: List[DesignRecommendation]
    chief_engineer_summary: str
    ai_explanation: str
    decision_rationale: str
    elapsed_ms: float
    created_at: datetime


# ── Project Read Schemas ──────────────────────────────────────────────────────

class OptimizationProjectResponse(BaseModel):
    id: str
    project_id: str
    name: str
    domain: str
    status: str
    runs: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class OptimizationRunDetailResponse(BaseModel):
    id: str
    opt_project_id: str
    algorithm: str
    status: str
    generation: int
    best_score: Optional[float]
    pareto_solutions: List[Dict[str, Any]] = Field(default_factory=list)
    iteration_history: List[Dict[str, Any]] = Field(default_factory=list)
    elapsed_ms: Optional[float]
    created_at: datetime
