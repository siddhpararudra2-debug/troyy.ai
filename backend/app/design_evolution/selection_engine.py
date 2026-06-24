"""
Selection Engine for Design Evolution
Selects top-performing design candidates from a population.
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class SelectionEngine:
    """
    Selects design candidates for reproduction based on their evaluation scores.
    """
    def select_top(
        self,
        population: List[Dict[str, Any]],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """
        Select the top K designs from the population based on score.
        """
        sorted_pop = sorted(
            population,
            key=lambda x: x.get("evaluation", {}).get("overall_score", 0),
            reverse=True,
        )
        return sorted_pop[:top_k]
