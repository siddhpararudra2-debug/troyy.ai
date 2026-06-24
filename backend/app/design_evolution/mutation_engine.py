"""
Mutation Engine for Design Evolution
Mutates design candidates to explore design space.
"""
import uuid
import random
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class MutationEngine:
    """
    Handles mutating design parameters to explore new design possibilities.
    """
    def mutate(self, design: Dict[str, Any], mutation_rate: float = 0.2) -> Dict[str, Any]:
        """
        Mutate a design candidate by randomly modifying parameters.
        """
        mutated_params = design.get("parameters", {}).copy()

        for key, value in mutated_params.items():
            if random.random() < mutation_rate:
                if isinstance(value, (int, float)):
                    # Mutate numerical value by ±10%
                    delta = value * 0.1 * (random.random() * 2 - 1)
                    mutated_params[key] = max(0, value + delta)

        return {
            "design_id": str(uuid.uuid4()),
            "domain": design.get("domain"),
            "parameters": mutated_params,
            "iteration": design.get("iteration", 0) + 1,
        }
