"""
Evaluation Engine — scores experiment outcomes against rubrics.
"""
from typing import Dict, List, Any, Callable
import numpy as np

class EvaluationEngine:
    """Evaluates experiment outcomes using configurable rubrics."""
    
    def __init__(self):
        self.rubrics: Dict[str, Dict] = {}
        self.custom_scorers: Dict[str, Callable] = {}
        
    def register_rubric(self, name: str, rubric: Dict) -> None:
        """Register an evaluation rubric.
        rubric: {
            "criteria": [
                {"name": "accuracy", "weight": 0.4, "target": 0.95},
                {"name": "efficiency", "weight": 0.3, "target": 0.8},
                ...
            ],
            "pass_threshold": 0.7
        }
        """
        self.rubrics[name] = rubric
        
    def register_scorer(self, name: str, scorer: Callable) -> None:
        """Register a custom scoring function."""
        self.custom_scorers[name] = scorer
        
    def evaluate(self, rubric_name: str, metrics: Dict[str, float]) -> Dict:
        """Evaluate metrics against a rubric."""
        rubric = self.rubrics.get(rubric_name)
        if not rubric:
            raise ValueError(f"Rubric {rubric_name} not found")
            
        criteria_scores = []
        weighted_sum = 0.0
        total_weight = 0.0
        
        for criterion in rubric["criteria"]:
            name = criterion["name"]
            weight = criterion.get("weight", 1.0)
            target = criterion.get("target", 1.0)
            
            actual = metrics.get(name, 0.0)
            
            # Compute score: ratio to target, capped at 1.0
            if target > 0:
                score = min(1.0, actual / target)
            else:
                score = 1.0 if actual == 0 else 0.0
                
            criteria_scores.append({
                "name": name,
                "actual": actual,
                "target": target,
                "score": score,
                "weight": weight
            })
            
            weighted_sum += score * weight
            total_weight += weight
            
        overall = weighted_sum / total_weight if total_weight > 0 else 0.0
        passed = overall >= rubric.get("pass_threshold", 0.7)
        
        return {
            "rubric": rubric_name,
            "criteria_scores": criteria_scores,
            "overall_score": overall,
            "pass_threshold": rubric.get("pass_threshold", 0.7),
            "passed": passed,
            "verdict": "PASS" if passed else "FAIL"
        }
        
    def compare_agents(self, agent_scores: Dict[str, Dict[str, float]],
                      rubric_name: str) -> Dict:
        """Compare multiple agents on a rubric."""
        results = {}
        for agent_id, metrics in agent_scores.items():
            results[agent_id] = self.evaluate(rubric_name, metrics)
            
        # Rank agents
        ranking = sorted(
            results.items(),
            key=lambda x: x[1]["overall_score"],
            reverse=True
        )
        
        return {
            "rubric": rubric_name,
            "results": results,
            "ranking": [{"agent_id": aid, "score": r["overall_score"]}
                       for aid, r in ranking]
        }
