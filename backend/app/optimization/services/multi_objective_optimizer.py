"""
Multi-Objective Optimizer — NSGA-II Implementation
Non-dominated Sorting Genetic Algorithm II with:
  - Fast non-dominated sorting
  - Crowding distance assignment
  - Tournament selection with feasibility rule
  - SBX crossover + polynomial mutation
  - Pareto front extraction + hypervolume indicator

All computation is pure numpy — no external solvers required.
"""
from __future__ import annotations

import time
import uuid
import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from app.optimization.schemas import (
    DesignParameter, DesignVector, ObjectiveSpec, ConstraintSpec,
    ParetoFrontRequest, ParetoFrontResponse, ParetoSolution,
    ObjectiveDirection, ConstraintOperator,
)


# ── Internal Design Representation ───────────────────────────────────────────

class _Individual:
    """Internal NSGA-II individual."""
    __slots__ = (
        "x", "objectives", "constraint_violation",
        "rank", "crowding_distance",
        "dominated_by_count", "dominates_set",
    )

    def __init__(self, x: np.ndarray):
        self.x: np.ndarray = x
        self.objectives: np.ndarray = np.zeros(0)
        self.constraint_violation: float = 0.0
        self.rank: int = 0
        self.crowding_distance: float = 0.0
        self.dominated_by_count: int = 0
        self.dominates_set: List[int] = []

    def is_feasible(self) -> bool:
        return self.constraint_violation <= 0.0


# ── NSGA-II Core ─────────────────────────────────────────────────────────────

