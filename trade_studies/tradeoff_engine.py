"""
Tradeoff Engine - Evaluates design tradeoffs and compares alternatives.

Capabilities:
- Design Tradeoffs
- Architecture Comparison
- Multi-Criteria Decision Analysis
"""

import uuid
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime


class Criterion:
    """A criterion for tradeoff analysis."""

    def __init__(self, name: str, weight: float = 1.0, is_benefit: bool = True,
                 description: Optional[str] = None):
        self.name = name
        self.weight = weight
        self.is_benefit = is_benefit  # True=higher is better, False=lower is better
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "weight": self.weight,
            "is_benefit": self.is_benefit,
            "description": self.description,
        }


class Alternative:
    """An alternative being evaluated."""

    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description
        self.scores: Dict[str, float] = {}
        self.costs: Dict[str, float] = {}
        self.risks: List[str] = []

    def set_score(self, criterion_name: str, score: float):
        self.scores[criterion_name] = score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "scores": self.scores,
            "costs": self.costs,
            "risks": self.risks,
        }


class TradeoffEngine:
    """Evaluates design alternatives using multi-criteria decision analysis."""

    def __init__(self):
        self._criteria: Dict[str, Criterion] = {}
        self._alternatives: List[Alternative] = []

    def add_criterion(self, name: str, weight: float = 1.0,
                      is_benefit: bool = True, description: Optional[str] = None) -> Criterion:
        criterion = Criterion(name, weight, is_benefit, description)
        self._criteria[name] = criterion
        return criterion

    def add_alternative(self, name: str, description: Optional[str] = None) -> Alternative:
        alt = Alternative(name, description)
        self._alternatives.append(alt)
        return alt

    def evaluate(self) -> Dict[str, Any]:
        """Perform weighted sum evaluation of all alternatives."""
        results = []
        total_weight = sum(c.weight for c in self._criteria.values())

        for alt in self._alternatives:
            weighted_score = 0.0
            details = []

            for cname, criterion in self._criteria.items():
                score = alt.scores.get(cname, 0)
                normalized = score / (total_weight / len(self._criteria)) if total_weight > 0 else score
                weighted = normalized * criterion.weight
                weighted_score += weighted

                details.append({
                    "criterion": cname,
                    "raw_score": score,
                    "weight": criterion.weight,
                    "weighted_score": weighted,
                })

            results.append({
                "alternative": alt.name,
                "description": alt.description,
                "total_score": round(weighted_score, 2),
                "details": details,
                "risks": alt.risks,
                "costs": alt.costs,
            })

        results.sort(key=lambda x: x["total_score"], reverse=True)

        return {
            "method": "Weighted Sum Model",
            "criteria": [c.to_dict() for c in self._criteria.values()],
            "results": results,
            "recommendation": results[0]["alternative"] if results else None,
            "evaluated_at": datetime.utcnow().isoformat(),
        }

    def normalize_scores(self) -> List[Alternative]:
        """Normalize scores to 0-1 range across alternatives."""
        if not self._alternatives:
            return []

        for criterion in self._criteria.values():
            scores = [alt.scores.get(criterion.name, 0) for alt in self._alternatives]
            if not scores:
                continue
            min_s, max_s = min(scores), max(scores)
            if max_s == min_s:
                continue
            for alt in self._alternatives:
                raw = alt.scores.get(criterion.name, 0)
                if criterion.is_benefit:
                    alt.scores[criterion.name] = (raw - min_s) / (max_s - min_s)
                else:
                    alt.scores[criterion.name] = 1 - (raw - min_s) / (max_s - min_s)

        return self._alternatives

    def get_alternatives(self) -> List[Alternative]:
        return self._alternatives