"""
Engineering reasoner for design decisions, trade-offs, and recommendations.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class DesignOption:
    name: str
    description: str
    metrics: dict[str, float]
    risks: list[str]
    assumptions: list[str]


@dataclass
class Recommendation:
    recommended: DesignOption
    alternatives: list[DesignOption]
    rationale: str
    trade_offs: list[dict]


class EngineeringReasoner:
    """Makes engineering design recommendations based on constraints and criteria."""

    def evaluate_options(self, options: list[DesignOption], criteria: dict[str, float]) -> Recommendation:
        """Evaluate design options against weighted criteria."""
        scored = []
        for opt in options:
            score = sum(criteria.get(k, 0) * v for k, v in opt.metrics.items())
            scored.append((score, opt))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        
        trade_offs = []
        for i in range(len(scored)):
            for j in range(i+1, len(scored)):
                trade_offs.append({
                    "option_a": scored[i][1].name,
                    "option_b": scored[j][1].name,
                    "score_diff": scored[i][0] - scored[j][0],
                })
        
        return Recommendation(
            recommended=scored[0][1],
            alternatives=[s[1] for s in scored[1:]],
            rationale=f"Option '{scored[0][1].name}' scored highest ({scored[0][0]:.2f})",
            trade_offs=trade_offs,
        )

    def check_constraints(self, design: DesignOption, constraints: dict[str, tuple]) -> list[str]:
        """Check if a design satisfies constraints."""
        violations = []
        for key, (min_val, max_val) in constraints.items():
            if key in design.metrics:
                val = design.metrics[key]
                if val < min_val:
                    violations.append(f"{key}={val:.2f} < minimum {min_val}")
                if val > max_val:
                    violations.append(f"{key}={val:.2f} > maximum {max_val}")
        return violations

    def suggest_alternatives(self, requirement: str, context: str = "") -> list[str]:
        """Suggest alternative design approaches."""
        suggestions = {
            "lightweight": ["Carbon fiber composite", "Aluminum alloy 7075", "Titanium Ti-6Al-4V", "Magnesium alloy"],
            "high_strength": ["Steel 4340", "Titanium alloy", "Carbon fiber", "Inconel"],
            "low_cost": ["Mild steel", "Aluminum 6061", "Polypropylene", "Nylon"],
            "high_temp": ["Inconel 718", "Ceramic matrix composite", "Titanium", "Stainless steel 310"],
            "electrical": ["Copper", "Aluminum", "Gold plating", "Silver"],
        }
        
        for key, options in suggestions.items():
            if key in requirement.lower():
                return options
        return ["Standard material/component", "Consult design standards"]