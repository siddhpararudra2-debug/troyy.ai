"""
Troy — Recommendation Service
Generates actionable engineering recommendations based on calculation results,
constraint violations, and safety margin analysis.
"""

from __future__ import annotations

import logging
from typing import List

from app.solver.models.domain_models import (
    RecommendationData,
    RecommendationItem,
    SolverState,
)

logger = logging.getLogger("solver.services.recommendation")


class RecommendationService:
    """Generates design recommendations based on calculation results."""

    async def generate_recommendations(self, state: SolverState) -> RecommendationData:
        """
        Analyze the solver state and return structured recommendations.
        """
        logger.info(f"Generating recommendations for solver session {state.session_id}")

        results = state.calculation_results
        domain = state.domain
        items: List[RecommendationItem] = []

        # ── Drone domain-specific recommendations ────────────────
        if domain == "drones":
            t_flight = results.get("t_flight_min")
            target_t = 20.0
            if "t_endurance" in state.variables.known:
                target_t = float(state.variables.known["t_endurance"]["value"])

            if t_flight and t_flight < target_t:
                items.append(
                    RecommendationItem(
                        recommendation="Increase Battery Capacity or Use Li-Ion Cells",
                        reasoning=f"Estimated endurance ({t_flight:.1f} mins) falls short of the target ({target_t:.1f} mins).",
                        expected_benefits="Directly boosts total stored energy (Wh) and endurance.",
                        potential_risks="Heavier battery pack increases disc loading, requiring higher motor thrust and power draw.",
                    )
                )
                items.append(
                    RecommendationItem(
                        recommendation="Optimize Propeller Diameter & Disc Loading",
                        reasoning="Large, slow-turning propellers are more aerodynamically efficient for hovering flight.",
                        expected_benefits="Reduces induced power requirements, improving overall efficiency.",
                        potential_risks="May require larger frame arms and can increase susceptibility to wind gusts.",
                    )
                )

            # Check thrust/weight ratios
            m_total = results.get("m_total") or results.get("m")
            t_total = results.get("T_total")
            if m_total and t_total:
                weight_n = m_total * 9.80665
                thrust_to_weight = t_total / weight_n if weight_n > 0 else 0
                if thrust_to_weight < 1.5:
                    items.append(
                        RecommendationItem(
                            recommendation="Upgrade Motors to Achieve higher Thrust-to-Weight Ratio",
                            reasoning=f"Current thrust-to-weight ratio is {thrust_to_weight:.2f}, below recommended minimum 1.5-2.0.",
                            expected_benefits="Ensures adequate control authority and wind resistance.",
                            potential_risks="Increases peak current draw, requiring beefier ESCs.",
                        )
                    )

        # ── Electronics domain-specific recommendations ──────────
        elif domain == "electronics":
            power_val = results.get("P")
            if power_val and power_val > 5.0:
                items.append(
                    RecommendationItem(
                        recommendation="Implement Active Cooling Design",
                        reasoning=f"Calculated power dissipation ({power_val:.1f} W) exceeds passive heatsink capacity limits (5.0 W).",
                        expected_benefits="Maintains safe junction temperature under peak loads.",
                        potential_risks="Adds weight, power consumption (fan), and noise.",
                    )
                )
            items.append(
                RecommendationItem(
                    recommendation="Increase PCB Copper Weight or Trace Width",
                    reasoning="Improves current-carrying capacity and minimizes trace resistance heating.",
                    expected_benefits="Reduces I2R voltage drop and improves thermal spreading.",
                    potential_risks="Increases manufacturing cost and complexity.",
                )
            )

        # ── Aerospace domain-specific recommendations ───────────
        elif domain == "aerospace":
            items.append(
                RecommendationItem(
                    recommendation="Perform High-Fidelity CFD Analysis",
                    reasoning="SymPy calculations use 2D/analytical approximations. 3D wing drag requires computational modeling.",
                    expected_benefits="Provides accurate drag coefficient (C_D) and lift distribution estimates.",
                    potential_risks="Requires high computational overhead and expert setup.",
                )
            )

        # ── General recommendations (fallback) ───────────────────
        if not items:
            items.append(
                RecommendationItem(
                    recommendation="Conduct Sensitivity Analysis on Key Parameters",
                    reasoning="Assumptions like safety factor and efficiency significantly impact sizing.",
                    expected_benefits="Identifies which parameters are most critical to refine first.",
                    potential_risks="Slightly increases design time but prevents downstream issues.",
                )
            )

        overall_reasoning = f"Based on calculation results indicating compliance status for {domain} domain parameters."
        return RecommendationData(recommendations=items, reasoning=overall_reasoning)
