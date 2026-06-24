"""
Evolution Engine for Design Evolution
Orchestrates genetic algorithm-based design optimization.
"""
import uuid
import logging
from typing import Dict, Any, List
from app.design_evolution.genetic_designer import GeneticDesigner
from app.design_evolution.mutation_engine import MutationEngine
from app.design_evolution.selection_engine import SelectionEngine
from app.autonomous_design.design_evaluator import DesignEvaluator

logger = logging.getLogger(__name__)


class EvolutionEngine:
    """
    Orchestrates the evolution of design candidates using genetic algorithms.
    """
    def __init__(self):
        self.genetic_designer = GeneticDesigner()
        self.mutation_engine = MutationEngine()
        self.selection_engine = SelectionEngine()
        self.evaluator = DesignEvaluator()

    async def evolve_designs(
        self,
        requirements: str,
        population_size: int = 10,
        generations: int = 10,
    ) -> Dict[str, Any]:
        """
        Evolve a population of design candidates over multiple generations.
        """
        # Initialize population
        population = self.genetic_designer.create_initial_population(population_size, requirements)
        best_designs = []

        for gen in range(generations):
            # Evaluate all designs
            evaluated_population = []
            for design in population:
                evaluation = await self.evaluator.evaluate_design(design, requirements)
                design["evaluation"] = evaluation
                evaluated_population.append(design)

            # Select the best designs
            selected = self.selection_engine.select_top(evaluated_population, top_k=population_size // 2)
            best_designs = selected  # Keep track of best for output

            # Create next generation via mutation and crossover
            next_generation = self.genetic_designer.create_next_generation(selected, population_size)
            population = next_generation

            logger.info(f"Generation {gen+1}: Best score = {selected[0]['evaluation']['overall_score']:.2f}")

        return {
            "final_population": population,
            "best_designs": best_designs,
            "generations": generations,
        }
