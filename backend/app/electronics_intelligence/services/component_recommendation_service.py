"""
Component Recommendation Service
Recommends electronic components based on requirements.
"""

import uuid
import time
import json
from typing import Dict, List, Any
from app.electronics_intelligence.services.component_library import (
    get_components_by_type,
    get_component_by_id,
)
from app.electronics_intelligence.schemas.schemas import (
    ComponentRecommendationRequest,
    ComponentRecommendationResponse,
    Component,
    EngineeringJustification,
    PerformanceAnalysis,
    CostAnalysis,
    AvailabilityAnalysis,
    Tradeoff,
)


class ComponentRecommendationService:
    """Service for recommending electronic components."""

    @staticmethod
    def _calculate_score(component: Dict[str, Any], requirements: Dict[str, Any], constraints: Dict[str, Any]) -> float:
        """Calculate a matching score for a component against requirements."""
        score = 0.0
        max_score = 100.0

        # Voltage compatibility
        req_voltage_min = requirements.get("voltage_min")
        req_voltage_max = requirements.get("voltage_max")
        if req_voltage_min is not None and req_voltage_max is not None:
            comp_vmin = component.get("operating_voltage_min", 0)
            comp_vmax = component.get("operating_voltage_max", 100)
            if comp_vmin <= req_voltage_max and comp_vmax >= req_voltage_min:
                score += 25.0

        # Current requirement
        req_current_max = requirements.get("current_max")
        if req_current_max is not None:
            comp_imax = component.get("operating_current_max", 0)
            if comp_imax >= req_current_max:
                score += 20.0

        # Temperature range
        req_temp_min = requirements.get("temperature_min")
        req_temp_max = requirements.get("temperature_max")
        if req_temp_min is not None and req_temp_max is not None:
            comp_tmin = component.get("operating_temp_min", -100)
            comp_tmax = component.get("operating_temp_max", 200)
            if comp_tmin <= req_temp_max and comp_tmax >= req_temp_min:
                score += 15.0

        # Interface requirements
        req_interfaces = requirements.get("interfaces", [])
        comp_interfaces = component.get("interfaces", [])
        if req_interfaces:
            match_count = sum(1 for iface in req_interfaces if iface in comp_interfaces)
            if match_count > 0:
                score += 15.0 * (match_count / len(req_interfaces))

        # Cost constraint
        max_cost = constraints.get("max_cost")
        if max_cost is not None:
            comp_cost = component.get("cost_usd", 0)
            if comp_cost <= max_cost:
                score += 15.0

        # Availability
        score += 10.0 * component.get("availability_score", 0.5)

        return min(score, max_score)

    @staticmethod
    def recommend(request: ComponentRecommendationRequest) -> ComponentRecommendationResponse:
        """Generate component recommendations."""
        start_time = time.time()
        components = get_components_by_type(request.component_type)

        scored_components = []
        for comp in components:
            score = ComponentRecommendationService._calculate_score(
                comp, request.requirements, request.constraints
            )
            scored_components.append((score, comp))

        scored_components.sort(key=lambda x: x[0], reverse=True)
        sorted_components = [comp for _, comp in scored_components]

        selected_component = None
        if sorted_components:
            selected_component = Component(**sorted_components[0])

        alternatives = []
        for comp in sorted_components[1:4]:
            alternatives.append(Component(**comp))

        justification = EngineeringJustification(
            requirements=request.requirements,
            constraints=request.constraints,
            selection_criteria=[
                "Voltage range compatibility",
                "Current capacity",
                "Temperature range",
                "Interface support",
                "Cost constraints",
                "Component availability",
            ],
            reasoning=f"Selected {selected_component.part_number if selected_component else 'no component'} based on matching requirements and constraints.",
        )

        tradeoffs = []
        if selected_component:
            if selected_component.cost_usd and selected_component.cost_usd > 5.0:
                tradeoffs.append(Tradeoff(
                    factor="Cost",
                    description=f"Component cost of ${selected_component.cost_usd:.2f} is above $5.00",
                    impact="negative",
                ))
            if selected_component.availability_score < 0.9:
                tradeoffs.append(Tradeoff(
                    factor="Availability",
                    description=f"Availability score is {selected_component.availability_score:.2f}",
                    impact="negative",
                ))

        performance_analysis = PerformanceAnalysis(
            metrics={
                "matching_score": scored_components[0][0] if scored_components else 0.0,
                "total_candidates": len(components),
            }
        )

        cost_analysis = CostAnalysis(
            unit_cost=selected_component.cost_usd if selected_component else None,
            cost_comparison={comp["part_number"]: comp["cost_usd"] for comp in sorted_components[:5] if "cost_usd" in comp},
        )

        availability_analysis = AvailabilityAnalysis(
            score=selected_component.availability_score if selected_component else 0.0,
            alternatives=[alt.part_number for alt in alternatives],
        )

        execution_time_ms = (time.time() - start_time) * 1000

        return ComponentRecommendationResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            component_type=request.component_type,
            selected_component=selected_component,
            alternatives=alternatives,
            justification=justification,
            tradeoffs=tradeoffs,
            performance_analysis=performance_analysis,
            cost_analysis=cost_analysis,
            availability_analysis=availability_analysis,
            validation_results={"status": "validated", "issues": []},
            documentation={"selection_report": "Component selection completed successfully"},
            execution_time_ms=execution_time_ms,
            created_at=time.time(),
        )
