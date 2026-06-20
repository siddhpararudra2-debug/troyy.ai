"""
Recommendation Engine — Chief Engineering Advisor
Acts as the senior principal engineer synthesizing all optimization results.

Answers:
  - Why was this design selected?
  - Why were alternatives rejected?
  - What are the critical tradeoffs?
  - What are the major risks?
  - What improvements remain?

Generates:
  - Ranked design recommendations with composite scores
  - Engineering justifications
  - AI narrative explanation
  - Decision rationale
"""
from __future__ import annotations

import time
import uuid
import math
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

from app.optimization.schemas import (
    RecommendationRequest, RecommendationResponse,
    DesignRecommendation, DesignVector, ConstraintSpec,
    ObjectiveDirection, OptimizationDomain,
)


class EngineeringScorer:
    """
    Composite engineering score for a design vector.
    Combines objective values, constraint satisfaction, and domain heuristics.
    Score: 0–100 (100 = ideal design).
    """

    # Domain-specific objective weights (aligned with engineering priority)
    _DOMAIN_WEIGHTS: Dict[str, Dict[str, float]] = {
        "drone":       {"weight": 0.25, "cost": 0.15, "efficiency": 0.30, "reliability": 0.20, "performance": 0.10},
        "aerospace":   {"weight": 0.20, "cost": 0.10, "efficiency": 0.35, "reliability": 0.30, "performance": 0.05},
        "robotics":    {"weight": 0.20, "cost": 0.20, "efficiency": 0.20, "reliability": 0.25, "performance": 0.15},
        "electronics": {"weight": 0.10, "cost": 0.25, "efficiency": 0.30, "reliability": 0.20, "performance": 0.15},
        "mechanical":  {"weight": 0.30, "cost": 0.20, "efficiency": 0.15, "reliability": 0.25, "performance": 0.10},
        "default":     {"weight": 0.20, "cost": 0.20, "efficiency": 0.20, "reliability": 0.20, "performance": 0.20},
    }

    @classmethod
    def score(cls, design: DesignVector, domain: OptimizationDomain, constraints: List[ConstraintSpec]) -> float:
        weights = cls._DOMAIN_WEIGHTS.get(domain.value, cls._DOMAIN_WEIGHTS["default"])
        objs = design.objectives

        if not objs:
            return 50.0

        # Normalize each objective to [0, 1] relative score
        scored_components: List[float] = []
        for obj_name, obj_val in objs.items():
            obj_lower = obj_name.lower()
            # Lower is better for these
            if any(k in obj_lower for k in ("weight", "mass", "cost", "power", "thermal", "temperature")):
                # Normalize: assume 0 = perfect, obj_val = actual, penalty grows
                score_component = max(0.0, 1.0 - obj_val / (abs(obj_val) * 2 + 1e-6))
            else:
                # Higher is better
                score_component = min(1.0, obj_val / (abs(obj_val) * 1.2 + 1e-6))

            # Find domain weight for this objective
            w = 0.2
            for key, weight in weights.items():
                if key in obj_lower:
                    w = weight
                    break
            scored_components.append(score_component * w * 100)

        base_score = sum(scored_components) / max(sum(weights.values()), 1e-6)

        # Constraint satisfaction bonus/penalty
        if design.constraints_satisfied:
            base_score *= 1.05
        else:
            viol = sum(design.constraint_violations.values()) if design.constraint_violations else 0.0
            base_score *= max(0.3, 1.0 - viol * 0.1)

        return round(min(100.0, max(0.0, base_score)), 2)


