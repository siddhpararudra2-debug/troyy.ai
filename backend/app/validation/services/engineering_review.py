"""
Engineering Review
"""
from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class DesignOption:
    name: str
    description: str
    metrics: Dict[str, float] = field(default_factory=dict)
    risks: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)


@dataclass
class EngineeringRecommendation:
    recommended: DesignOption
    alternatives: List[DesignOption]
    rationale: str
    trade_offs: List[str]


class EngineeringReview:
    """Engineering reasoning and design option evaluation"""

    def evaluate_options(
        self,
        options: List[DesignOption],
        criteria: Dict[str, float],
    ) -> EngineeringRecommendation:
        """Evaluate design options"""
        scores = []
        for opt in options:
            score = 0.0
            for name, weight in criteria.items():
                if name in opt.metrics:
                    score += opt.metrics[name] * weight
            scores.append((opt, score))
        sorted_options = sorted(scores, key=lambda x: x[1], reverse=True)
        recommended = sorted_options[0][0]
        alternatives = [opt for opt, _ in sorted_options[1:]]
        return EngineeringRecommendation(
            recommended=recommended,
            alternatives=alternatives,
            rationale="Best overall score highest",
            trade_offs=["Initial pass"],
        )
