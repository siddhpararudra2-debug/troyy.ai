"""
Alternative Evaluator - Evaluates and compares design alternatives.

Capabilities:
- Alternative Evaluation
- Technology Assessment
- Risk Comparison
- Architecture Ranking
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from trade_studies.tradeoff_engine import TradeoffEngine, Alternative


class AlternativeEvaluator:
    """Evaluates design alternatives with comprehensive analysis."""

    def __init__(self):
        self._evaluations: Dict[str, Dict[str, Any]] = {}

    def evaluate_technologies(self, alternatives: List[Dict[str, Any]],
                               criteria: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate technology alternatives."""
        engine = TradeoffEngine()
        for c in criteria:
            engine.add_criterion(c["name"], c.get("weight", 1.0), c.get("is_benefit", True))
        for alt_data in alternatives:
            alt = engine.add_alternative(alt_data["name"], alt_data.get("description"))
            for cname, score in alt_data.get("scores", {}).items():
                alt.set_score(cname, score)
            alt.risks = alt_data.get("risks", [])
            alt.costs = alt_data.get("costs", {})
        engine.normalize_scores()
        return engine.evaluate()

    def rank_architectures(self, architectures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank system architectures."""
        scored = []
        for arch in architectures:
            score = 0.0
            if arch.get("complexity"):
                score += (10 - arch["complexity"]) * 0.3
            if arch.get("performance"):
                score += arch["performance"] * 0.3
            if arch.get("cost"):
                score += (10 - arch["cost"]) * 0.2
            if arch.get("reliability"):
                score += arch["reliability"] * 0.2
            scored.append({**arch, "total_score": round(score, 2)})
        return sorted(scored, key=lambda x: x["total_score"], reverse=True)