class NSGA2Solver:
    """
    NSGA-II solver.  All objectives are internally minimized;
    'maximize' objectives are negated before evaluation.
    """

    def __init__(
        self,
        parameters: List[DesignParameter],
        objectives: List[ObjectiveSpec],
        constraints: List[ConstraintSpec],
        population_size: int = 50,
        generations: int = 50,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        seed: Optional[int] = 42,
    ):
        self.parameters = parameters
        self.objectives = objectives
        self.constraints = constraints
        self.pop_size = population_size
        self.generations = generations
        self.cr = crossover_rate
        self.mr = mutation_rate
        self.n_obj = len(objectives)
        self.n_var = len(parameters)
        self.n_con = len(constraints)
        self.lb = np.array([p.lower_bound for p in parameters], dtype=float)
        self.ub = np.array([p.upper_bound for p in parameters], dtype=float)
        self.rng = np.random.default_rng(seed)
        self.history: List[Dict[str, Any]] = []

    # ── Objective Evaluation ──────────────────────────────────────────────────

    def _evaluate_objectives(self, x: np.ndarray) -> np.ndarray:
        """
        Physics-grounded objective evaluation.
        Maps design variables to engineering objectives using domain heuristics.
        In a real system this calls simulation services.
        """
        objs = np.zeros(self.n_obj)
        for i, obj in enumerate(self.objectives):
            val = self._compute_single_objective(x, obj)
            # Negate maximize objectives for internal minimization
            objs[i] = -val if obj.direction == ObjectiveDirection.MAXIMIZE else val
        return objs

    def _compute_single_objective(self, x: np.ndarray, obj: ObjectiveSpec) -> float:
        """
        Compute a single objective from the design vector.
        Uses a physics-inspired surrogate based on objective name.
        """
        # Normalize x to [0,1]
        xn = (x - self.lb) / (self.ub - self.lb + 1e-12)

        name = obj.name.lower()
        if "weight" in name or "mass" in name:
            # mass scales with volume-like combination of parameters
            base = self.ub[0] if len(self.ub) > 0 else 10.0
            return float(np.sum(xn ** 1.5) * base * 0.3 + 0.1)
        elif "cost" in name:
            # Cost is roughly linear in component parameters + premium for high perf
            return float(np.dot(xn, np.linspace(1.0, 3.0, self.n_var)) * 500 + 50)
        elif "efficiency" in name or "performance" in name:
            # Efficiency peaks at a design point ~0.7 normalized
            return float(1.0 - np.exp(-3 * np.sum((xn - 0.7) ** 2)))
        elif "reliability" in name:
            # Reliability improves with higher design margins (larger values)
            return float(1.0 - 0.95 * np.prod(xn + 0.05))
        elif "thermal" in name or "temperature" in name:
            # Thermal scales with power dissipation
            return float(np.sum(xn ** 2) * 150 + 25)
        elif "power" in name:
            return float(np.sum(xn) * (self.ub[-1] if len(self.ub) > 0 else 1.0) * 0.4 + 1.0)
        else:
            # Generic: Rastrigin-like (multi-modal) surrogate for unknown objectives
            A = 10.0
            return float(A * self.n_var + np.sum(xn ** 2 - A * np.cos(2 * math.pi * xn)))

    # ── Constraint Evaluation ────────────────────────────────────────────────

    def _evaluate_constraints(self, x: np.ndarray) -> float:
        """Return total constraint violation (0 = feasible)."""
        if not self.constraints:
            return 0.0
        total = 0.0
        for i, con in enumerate(self.constraints):
            # Map parameter name to x index
            val = x[i % self.n_var]
            viol = self._constraint_violation(val, con)
            if viol > 0:
                total += viol
        return total

    @staticmethod
    def _constraint_violation(val: float, con: ConstraintSpec) -> float:
        if con.operator == ConstraintOperator.LTE:
            return max(0.0, val - con.value)
        elif con.operator == ConstraintOperator.GTE:
            return max(0.0, con.value - val)
        elif con.operator == ConstraintOperator.EQ:
            return abs(val - con.value)
        elif con.operator == ConstraintOperator.RANGE:
            lo, hi = con.value, (con.value_max or con.value)
            return max(0.0, lo - val, val - hi)
        return 0.0

    # ── Genetic Operators ────────────────────────────────────────────────────

    def _sbx_crossover(self, p1: np.ndarray, p2: np.ndarray, eta_c: float = 20.0) -> Tuple[np.ndarray, np.ndarray]:
        """Simulated Binary Crossover (SBX)."""
        c1, c2 = p1.copy(), p2.copy()
        for j in range(self.n_var):
            if self.rng.random() < 0.5:
                if abs(p1[j] - p2[j]) > 1e-10:
                    y1, y2 = min(p1[j], p2[j]), max(p1[j], p2[j])
                    rand = self.rng.random()
                    beta = 1 + (2 * (y1 - self.lb[j]) / (y2 - y1 + 1e-12))
                    alpha = 2 - beta ** (-(eta_c + 1))
                    if rand <= 1.0 / alpha:
                        betaq = (rand * alpha) ** (1.0 / (eta_c + 1))
                    else:
                        betaq = (1.0 / (2.0 - rand * alpha)) ** (1.0 / (eta_c + 1))
                    c1[j] = 0.5 * ((y1 + y2) - betaq * (y2 - y1))
                    c2[j] = 0.5 * ((y1 + y2) + betaq * (y2 - y1))
                    c1[j] = np.clip(c1[j], self.lb[j], self.ub[j])
                    c2[j] = np.clip(c2[j], self.lb[j], self.ub[j])
        return c1, c2

    def _polynomial_mutation(self, x: np.ndarray, eta_m: float = 20.0) -> np.ndarray:
        """Polynomial mutation."""
        child = x.copy()
        for j in range(self.n_var):
            if self.rng.random() < self.mr:
                delta1 = (child[j] - self.lb[j]) / (self.ub[j] - self.lb[j] + 1e-12)
                delta2 = (self.ub[j] - child[j]) / (self.ub[j] - self.lb[j] + 1e-12)
                rand = self.rng.random()
                mut_pow = 1.0 / (eta_m + 1)
                if rand < 0.5:
                    deltaq = (2 * rand + (1 - 2 * rand) * (1 - delta1) ** (eta_m + 1)) ** mut_pow - 1
                else:
                    deltaq = 1 - (2 * (1 - rand) + 2 * (rand - 0.5) * (1 - delta2) ** (eta_m + 1)) ** mut_pow
                child[j] += deltaq * (self.ub[j] - self.lb[j])
                child[j] = np.clip(child[j], self.lb[j], self.ub[j])
        return child

    # ── Non-Dominated Sorting ────────────────────────────────────────────────

    def _fast_nondominated_sort(self, pop: List[_Individual]) -> List[List[int]]:
        """Fast non-dominated sorting — O(M*N^2) where M=objectives, N=population."""
        n = len(pop)
        for ind in pop:
            ind.dominated_by_count = 0
            ind.dominates_set = []

        fronts: List[List[int]] = [[]]

        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                if self._dominates(pop[i], pop[j]):
                    pop[i].dominates_set.append(j)
                elif self._dominates(pop[j], pop[i]):
                    pop[i].dominated_by_count += 1
            if pop[i].dominated_by_count == 0:
                pop[i].rank = 0
                fronts[0].append(i)

        k = 0
        while fronts[k]:
            next_front: List[int] = []
            for i in fronts[k]:
                for j in pop[i].dominates_set:
                    pop[j].dominated_by_count -= 1
                    if pop[j].dominated_by_count == 0:
                        pop[j].rank = k + 1
                        next_front.append(j)
            k += 1
            fronts.append(next_front)

        return [f for f in fronts if f]

    def _dominates(self, a: _Individual, b: _Individual) -> bool:
        """
        Feasibility-first dominance:
        Feasible solutions dominate infeasible ones.
        Among feasible: standard Pareto dominance.
        Among infeasible: less violation dominates.
        """
        if a.is_feasible() and not b.is_feasible():
            return True
        if not a.is_feasible() and b.is_feasible():
            return False
        if not a.is_feasible() and not b.is_feasible():
            return a.constraint_violation < b.constraint_violation
        # Both feasible — standard dominance
        return (
            all(a.objectives[i] <= b.objectives[i] for i in range(self.n_obj))
            and any(a.objectives[i] < b.objectives[i] for i in range(self.n_obj))
        )

    # ── Crowding Distance ────────────────────────────────────────────────────

    def _assign_crowding_distance(self, pop: List[_Individual], front: List[int]) -> None:
        n = len(front)
        if n == 0:
            return
        for i in front:
            pop[i].crowding_distance = 0.0
        for m in range(self.n_obj):
            front_sorted = sorted(front, key=lambda i: pop[i].objectives[m])
            pop[front_sorted[0]].crowding_distance = float("inf")
            pop[front_sorted[-1]].crowding_distance = float("inf")
            obj_range = pop[front_sorted[-1]].objectives[m] - pop[front_sorted[0]].objectives[m]
            if obj_range == 0:
                continue
            for k in range(1, n - 1):
                pop[front_sorted[k]].crowding_distance += (
                    pop[front_sorted[k + 1]].objectives[m]
                    - pop[front_sorted[k - 1]].objectives[m]
                ) / obj_range

    # ── Selection ────────────────────────────────────────────────────────────

    def _tournament_select(self, pop: List[_Individual]) -> _Individual:
        """Binary tournament selection based on rank + crowding distance."""
        a, b = self.rng.choice(len(pop), 2, replace=False)
        pa, pb = pop[a], pop[b]
        if pa.rank < pb.rank:
            return pa
        if pb.rank < pa.rank:
            return pb
        return pa if pa.crowding_distance >= pb.crowding_distance else pb

    # ── Main Loop ────────────────────────────────────────────────────────────

    def run(self) -> Tuple[List[_Individual], List[Dict[str, Any]]]:
        """Run NSGA-II and return Pareto front + iteration history."""
        # Initialize population
        X = self.rng.uniform(self.lb, self.ub, (self.pop_size, self.n_var))
        pop: List[_Individual] = []
        for x in X:
            ind = _Individual(x)
            ind.objectives = self._evaluate_objectives(x)
            ind.constraint_violation = self._evaluate_constraints(x)
            pop.append(ind)

        # Initial fronts + crowding
        fronts = self._fast_nondominated_sort(pop)
        for front in fronts:
            self._assign_crowding_distance(pop, front)

        for gen in range(self.generations):
            t0 = time.perf_counter()

            # Generate offspring
            offspring: List[_Individual] = []
            while len(offspring) < self.pop_size:
                p1 = self._tournament_select(pop)
                p2 = self._tournament_select(pop)
                c1_x, c2_x = self._sbx_crossover(p1.x, p2.x)
                for cx in (c1_x, c2_x):
                    cx = self._polynomial_mutation(cx)
                    child = _Individual(cx)
                    child.objectives = self._evaluate_objectives(cx)
                    child.constraint_violation = self._evaluate_constraints(cx)
                    offspring.append(child)

            # Combine parent + offspring
            combined = pop + offspring

            # Sort combined
            fronts = self._fast_nondominated_sort(combined)
            for front in fronts:
                self._assign_crowding_distance(combined, front)

            # Select next generation
            new_pop: List[_Individual] = []
            for front in fronts:
                if len(new_pop) + len(front) <= self.pop_size:
                    new_pop.extend([combined[i] for i in front])
                else:
                    # Fill remainder by crowding distance (descending)
                    remaining = self.pop_size - len(new_pop)
                    front_sorted = sorted(front, key=lambda i: -combined[i].crowding_distance)
                    new_pop.extend([combined[i] for i in front_sorted[:remaining]])
                    break
            pop = new_pop

            # Record history
            feasible = [ind for ind in pop if ind.is_feasible()]
            best_objs = (
                np.min([ind.objectives for ind in feasible], axis=0).tolist()
                if feasible else [float("inf")] * self.n_obj
            )
            elapsed = (time.perf_counter() - t0) * 1000
            self.history.append({
                "generation": gen + 1,
                "best_objectives": best_objs,
                "feasible_count": len(feasible),
                "elapsed_ms": round(elapsed, 2),
            })

        # Extract final Pareto front (rank == 0)
        pareto = [ind for ind in pop if ind.rank == 0]
        return pareto, self.history


