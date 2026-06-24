"""Decision Matrix - Multi-Criteria Decision Analysis for Sprint 16."""
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime


class DecisionMatrix:
    """Creates and analyzes decision matrices for trade studies."""

    def __init__(self):
        self.matrices: Dict[str, Dict[str, Any]] = {}

    def create_matrix(
        self,
        name: str,
        alternatives: List[Dict[str, Any]],
        criteria: List[Dict[str, Any]],
        scores: Optional[List[List[float]]] = None,
    ) -> Dict[str, Any]:
        """Create a new decision matrix."""
        matrix_id = str(uuid.uuid4())
        matrix = {
            "id": matrix_id,
            "name": name,
            "alternatives": alternatives,
            "criteria": criteria,
            "scores": scores or [[0.0 for _ in criteria] for _ in alternatives],
            "created_at": datetime.utcnow().isoformat(),
        }
        self.matrices[matrix_id] = matrix
        return matrix

    def calculate_scores(
        self,
        matrix_id: str,
        weights: List[float],
    ) -> Optional[Dict[str, Any]]:
        """Calculate weighted scores for alternatives."""
        if matrix_id not in self.matrices:
            return None
        matrix = self.matrices[matrix_id]
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        results = []
        for alt_idx, alt in enumerate(matrix["alternatives"]):
            score = 0.0
            for crit_idx, weight in enumerate(normalized_weights):
                score += matrix["scores"][alt_idx][crit_idx] * weight
            results.append({"alternative": alt, "score": score})
        results_sorted = sorted(results, key=lambda x: x["score"], reverse=True)
        return {"matrix": matrix, "results": results_sorted}
