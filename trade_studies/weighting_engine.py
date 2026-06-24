"""Weighting Engine - Determines criteria weights for trade studies in Sprint 16."""
from typing import Dict, Any, List


class WeightingEngine:
    """Calculates and manages criteria weights."""

    def __init__(self):
        self.weight_sets: Dict[str, List[float]] = {}

    def equal_weights(self, num_criteria: int) -> List[float]:
        """Generate equal weights for criteria."""
        weight = 1.0 / num_criteria
        return [weight for _ in range(num_criteria)]

    def rank_order_weights(self, ranks: List[int]) -> List[float]:
        """Generate weights based on rank order (1 is highest priority)."""
        total = sum(ranks)
        return [(len(ranks) - r + 1) / total for r in ranks]
