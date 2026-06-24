"""
Self Evaluator — agents evaluate their own outputs against rubrics.
"""
from typing import Dict, List, Any, Callable
import numpy as np
from sprint11.self_improvement.capability_analyzer import CapabilityAnalyzer

class SelfEvaluator:
    """Evaluates agent outputs for self-improvement."""
    
    def __init__(self, capability_analyzer: CapabilityAnalyzer):
        self.capability_analyzer = capability_analyzer
        self.evaluation_history: List[Dict] = []
        self.calibration_data: Dict[str, List[Dict]] = {}
        
    def evaluate_output(self, agent_id: str, task_type: str,
                       output: Any, reference: Any = None,
                       rubric: Dict = None) -> Dict:
        """Evaluate an agent's output."""
        rubric = rubric or self._default_rubric(task_type)
        
        scores = {}
        for criterion in rubric["criteria"]:
            scorer_name = criterion.get("scorer", "default")
            scorer = self._get_scorer(scorer_name)
            score = scorer(output, reference, criterion)
            scores[criterion["name"]] = score
            
        # Weighted overall
        overall = sum(
            scores[c["name"]] * c.get("weight", 1.0)
            for c in rubric["criteria"]
        ) / sum(c.get("weight", 1.0) for c in rubric["criteria"])
        
        # Record evaluation
        evaluation = {
            "agent_id": agent_id,
            "task_type": task_type,
            "scores": scores,
            "overall": overall,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat()
        }
        self.evaluation_history.append(evaluation)
        
        # Update capabilities
        for criterion_name, score in scores.items():
            self.capability_analyzer.record_capability(
                agent_id, criterion_name, score,
                evidence={"task_type": task_type, "output_hash": str(hash(str(output)))}
            )
            
        # Update calibration
        if reference is not None:
            self.calibration_data.setdefault(agent_id, []).append({
                "task_type": task_type,
                "self_score": overall,
                "has_reference": True
            })
            
        return evaluation
        
    def evaluate_batch(self, agent_id: str, evaluations: List[Dict]) -> Dict:
        """Evaluate a batch of outputs."""
        results = []
        for ev in evaluations:
            result = self.evaluate_output(
                agent_id,
                ev["task_type"],
                ev["output"],
                ev.get("reference"),
                ev.get("rubric")
            )
            results.append(result)
            
        avg_overall = sum(r["overall"] for r in results) / len(results)
        return {
            "agent_id": agent_id,
            "evaluations": results,
            "average_score": avg_overall,
            "count": len(results),
            "strongest_task": max(results, key=lambda r: r["overall"])["task_type"],
            "weakest_task": min(results, key=lambda r: r["overall"])["task_type"]
        }
        
    def _default_rubric(self, task_type: str) -> Dict:
        """Get default rubric for task type."""
        rubrics = {
            "reasoning": {
                "criteria": [
                    {"name": "reasoning", "weight": 0.4, "scorer": "logic"},
                    {"name": "completeness", "weight": 0.3, "scorer": "coverage"},
                    {"name": "accuracy", "weight": 0.3, "scorer": "correctness"}
                ]
            },
            "coding": {
                "criteria": [
                    {"name": "coding", "weight": 0.4, "scorer": "code_quality"},
                    {"name": "correctness", "weight": 0.4, "scorer": "tests_pass"},
                    {"name": "efficiency", "weight": 0.2, "scorer": "complexity"}
                ]
            },
            "design": {
                "criteria": [
                    {"name": "design", "weight": 0.3, "scorer": "feasibility"},
                    {"name": "safety", "weight": 0.3, "scorer": "safety_check"},
                    {"name": "performance", "weight": 0.2, "scorer": "performance"},
                    {"name": "cost", "weight": 0.2, "scorer": "cost_estimate"}
                ]
            },
            "planning": {
                "criteria": [
                    {"name": "planning", "weight": 0.4, "scorer": "completeness"},
                    {"name": "feasibility", "weight": 0.3, "scorer": "feasibility"},
                    {"name": "efficiency", "weight": 0.3, "scorer": "optimality"}
                ]
            }
        }
        return rubrics.get(task_type, rubrics["reasoning"])
        
    def _get_scorer(self, scorer_name: str) -> Callable:
        """Get scoring function by name."""
        scorers = {
            "default": self._score_default,
            "logic": self._score_logic,
            "coverage": self._score_coverage,
            "correctness": self._score_correctness,
            "code_quality": self._score_code_quality,
            "tests_pass": self._score_tests_pass,
            "complexity": self._score_complexity,
            "feasibility": self._score_feasibility,
            "safety_check": self._score_safety,
            "performance": self._score_performance,
            "cost_estimate": self._score_cost,
            "completeness": self._score_completeness,
            "optimality": self._score_optimality,
        }
        return scorers.get(scorer_name, self._score_default)
        
    def _score_default(self, output, reference, criterion) -> float:
        """Default scorer — checks if output is non-empty."""
        if output is None:
            return 0.0
        if isinstance(output, (str, list, dict)) and len(output) == 0:
            return 0.0
        return 0.7  # Neutral score
        
    def _score_logic(self, output, reference, criterion) -> float:
        """Score logical coherence."""
        if not isinstance(output, str):
            output = str(output)
        markers = ["therefore", "because", "since", "thus", "hence", "implies"]
        score = 0.5
        for marker in markers:
            if marker in output.lower():
                score += 0.1
        return min(1.0, score)
        
    def _score_coverage(self, output, reference, criterion) -> float:
        """Score completeness of coverage."""
        if reference is None:
            return 0.7
        if isinstance(output, str) and isinstance(reference, (list, set)):
            covered = sum(1 for item in reference if str(item) in output)
            return covered / len(reference) if reference else 0.0
        return 0.7
        
    def _score_correctness(self, output, reference, criterion) -> float:
        """Score correctness against reference."""
        if reference is None:
            return 0.7
        if output == reference:
            return 1.0
        if isinstance(output, (int, float)) and isinstance(reference, (int, float)):
            if reference == 0:
                return 1.0 if output == 0 else 0.0
            return max(0.0, 1.0 - abs(output - reference) / abs(reference))
        return 0.5
        
    def _score_code_quality(self, output, reference, criterion) -> float:
        """Score code quality heuristics."""
        if not isinstance(output, str):
            return 0.3
        score = 0.5
        if "def " in output or "function " in output:
            score += 0.1
        if "return" in output:
            score += 0.1
        if "\n" in output and len(output) > 50:
            score += 0.1
        if "import" in output:
            score += 0.1
        return min(1.0, score)
        
    def _score_tests_pass(self, output, reference, criterion) -> float:
        """Score based on test results."""
        if isinstance(output, dict) and "tests_passed" in output:
            total = output.get("tests_total", 1)
            passed = output.get("tests_passed", 0)
            return passed / total if total > 0 else 0.0
        return 0.7
        
    def _score_complexity(self, output, reference, criterion) -> float:
        """Score computational complexity (lower is better)."""
        if isinstance(output, dict) and "complexity" in output:
            return max(0.0, 1.0 - output["complexity"] / 100)
        return 0.7
        
    def _score_feasibility(self, output, reference, criterion) -> float:
        """Score design feasibility."""
        if isinstance(output, dict):
            if output.get("feasible") is True:
                return 0.9
            if output.get("feasible") is False:
                return 0.2
            if "constraints_violated" in output:
                violations = len(output["constraints_violated"])
                return max(0.0, 1.0 - violations * 0.2)
        return 0.7
        
    def _score_safety(self, output, reference, criterion) -> float:
        """Score safety assessment."""
        if isinstance(output, dict):
            if output.get("safety_issues"):
                return max(0.0, 1.0 - len(output["safety_issues"]) * 0.3)
            if output.get("safety_verified") is True:
                return 1.0
        return 0.8
        
    def _score_performance(self, output, reference, criterion) -> float:
        """Score performance metrics."""
        if isinstance(output, dict) and "performance" in output:
            return min(1.0, output["performance"])
        return 0.7
        
    def _score_cost(self, output, reference, criterion) -> float:
        """Score cost efficiency."""
        if isinstance(output, dict) and "cost" in output:
            if reference and "cost" in reference:
                ratio = output["cost"] / reference["cost"] if reference["cost"] > 0 else 1.0
                return max(0.0, 1.0 - (ratio - 1.0))
        return 0.7
        
    def _score_completeness(self, output, reference, criterion) -> float:
        """Score planning completeness."""
        if isinstance(output, (list, dict)):
            length = len(output)
            return min(1.0, length / 10)
        if isinstance(output, str):
            return min(1.0, len(output) / 500)
        return 0.5
        
    def _score_optimality(self, output, reference, criterion) -> float:
        """Score optimality of solution."""
        if isinstance(output, dict) and "optimality_gap" in output:
            return max(0.0, 1.0 - output["optimality_gap"])
        return 0.7
