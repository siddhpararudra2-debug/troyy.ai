"""
Genetic Designer for Design Evolution
Creates design populations and next generations.
"""
import uuid
import random
import logging
from typing import Dict, Any, List
from app.autonomous_design.design_generator import DesignGenerator

logger = logging.getLogger(__name__)


class GeneticDesigner:
    """
    Handles creating initial design populations and generating next generations.
    """
    def __init__(self):
        self.design_generator = DesignGenerator()

    async def create_initial_population(
        self,
        size: int,
        requirements: str,
    ) -> List[Dict[str, Any]]:
        """
        Create an initial population of design candidates.
        """
        population = []
        for _ in range(size):
            design = await self.design_generator.generate_design(requirements)
            population.append(design)
        return population

    async def create_next_generation(
        self,
        selected_designs: List[Dict[str, Any]],
        target_size: int,
    ) -> List[Dict[str, Any]]:
        """
        Create next generation by combining and mutating selected designs.
        """
        next_gen = selected_designs.copy()

        # Generate new designs via crossover until we hit target size
        while len(next_gen) < target_size:
            # Pick two parents randomly
            parent1, parent2 = random.sample(selected_designs, 2)
            # Crossover them
            child = self._crossover(parent1, parent2)
            next_gen.append(child)

        return next_gen

    def _crossover(
        self,
        parent_a: Dict[str, Any],
        parent_b: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Combine two parent designs into a child design.
        """
        child_params = {}
        params_a = parent_a.get("parameters", {})
        params_b = parent_b.get("parameters", {})
        all_keys = set(params_a.keys()).union(set(params_b.keys()))

        for key in all_keys:
            if key in params_a and key in params_b:
                # Randomly pick from either parent
                child_params[key] = params_a[key] if random.random() < 0.5 else params_b[key]
            elif key in params_a:
                child_params[key] = params_a[key]
            elif key in params_b:
                child_params[key] = params_b[key]

        return {
            "design_id": str(uuid.uuid4()),
            "domain": parent_a.get("domain", parent_b.get("domain")),
            "parameters": child_params,
            "iteration": max(parent_a.get("iteration", 0), parent_b.get("iteration", 0)) + 1,
        }
