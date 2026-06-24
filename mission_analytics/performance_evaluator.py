"""Performance Evaluator - Module 9 for Sprint 13."""
from typing import Dict, Any, List


class PerformanceEvaluator:
    def __init__(self):
        self.evaluations: List[Dict[str, Any]] = []

    def evaluate_performance(
        self,
        mission_id: str,
        planned: Dict[str, Any],
        actual: Dict[str, Any]
    ) -> Dict[str, Any]:
        evaluation = {
            "mission_id": mission_id,
            "planned": planned,
            "actual": actual,
            "score": 0.85,
            "deviations": [],
        }
        
        for key in planned:
            if key in actual and planned[key] != actual[key]:
                evaluation["deviations"].append({
                    "metric": key,
                    "planned": planned[key],
                    "actual": actual[key],
                })
        
        self.evaluations.append(evaluation)
        return evaluation
