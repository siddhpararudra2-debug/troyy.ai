"""
Regulator Selection Service
Selects regulators (LDO, Buck, Boost, Buck-Boost) based on requirements.
"""

import uuid
import time
from typing import Dict, Any
from app.electronics_intelligence.services.component_library import get_components_by_type
from app.electronics_intelligence.schemas.schemas import (
    RegulatorSelectionRequest,
    RegulatorSelectionResponse,
    Component,
    EngineeringJustification,
    Tradeoff,
)


class RegulatorSelectionService:
    """Service for selecting voltage regulators."""

    @staticmethod
    def _calculate_regulator_score(reg: Dict[str, Any], request: RegulatorSelectionRequest) -> float:
        """Calculate regulator matching score."""
        specs = reg.get("specifications", {})
        score = 0.0

        # Check regulator type
        req_type = request.regulator_type.lower()
        reg_type = specs.get("regulator_type", "").lower()
        if req_type in reg_type or reg_type in req_type:
            score += 30.0

        # Voltage requirements
        req_vout = request.requirements.get("output_voltage")
        req_vin_min = request.requirements.get("input_voltage_min")
        req_vin_max = request.requirements.get("input_voltage_max")

        if req_vout is not None:
            spec_vout = specs.get("output_voltage")
            if spec_vout is not None and abs(spec_vout - req_vout) < 0.1:
                score += 25.0

        reg_vmin = reg.get("operating_voltage_min", 0)
        reg_vmax = reg.get("operating_voltage_max", 100)
        if req_vin_min is not None and req_vin_max is not None:
            if reg_vmin <= req_vin_max and reg_vmax >= req_vin_min:
                score += 20.0

        # Current requirement
        req_iout = request.requirements.get("output_current_max")
        if req_iout is not None:
            reg_iout = specs.get("output_current_max", 0)
            if reg_iout >= req_iout:
                score += 15.0

        score += 10.0 * reg.get("availability_score", 0.5)

        return score

    @staticmethod
    def select(request: RegulatorSelectionRequest) -> RegulatorSelectionResponse:
        """Select a voltage regulator."""
        start_time = time.time()
        regulators = get_components_by_type("regulator")

        scored_regs = []
        for reg in regulators:
            score = RegulatorSelectionService._calculate_regulator_score(reg, request)
            scored_regs.append((score, reg))

        scored_regs.sort(key=lambda x: x[0], reverse=True)
        sorted_regs = [reg for _, reg in scored_regs]

        selected_regulator = None
        if sorted_regs:
            selected_regulator = Component(**sorted_regs[0])

        alternatives = []
        for reg in sorted_regs[1:4]:
            alternatives.append(Component(**reg))

        specs = selected_regulator.specifications if selected_regulator else {}

        justification = EngineeringJustification(
            requirements=request.requirements,
            constraints={},
            selection_criteria=[
                "Regulator type",
                "Output voltage",
                "Input voltage range",
                "Output current",
                "Availability",
            ],
            reasoning=f"Selected {selected_regulator.part_number if selected_regulator else 'no regulator'} as {request.regulator_type} converter.",
        )

        tradeoffs = []

        # Simple efficiency estimation
        efficiency = specs.get("efficiency", 80.0)
        if request.regulator_type == "ldo":
            vin = request.requirements.get("input_voltage_max", 12.0)
            vout = request.requirements.get("output_voltage", 3.3)
            iout = request.requirements.get("output_current_max", 0.1)
            power_dissipation = (vin - vout) * iout if vin > vout else 0
        else:
            power_dissipation = 0.5

        execution_time_ms = (time.time() - start_time) * 1000

        return RegulatorSelectionResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            regulator_type=request.regulator_type,
            selected_regulator=selected_regulator,
            alternatives=alternatives,
            power_dissipation_analysis={"watts": power_dissipation},
            efficiency_analysis={"percent": efficiency},
            thermal_analysis={"max_temp": selected_regulator.operating_temp_max if selected_regulator else None},
            justification=justification,
            tradeoffs=tradeoffs,
            execution_time_ms=execution_time_ms,
            created_at=time.time(),
        )