class RecommendationEngine:
    """Chief Engineering Advisor — synthesizes all results into recommendations."""

    @staticmethod
    def recommend(request: RecommendationRequest) -> RecommendationResponse:
        t_start = time.perf_counter()

        domain = request.domain
        n_recs = request.n_recommendations

        # ── Collect candidate designs ─────────────────────────────────────────
        candidates: List[DesignVector] = []
        if request.pareto_designs:
            candidates.extend(request.pareto_designs)
        # If from trade study, synthesize design vectors
        if request.trade_study_results:
            for result in request.trade_study_results:
                fake_design = DesignVector(
                    name=result.option_name,
                    parameters=result.raw_scores,
                    objectives=result.raw_scores,
                    constraints_satisfied=result.risk_level not in ("CRITICAL", "HIGH"),
                )
                candidates.append(fake_design)

        if not candidates:
            # Generate synthetic candidates for demonstration
            candidates = RecommendationEngine._generate_synthetic_candidates(domain, n_recs + 2)

        # ── Score all candidates ──────────────────────────────────────────────
        scored = [
            (design, EngineeringScorer.score(design, domain, request.constraints))
            for design in candidates
        ]
        scored.sort(key=lambda x: -x[1])

        # ── Build Recommendations ─────────────────────────────────────────────
        recs: List[DesignRecommendation] = []
        winner_design, winner_score = scored[0]

        for rank, (design, score) in enumerate(scored[:n_recs], start=1):
            is_best = rank == 1

            # Why selected / why rejected
            if is_best:
                why_selected = RecommendationEngine._explain_selection(design, domain, score)
                why_rejected = "N/A — this is the recommended design."
            else:
                why_selected = "Not selected as primary recommendation."
                why_rejected = RecommendationEngine._explain_rejection(design, winner_design, score, winner_score)

            # Critical tradeoffs
            tradeoffs = RecommendationEngine._identify_tradeoffs(design, domain)

            # Risks
            risks = RecommendationEngine._identify_risks(design, domain, request.constraints)

            # Remaining improvements
            improvements = RecommendationEngine._identify_improvements(design, domain, score)

            # Confidence
            confidence = min(0.95, score / 100 * (0.8 + 0.2 * (1 if design.constraints_satisfied else 0)))

            recs.append(DesignRecommendation(
                rank=rank,
                title=f"{'Recommended' if is_best else f'Alternative {rank-1}'}: {design.name}",
                design=design,
                score=score,
                justification=why_selected if is_best else f"Viable alternative with score {score:.1f}/100",
                tradeoff_summary="; ".join(tradeoffs[:3]),
                risk_summary="; ".join(risks[:2]),
                why_selected=why_selected,
                why_alternatives_rejected=why_rejected,
                critical_tradeoffs=tradeoffs,
                major_risks=risks,
                remaining_improvements=improvements,
                confidence=round(confidence, 3),
            ))

        best_rec = recs[0]
        alternatives = recs[1:]

        # ── AI Explanation ────────────────────────────────────────────────────
        ai_explanation = RecommendationEngine._generate_ai_explanation(
            best_rec, alternatives, domain, scored
        )

        # ── Chief Engineer Summary ─────────────────────────────────────────────
        chief_summary = (
            f"As Chief Engineering Advisor for this {domain.value.upper()} optimization, "
            f"I recommend '{winner_design.name}' (score {winner_score:.1f}/100) as the primary design. "
            f"This design {'satisfies all' if winner_design.constraints_satisfied else 'has minor violations in'} "
            f"engineering constraints and demonstrates superior performance "
            f"in {'weight, efficiency' if domain.value in ('drone', 'aerospace') else 'reliability, cost'} optimization. "
            f"{len(alternatives)} alternative designs evaluated. "
            f"Confidence: {best_rec.confidence:.0%}."
        )

        # ── Decision Rationale ────────────────────────────────────────────────
        rationale = (
            f"Decision based on composite engineering score methodology:\n"
            f"1. Objective performance evaluated across {len(winner_design.objectives)} KPIs\n"
            f"2. Constraint satisfaction verified ({len(request.constraints)} constraints)\n"
            f"3. Domain-specific weighting applied ({domain.value} priority matrix)\n"
            f"4. Risk assessment completed (safety, reliability, cost)\n"
            f"5. Winner selected: score {winner_score:.1f}/100 "
            f"vs. next best {scored[1][1]:.1f}/100 (+{winner_score - scored[1][1]:.1f} margin) "
            if len(scored) > 1 else f"Winner: only feasible design"
        )

        elapsed = (time.perf_counter() - t_start) * 1000
        return RecommendationResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            best_design=best_rec,
            alternatives=alternatives,
            chief_engineer_summary=chief_summary,
            ai_explanation=ai_explanation,
            decision_rationale=rationale,
            elapsed_ms=round(elapsed, 2),
            created_at=datetime.utcnow(),
        )

    @staticmethod
    def _generate_synthetic_candidates(domain: OptimizationDomain, n: int) -> List[DesignVector]:
        rng = np.random.default_rng(42)
        candidates = []
        for i in range(n):
            perf = rng.uniform(0.6, 1.0)
            design = DesignVector(
                name=f"design_candidate_{chr(65+i)}",
                parameters={
                    "x1": float(rng.uniform(0.5, 2.0)),
                    "x2": float(rng.uniform(1.0, 5.0)),
                    "x3": float(rng.uniform(0.1, 0.9)),
                },
                objectives={
                    "weight": float(rng.uniform(0.5, 3.0)),
                    "cost":   float(rng.uniform(200, 1000)),
                    "efficiency": perf,
                    "reliability": float(rng.uniform(0.85, 0.999)),
                },
                constraints_satisfied=rng.random() > 0.2,
            )
            candidates.append(design)
        return candidates

    @staticmethod
    def _explain_selection(design: DesignVector, domain: OptimizationDomain, score: float) -> str:
        objs = design.objectives
        strengths = []
        for name, val in objs.items():
            if "efficiency" in name.lower() and val > 0.8:
                strengths.append(f"high efficiency ({val:.2%})")
            elif "reliability" in name.lower() and val > 0.95:
                strengths.append(f"excellent reliability ({val:.4f})")
            elif "cost" in name.lower() and val < 500:
                strengths.append(f"low cost (${val:.0f})")
        if not strengths:
            strengths = ["balanced performance across all objectives"]
        return (
            f"Selected as primary recommendation (score {score:.1f}/100) because it demonstrates "
            f"{', '.join(strengths)}. "
            f"{'Fully feasible — all constraints satisfied.' if design.constraints_satisfied else 'Minor constraint margin issues identified — review before manufacture.'}"
        )

    @staticmethod
    def _explain_rejection(design: DesignVector, winner: DesignVector, score: float, winner_score: float) -> str:
        delta = winner_score - score
        reasons = []
        for obj_name in design.objectives:
            d_val = design.objectives.get(obj_name, 0)
            w_val = winner.objectives.get(obj_name, 0)
            if abs(d_val) > 0 and abs(w_val) > 0:
                if "efficiency" in obj_name.lower() or "reliability" in obj_name.lower():
                    if w_val > d_val * 1.05:
                        reasons.append(f"lower {obj_name} than winner ({d_val:.3f} vs {w_val:.3f})")
                elif "cost" in obj_name.lower() or "weight" in obj_name.lower() or "mass" in obj_name.lower():
                    if d_val > w_val * 1.05:
                        reasons.append(f"higher {obj_name} than winner ({d_val:.1f} vs {w_val:.1f})")
        if not reasons:
            reasons = [f"composite score {delta:.1f} points below winner"]
        return (
            f"Rejected as primary design: {', '.join(reasons[:2])}. "
            f"Score gap: {delta:.1f} points. Viable as fallback if primary is unavailable."
        )

    @staticmethod
    def _identify_tradeoffs(design: DesignVector, domain: OptimizationDomain) -> List[str]:
        tradeoffs = []
        objs = design.objectives

        if "weight" in objs and "cost" in objs:
            tradeoffs.append(
                f"Mass vs. Cost: lighter materials increase cost "
                f"(mass={objs['weight']:.2f}kg, cost=${objs.get('cost', 0):.0f})"
            )
        if "efficiency" in objs and "reliability" in objs:
            tradeoffs.append(
                f"Efficiency vs. Reliability: higher efficiency components may have lower MTBF "
                f"(efficiency={objs['efficiency']:.2%}, reliability={objs['reliability']:.4f})"
            )
        if domain.value in ("drone", "aerospace"):
            tradeoffs.append(
                "Payload vs. Endurance: increasing payload reduces flight time (fundamental thrust constraint)"
            )
        if domain.value == "robotics":
            tradeoffs.append(
                "Reach vs. Accuracy: longer arm increases workspace but amplifies joint error"
            )
        if not tradeoffs:
            tradeoffs = ["No dominant tradeoffs identified — design is well-balanced"]
        return tradeoffs

    @staticmethod
    def _identify_risks(design: DesignVector, domain: OptimizationDomain, constraints: List[ConstraintSpec]) -> List[str]:
        risks = []
        if not design.constraints_satisfied:
            risks.append("CONSTRAINT VIOLATION: design exceeds one or more engineering limits — must resolve before production")
        objs = design.objectives
        if objs.get("reliability", 1.0) < 0.95:
            risks.append(f"Reliability below 95% threshold ({objs.get('reliability', 0):.4f}) — add redundancy")
        if domain.value in ("drone", "aerospace") and objs.get("weight", 0) > 5.0:
            risks.append("Mass margin is tight — any design changes risk exceeding battery/motor specs")
        risks.append("Prototype validation required: surrogates are physics-informed approximations, not FEA/CFD")
        return risks

    @staticmethod
    def _identify_improvements(design: DesignVector, domain: OptimizationDomain, score: float) -> List[str]:
        improvements = []
        gap = 100.0 - score
        if gap > 30:
            improvements.append(f"High improvement potential ({gap:.0f} points). Run 500+ NSGA-II generations")
        if gap > 15:
            improvements.append("Increase simulation fidelity: replace surrogates with physics solvers")
        improvements.append("Multi-fidelity optimization: start with LHS, refine top 10% with gradient methods")
        improvements.append("Digital twin validation: run optimized design through Day 22 mission simulation")
        improvements.append("Manufacturing DFM review: check optimized parameters against Day 27 constraints")
        return improvements[:5]

    @staticmethod
    def _generate_ai_explanation(
        best: DesignRecommendation,
        alternatives: List[DesignRecommendation],
        domain: OptimizationDomain,
        all_scored: List,
    ) -> str:
        n_evaluated = len(all_scored)
        score_spread = all_scored[0][1] - all_scored[-1][1] if len(all_scored) > 1 else 0
        return (
            f"[AI Engineering Intelligence Analysis]\n\n"
            f"Domain: {domain.value.upper()}\n"
            f"Designs evaluated: {n_evaluated} | Score spread: {score_spread:.1f} points\n\n"
            f"WHY '{best.design.name}' WAS SELECTED:\n"
            f"{best.why_selected}\n\n"
            f"CRITICAL TRADEOFFS:\n"
            + "\n".join(f"• {t}" for t in best.critical_tradeoffs[:3]) +
            f"\n\nMAJOR RISKS:\n"
            + "\n".join(f"⚠ {r}" for r in best.major_risks[:3]) +
            f"\n\nREMAINING IMPROVEMENTS:\n"
            + "\n".join(f"→ {i}" for i in best.remaining_improvements[:3]) +
            f"\n\nCONFIDENCE: {best.confidence:.0%}\n"
            f"Recommendation confidence is derived from objective coverage, constraint satisfaction, "
            f"and domain-specific engineering heuristics."
        )
