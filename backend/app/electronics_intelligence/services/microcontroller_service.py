"""
Microcontroller Selection Service
Selects microcontrollers based on GPIO, ADC, PWM, memory, and communication requirements.
"""

import uuid
import time
from typing import Dict, Any
from app.electronics_intelligence.services.component_library import get_components_by_type
from app.electronics_intelligence.schemas.schemas import (
    MicrocontrollerSelectionRequest,
    MicrocontrollerSelectionResponse,
    Component,
    EngineeringJustification,
    Tradeoff,
)


class MicrocontrollerSelectionService:
    """Service for selecting microcontrollers."""

    @staticmethod
    def _calculate_mcu_score(mcu: Dict[str, Any], request: MicrocontrollerSelectionRequest) -> float:
        """Calculate MCU matching score."""
        specs = mcu.get("specifications", {})
        score = 0.0

        # GPIO requirements
        req_gpio = request.gpio_requirements.get("count", 0)
        mcu_gpio = specs.get("gpio_count", 0)
        if mcu_gpio >= req_gpio:
            score += 20.0

        # ADC requirements
        req_adc = request.adc_requirements.get("channels", 0)
        mcu_adc = specs.get("adc_channels", 0)
        if mcu_adc >= req_adc:
            score += 15.0

        # PWM requirements
        req_pwm = request.pwm_requirements.get("channels", 0)
        mcu_pwm = specs.get("pwm_channels", 0)
        if mcu_pwm >= req_pwm:
            score += 15.0

        # Memory requirements
        req_flash = request.memory_requirements.get("flash_kb", 0)
        req_sram = request.memory_requirements.get("sram_kb", 0)
        mcu_flash = specs.get("flash_kb", 0)
        mcu_sram = specs.get("sram_kb", 0)
        if mcu_flash >= req_flash:
            score += 15.0
        if mcu_sram >= req_sram:
            score += 15.0

        # Communication requirements
        req_comm = request.communication_requirements
        mcu_interfaces = mcu.get("interfaces", [])
        match_count = sum(1 for c in req_comm if any(c.lower() in iface.lower() for iface in mcu_interfaces))
        if req_comm:
            score += 20.0 * (match_count / len(req_comm))

        return score

    @staticmethod
    def select(request: MicrocontrollerSelectionRequest) -> MicrocontrollerSelectionResponse:
        """Select a microcontroller based on requirements."""
        start_time = time.time()
        mcus = get_components_by_type("mcu")

        scored_mcus = []
        for mcu in mcus:
            score = MicrocontrollerSelectionService._calculate_mcu_score(mcu, request)
            scored_mcus.append((score, mcu))

        scored_mcus.sort(key=lambda x: x[0], reverse=True)
        sorted_mcus = [mcu for _, mcu in scored_mcus]

        selected_mcu = None
        if sorted_mcus:
            selected_mcu = Component(**sorted_mcus[0])

        alternatives = []
        for mcu in sorted_mcus[1:4]:
            alternatives.append(Component(**mcu))

        specs = selected_mcu.specifications if selected_mcu else {}

        justification = EngineeringJustification(
            requirements=request.requirements,
            constraints={},
            selection_criteria=[
                "GPIO count",
                "ADC channels",
                "PWM channels",
                "Flash memory",
                "SRAM",
                "Communication interfaces",
            ],
            reasoning=f"Selected {selected_mcu.part_number if selected_mcu else 'no MCU'} based on peripheral and memory requirements.",
        )

        tradeoffs = []
        if selected_mcu:
            if selected_mcu.cost_usd and selected_mcu.cost_usd > 5.0:
                tradeoffs.append(Tradeoff(
                    factor="Cost",
                    description=f"MCU cost is ${selected_mcu.cost_usd:.2f}",
                    impact="negative",
                ))

        execution_time_ms = (time.time() - start_time) * 1000

        return MicrocontrollerSelectionResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            selected_mcu=selected_mcu,
            alternatives=alternatives,
            gpio_analysis={"required": request.gpio_requirements.get("count", 0), "available": specs.get("gpio_count", 0)},
            adc_analysis={"required": request.adc_requirements.get("channels", 0), "available": specs.get("adc_channels", 0)},
            pwm_analysis={"required": request.pwm_requirements.get("channels", 0), "available": specs.get("pwm_channels", 0)},
            memory_analysis={
                "flash_required_kb": request.memory_requirements.get("flash_kb", 0),
                "flash_available_kb": specs.get("flash_kb", 0),
                "sram_required_kb": request.memory_requirements.get("sram_kb", 0),
                "sram_available_kb": specs.get("sram_kb", 0),
            },
            communication_analysis={
                "required": request.communication_requirements,
                "available": selected_mcu.interfaces if selected_mcu else [],
            },
            justification=justification,
            tradeoffs=tradeoffs,
            execution_time_ms=execution_time_ms,
            created_at=time.time(),
        )
