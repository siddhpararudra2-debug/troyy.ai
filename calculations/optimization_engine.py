"""
Optimization Engine for Engineering OS.
Optimizes designs for weight, cost, performance, etc.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Any, Callable, Tuple
from datetime import datetime
import uuid
import random
import math


class ObjectiveType(str, Enum):
    """Types of optimization objectives."""
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"
    TARGET = "target"


class OptimizationType(str, Enum):
    """Types of optimization."""
    SINGLE_OBJECTIVE = "single_objective"
    MULTI_OBJECTIVE = "multi_objective"
    CONSTRAINED = "constrained"
    UNCONSTRAINED = "unconstrained"


@dataclass
class Objective:
    """An optimization objective."""
    name: str = ""
    objective_type: ObjectiveType = ObjectiveType.MINIMIZE
    weight: float = 1.0  # For multi-objective, relative importance (0-1)
    description: str = ""
    priority: float = 1.0
    target_value: Optional[float] = None  # Optional target
    penalty_function: Optional[Callable] = None


@dataclass
class DesignVariable:
    """A design parameter to optimize."""
    name: str = ""
    description: str = ""
    lower_bound: float = 0.0
    upper_bound: float = 100.0
    initial_value: float = 50.0
    discrete: bool = False  # True for integer values
    step_size: Optional[float] = None  # For discrete variables
    
    def get_random_value(self) -> float:
        """Generate random value within bounds."""
        if self.discrete and self.step_size:
            steps = int((self.upper_bound - self.lower_bound) / self.step_size)
            step = random.randint(0, steps)
            return self.lower_bound + step * self.step_size
        else:
            return random.uniform(self.lower_bound, self.upper_bound)


@dataclass
class Solution:
    """A candidate solution."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    design_variables: Dict[str, float] = field(default_factory=dict)
    objective_values: Dict[str, float] = field(default_factory=dict)
    fitness: float = 0.0  # Overall fitness score
    feasible: bool = True
    constraints_violated: List[str] = field(default_factory=list)
    generation: int = 0