# ── Hypervolume Indicator ─────────────────────────────────────────────────────

def compute_hypervolume(pareto: List[_Individual], ref_point: np.ndarray) -> float:
    """
    2D hypervolume (exact) or approximate for >2 objectives using Monte Carlo.
    """
    if not pareto:
        return 0.0
    n_obj = len(pareto[0].objectives)
    if n_obj == 2:
        # Exact 2D hypervolume
        pts = sorted(pareto, key=lambda ind: ind.objectives[0])
        hv = 0.0
        prev_x = ref_point[0]
        for ind in reversed(pts):
            hv += (prev_x - ind.objectives[0]) * (ref_point[1] - ind.objectives[1])
            prev_x = ind.objectives[0]
        return max(0.0, hv)
    else:
        # Monte Carlo approximation
        rng = np.random.default_rng(0)
        low = np.array([np.min([ind.objectives[m] for ind in pareto]) for m in range(n_obj)])
        high = ref_point
        # Ensure low < high for each dimension (handles negated maximize objectives)
        valid = high > low
        if not valid.all():
            # Swap where high < low
            low_fixed = np.minimum(low, high)
            high_fixed = np.maximum(low, high)
            low, high = low_fixed, high_fixed
        if np.any(high - low <= 0):
            return 0.0
        samples = rng.uniform(
            low,
            high,
            (10000, n_obj),
        )
        dominated = sum(
            1 for s in samples
            if any(all(ind.objectives[m] <= s[m] for m in range(n_obj)) for ind in pareto)
        )
        vol = np.prod(high - low)
        return float(dominated / 10000 * vol)


