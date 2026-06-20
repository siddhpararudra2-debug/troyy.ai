"""
Sensor Selection Service
Selects sensors based on type and requirements.
"""

import uuid
import time
from typing import Dict, Any
from app.electronics_intelligence.services.component_library import get_components_by_type
from app.electronics_intelligence.schemas.schemas import (
    SensorSelectionRequest,
    SensorSelectionResponse,
    Component,
    EngineeringJustification,
    Tradeoff,
    PerformanceAnalysis,
)


class SensorSelectionService:
    """Service for selecting sensors."""

    @staticmethod
    def _calculate_sensor_score(sensor: Dict[str, Any], request: SensorSelectionRequest) -> float:
        """Calculate sensor matching score."""
        score = 0.0
        specs = sensor.get("specifications", {})

        sensor_type = specs.get("sensor_type", "").lower()
        req_type = request.sensor_type.lower()

        if req_type in sensor_type or sensor_type in req_type:
            score += 40.0

        # Check interfaces
        req_interfaces = request.requirements.get("interfaces", [])
        sensor_interfaces = sensor.get("interfaces", [])
        match_count = sum(1 for iface in req_interfaces if iface in sensor_interfaces)
        if req_interfaces:
            score += 30.0 * (match_count / len(req_interfaces))

        score += 30.0 * sensor.get("availability_score", 0.5)

        return score

    @staticmethod
    def select(request: SensorSelectionRequest) -> SensorSelectionResponse:
        """Select a sensor based on requirements."""
        start_time = time.time()
        sensors = get_components_by_type("sensor")

        scored_sensors = []
        for sensor in sensors:
            score = SensorSelectionService._calculate_sensor_score(sensor, request)
            scored_sensors.append((score, sensor))

        scored_sensors.sort(key=lambda x: x[0], reverse=True)
        sorted_sensors = [sensor for _, sensor in scored_sensors]

        selected_sensor = None
        if sorted_sensors:
            selected_sensor = Component(**sorted_sensors[0])

        alternatives = []
        for sensor in sorted_sensors[1:4]:
            alternatives.append(Component(**sensor))

        justification = EngineeringJustification(
            requirements=request.requirements,
            constraints={},
            selection_criteria=[
                "Sensor type match",
                "Interface compatibility",
                "Availability",
            ],
            reasoning=f"Selected {selected_sensor.part_number if selected_sensor else 'no sensor'} for {request.sensor_type} measurement.",
        )

        tradeoffs = []

        performance_analysis = PerformanceAnalysis(
            metrics=selected_sensor.specifications if selected_sensor else {}
        )

        execution_time_ms = (time.time() - start_time) * 1000

        return SensorSelectionResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            sensor_type=request.sensor_type,
            selected_sensor=selected_sensor,
            alternatives=alternatives,
            justification=justification,
            tradeoffs=tradeoffs,
            performance_analysis=performance_analysis,
            execution_time_ms=execution_time_ms,
            created_at=time.time(),
        )