@dataclass
class OptimizationRun:
    """Record of an optimization run."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    run_id: str = ""
    design_id: str = ""
    optimization_type: OptimizationType = OptimizationType.SINGLE_OBJECTIVE
    objectives: List[Objective] = field(default_factory=list)
    variables: List[DesignVariable] = field(default_factory=list)
    
    # Configuration
    algorithm: str = "genetic_algorithm"
    max_generations: int = 100
    population_size: int = 50
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    constraints: List[Any] = field(default_factory=list)
    
    # Results
    best_solution: Optional[Solution] = None
    solutions_history: List[Solution] = field(default_factory=list)
    pareto_front: List[Solution] = field(default_factory=list)
    
    # Statistics
    generations_completed: int = 0
    fitness_improvement: float = 0.0  # Percent improvement
    convergence_rate: float = 0.0
    
    # Timing
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    total_time_seconds: float = 0.0

    @property
    def generations(self) -> int:
        return self.generations_completed

    @property
    def best_fitness(self) -> Optional[float]:
        return self.best_solution.fitness if self.best_solution else None

    @property
    def design_variables(self) -> List[DesignVariable]:
        return self.variables

    @design_variables.setter
    def design_variables(self, value: List[DesignVariable]):
        self.variables = value


class OptimizationEngine:
    """Engine for design optimization."""

    def __init__(self):
        self.run_count = 0
        self.objective_functions = {}

    async def create_optimization(
        self,
        run_id: str,
        design_id: str,
        objectives: Optional[List[Objective]] = None,
        variables: Optional[List[DesignVariable]] = None,
        optimization_type: OptimizationType = OptimizationType.MULTI_OBJECTIVE
    ) -> OptimizationRun:
        """Create a new optimization run."""
        self.run_count += 1
        
        run = OptimizationRun(
            run_id=run_id,
            design_id=design_id,
            objectives=objectives or [],
            variables=variables or [],
            optimization_type=optimization_type
        )
        
        return run

    async def add_objective(self, run: OptimizationRun, objective: Objective) -> OptimizationRun:
        """Add an optimization objective."""
        run.objectives.append(objective)
        return run

    async def add_design_variable(self, run: OptimizationRun, variable: DesignVariable) -> OptimizationRun:
        """Add a design variable."""
        run.variables.append(variable)
        return run

    async def optimize_genetic_algorithm(
        self,
        optimization_run: OptimizationRun,
        constraint_checker: Optional[Callable] = None,
        fitness_function: Optional[Callable] = None,
        max_generations: int = 100,
        population_size: int = 50,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8
    ) -> OptimizationRun:
        """Run genetic algorithm optimization."""
        
        # Initialize population
        population = self._create_initial_population(
            optimization_run.variables,
            population_size
        )
        
        best_fitness = float('-inf')
        best_solution = None
        fitness_history = []
        
        for generation in range(max_generations):
            # Evaluate fitness
            for solution in population:
                solution.generation = generation
                
                # Check constraints
                if constraint_checker:
                    feasible, violations = constraint_checker(solution.design_variables)
                    solution.feasible = feasible
                    solution.constraints_violated = violations
                
                # Calculate fitness
                if fitness_function:
                    solution.fitness = fitness_function(solution.design_variables)
                else:
                    solution.fitness = self._default_fitness(
                        solution.design_variables,
                        optimization_run.objectives
                    )
                
                # Penalize infeasible solutions
                if not solution.feasible:
                    solution.fitness *= 0.5
                
                optimization_run.solutions_history.append(solution)
                
                # Track best
                if solution.fitness > best_fitness and solution.feasible:
                    best_fitness = solution.fitness
                    best_solution = solution
            
            fitness_history.append(best_fitness)
            
            # Selection
            selected = self._tournament_selection(population, 2)
            
            # Crossover and mutation
            new_population = []
            for i in range(0, len(selected), 2):
                parent1 = selected[i]
                parent2 = selected[i + 1] if i + 1 < len(selected) else selected[0]
                
                if random.random() < crossover_rate:
                    child1, child2 = self._crossover(
                        parent1,
                        parent2,
                        optimization_run.variables
                    )
                else:
                    child1, child2 = parent1, parent2
                
                if random.random() < mutation_rate:
                    child1 = self._mutate(child1, optimization_run.variables)
                if random.random() < mutation_rate:
                    child2 = self._mutate(child2, optimization_run.variables)
                
                new_population.extend([child1, child2])
            
            population = new_population[:population_size]
            
            # Convergence check
            if generation > 10 and len(fitness_history) > 10:
                recent_improvement = fitness_history[-1] - fitness_history[-10]
                if recent_improvement < 1e-6:
                    # Converged
                    break
        
        optimization_run.best_solution = best_solution
        optimization_run.generations_completed = len(fitness_history)
        
        if len(fitness_history) > 1:
            optimization_run.fitness_improvement = (
                (fitness_history[-1] - fitness_history[0]) / abs(fitness_history[0]) * 100
                if fitness_history[0] != 0 else 0
            )
        
        optimization_run.completed_at = datetime.utcnow()
        
        return optimization_run

    def _create_initial_population(
        self,
        variables: List[DesignVariable],
        population_size: int
    ) -> List[Solution]:
        """Create initial random population."""
        population = []
        
        for _ in range(population_size):
            design_vars = {
                var.name: var.get_random_value()
                for var in variables
            }
            solution = Solution(design_variables=design_vars)
            population.append(solution)
        
        return population

    def _default_fitness(
        self,
        design_variables: Dict[str, float],
        objectives: List[Objective]
    ) -> float:
        """Calculate default fitness from objectives."""
        total_fitness = 0.0
        
        for objective in objectives:
            # Mock objective calculation
            if "weight" in objective.name.lower():
                # Minimize weight
                weight = design_variables.get("weight", 1.0)
                score = 1.0 / (1.0 + weight)
            elif "cost" in objective.name.lower():
                # Minimize cost
                cost = design_variables.get("cost", 1.0)
                score = 1.0 / (1.0 + cost)
            elif "performance" in objective.name.lower():
                # Maximize performance
                score = design_variables.get("performance", 0.5)
            else:
                score = 0.5
            
            if objective.objective_type == ObjectiveType.MINIMIZE:
                score = 1.0 - score
            
            total_fitness += score * objective.weight
        
        return total_fitness

    def _tournament_selection(
        self,
        population: List[Solution],
        tournament_size: int
    ) -> List[Solution]:
        """Tournament selection."""
        selected = []
        
        for _ in range(len(population)):
            tournament = random.sample(population, min(tournament_size, len(population)))
            winner = max(tournament, key=lambda s: s.fitness if s.feasible else -float('inf'))
            selected.append(winner)
        
        return selected

    def _crossover(
        self,
        parent1: Solution,
        parent2: Solution,
        variables: List[DesignVariable]
    ) -> Tuple[Solution, Solution]:
        """Single-point crossover."""
        crossover_point = random.randint(0, len(variables) - 1)
        
        child1_vars = {}
        child2_vars = {}
        
        for i, var in enumerate(variables):
            if i < crossover_point:
                child1_vars[var.name] = parent1.design_variables.get(var.name, var.initial_value)
                child2_vars[var.name] = parent2.design_variables.get(var.name, var.initial_value)
            else:
                child1_vars[var.name] = parent2.design_variables.get(var.name, var.initial_value)
                child2_vars[var.name] = parent1.design_variables.get(var.name, var.initial_value)
        
        child1 = Solution(design_variables=child1_vars)
        child2 = Solution(design_variables=child2_vars)
        
        return child1, child2

    def _mutate(
        self,
        solution: Solution,
        variables: List[DesignVariable]
    ) -> Solution:
        """Gaussian mutation."""
        mutated_vars = solution.design_variables.copy()
        
        mutation_var = random.choice(variables)
        old_value = mutated_vars.get(mutation_var.name, mutation_var.initial_value)
        
        # Gaussian mutation with standard deviation
        std_dev = (mutation_var.upper_bound - mutation_var.lower_bound) * 0.1
        new_value = old_value + random.gauss(0, std_dev)
        
        # Clamp to bounds
        new_value = max(mutation_var.lower_bound, min(mutation_var.upper_bound, new_value))
        mutated_vars[mutation_var.name] = new_value
        
        return Solution(design_variables=mutated_vars)
