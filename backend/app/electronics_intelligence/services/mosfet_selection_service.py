"""
MOSFET Selection Service
Selects MOSFETs based on voltage, current, and switching requirements.
"""

import uuid
import time
from typing import Dict, Any
from app.electronics_intelligence.services.component_library import get_components_by_type
from app.electronics_intelligence.schemas.schemas import (
    MosfetSelectionRequest,
    MosfetSelectionResponse,
    Component,
    EngineeringJustification,
    Tradeoff,
)


class MosfetSelectionService:
    """Service for selecting MOSFETs."""

    @staticmethod
    def _calculate_mosfet_score(mosfet: Dict[str, Any], request: MosfetSelectionRequest) -> float:
        """Calculate MOSFET matching score."""
        specs = mosfet.get("specifications", {})
        score = 0.0

        # Voltage rating
        req_vds = request.requirements.get("vds", 20)
        mosfet_vds = specs.get("vds", 0)
        if mosfet_vds >= req_vds * 1.2:  # 20% safety margin
            score += 35.0

        # Current rating
        req_id = request.requirements.get("id", 5)
        mosfet_id = specs.get("id", 0)
        if mosfet_id >= req_id * 1.2:
            score += 30.0

        score += 25.0 * mosfet.get("availability_score", 0.5)
        score += 10.0

        return score

    @staticmethod
    def select(request: MosfetSelectionRequest) -> MosfetSelectionResponse:
        """Select a MOSFET."""
        start_time = time.time()
        mosfets = get_components_by_type("mosfet")

        scored_mosfets = []
        for mosfet in mosfets:
            score = MosfetSelectionService._calculate_mosfet_score(mosfet, request)
            scored_mosfets.append((score, mosfet))

        scored_mosfets.sort(key=lambda x: x[0], reverse=True)
        sorted_mosfets = [mosfet for _, mosfet in scored_mosfets]

        selected_mosfet = None
        if sorted_mosfets:
            selected_mosfet = Component(**sorted_mosfets[0])

        alternatives = []
        for mosfet in sorted_mosfets[1:4]:
            alternatives.append(Component(**mosfet))

        specs = selected_mosfet.specifications if selected_mosfet else {}

        justification = EngineeringJustification(
            requirements=request.requirements,
            constraints={},
            selection_criteria=[
                "Vds rating (with safety margin)",
                "Id rating (with safety margin)",
                "Availability",
            ],
            reasoning=f"Selected {selected_mosfet.part_number if selected_mosfet else 'no MOSFET'} based on voltage and current requirements.",
        )

        tradeoffs = []

        execution_time_ms = (time.time() - start_time) * 1000

        return MosfetSelectionResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            selected_mosfet=selected_mosfet,
            alternatives=alternatives,
            voltage_analysis={"vds": specs.get("vds"), "required": request.requirements.get("vds")},
            current_analysis={"id": specs.get("id"), "required": request.requirements.get("id")},
            switching_analysis={},
            thermal_analysis={"max_temp": selected_mosfet.operating_temp_max if selected_mosfet else None},
            justification=justification,
            tradeoffs=tradeoffs,
            execution_time_ms=execution_time_ms,
            created_at=time.time(),
        )