# ── Service Layer ─────────────────────────────────────────────────────────────

class MultiObjectiveOptimizer:
    """Service wrapping NSGA2Solver with schema translation."""

    @staticmethod
    def optimize(request: ParetoFrontRequest) -> ParetoFrontResponse:
        t_start = time.perf_counter()

        solver = NSGA2Solver(
            parameters=request.design_parameters,
            objectives=request.objectives,
            constraints=request.constraints,
            population_size=request.population_size,
            generations=request.generations,
            crossover_rate=request.crossover_rate,
            mutation_rate=request.mutation_rate,
        )

        pareto_inds, history = solver.run()

        # Reference point: 1.1× nadir
        if pareto_inds:
            all_objs = np.array([ind.objectives for ind in pareto_inds])
            ref_point = all_objs.max(axis=0) * 1.1
        else:
            ref_point = np.ones(len(request.objectives))

        hv = compute_hypervolume(pareto_inds, ref_point)

        # Build parameter names
        param_names = [p.name for p in request.design_parameters]
        obj_names_raw = [o.name for o in request.objectives]

        pareto_solutions: List[ParetoSolution] = []
        for ind in pareto_inds:
            params = {param_names[j]: float(ind.x[j]) for j in range(len(param_names))}
            objs: Dict[str, float] = {}
            for m, obj in enumerate(request.objectives):
                raw = float(ind.objectives[m])
                objs[obj.name] = -raw if obj.direction == ObjectiveDirection.MAXIMIZE else raw

            design = DesignVector(
                name=f"design_{uuid.uuid4().hex[:6]}",
                parameters=params,
                objectives=objs,
                constraints_satisfied=ind.is_feasible(),
                constraint_violations=(
                    {"total_violation": ind.constraint_violation}
                    if not ind.is_feasible() else {}
                ),
            )
            pareto_solutions.append(ParetoSolution(
                design=design,
                front_rank=ind.rank,
                crowding_distance=ind.crowding_distance if ind.crowding_distance != float("inf") else 9999.0,
                hypervolume_contribution=None,
            ))

        # Objective ranges
        obj_ranges: Dict[str, Dict[str, float]] = {}
        if pareto_inds:
            all_objs_arr = np.array([ind.objectives for ind in pareto_inds])
            for m, obj in enumerate(request.objectives):
                obj_ranges[obj.name] = {
                    "min": float(all_objs_arr[:, m].min()),
                    "max": float(all_objs_arr[:, m].max()),
                    "mean": float(all_objs_arr[:, m].mean()),
                }

        # Tradeoff analysis
        tradeoff: Dict[str, Any] = {
            "n_pareto_solutions": len(pareto_solutions),
            "hypervolume": round(hv, 4),
            "objective_conflict_detected": len(request.objectives) > 1 and len(pareto_solutions) > 1,
            "convergence": history[-1] if history else {},
        }

        elapsed = (time.perf_counter() - t_start) * 1000
        return ParetoFrontResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            pareto_front=pareto_solutions,
            total_evaluated=request.population_size * request.generations,
            generations_run=request.generations,
            hypervolume_indicator=hv,
            tradeoff_analysis=tradeoff,
            objective_ranges=obj_ranges,
            elapsed_ms=round(elapsed, 2),
            created_at=datetime.utcnow(),
        )
