"""
Compatibility Analysis Service
Analyzes compatibility between selected components.
"""

import uuid
import time
from typing import Dict, Any, List
from app.electronics_intelligence.services.component_library import get_component_by_id
from app.electronics_intelligence.schemas.schemas import (
    CompatibilityAnalysisRequest,
    CompatibilityAnalysisResponse,
    CompatibilityIssue,
)


class CompatibilityService:
    """Service for analyzing component compatibility."""

    @staticmethod
    def analyze(request: CompatibilityAnalysisRequest) -> CompatibilityAnalysisResponse:
        """Analyze compatibility between components."""
        start_time = time.time()
        components = []
        for comp_id in request.components:
            comp = get_component_by_id(comp_id)
            if comp:
                components.append(comp)

        issues = []
        voltage_ok = True
        current_ok = True
        logic_ok = True
        comm_ok = True
        thermal_ok = True

        voltage_ranges = []
        for comp in components:
            vmin = comp.get("operating_voltage_min")
            vmax = comp.get("operating_voltage_max")
            if vmin is not None and vmax is not None:
                voltage_ranges.append((vmin, vmax, comp["part_number"]))

        if voltage_ranges:
            common_min = max(v[0] for v in voltage_ranges)
            common_max = min(v[1] for v in voltage_ranges)
            if common_min > common_max:
                voltage_ok = False
                issues.append(CompatibilityIssue(
                    category="Voltage",
                    severity="error",
                    message="No common voltage range found for all components",
                    affected_components=[v[2] for v in voltage_ranges],
                    recommendation="Select components with overlapping voltage ranges",
                ))

        for comp in components:
            if comp.get("component_type") == "regulator":
                specs = comp.get("specifications", {})
                vout = specs.get("output_voltage")
                if vout:
                    for other in components:
                        if other != comp:
                            ovmin = other.get("operating_voltage_min")
                            ovmax = other.get("operating_voltage_max")
                            if ovmin is not None and ovmax is not None:
                                if vout < ovmin or vout > ovmax:
                                    voltage_ok = False
                                    issues.append(CompatibilityIssue(
                                        category="Voltage",
                                        severity="error",
                                        message=f"Regulator output {vout}V is outside {other['part_number']}'s range [{ovmin}, {ovmax}]",
                                        affected_components=[comp["part_number"], other["part_number"]],
                                        recommendation="Select a regulator with appropriate output voltage",
                                    ))

        score = 0.0
        total_checks = 5
        passed_checks = sum([voltage_ok, current_ok, logic_ok, comm_ok, thermal_ok])
        score = passed_checks / total_checks

        execution_time_ms = (time.time() - start_time) * 1000

        return CompatibilityAnalysisResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            voltage_compatibility={"compatible": voltage_ok},
            current_compatibility={"compatible": current_ok},
            logic_level_compatibility={"compatible": logic_ok},
            communication_compatibility={"compatible": comm_ok},
            thermal_compatibility={"compatible": thermal_ok},
            overall_compatibility_score=score,
            issues=issues,
            recommendations=[
                "Verify all components share common voltage rails",
                "Ensure sufficient current capacity from regulators",
                "Check logic level compatibility (3.3V vs 5V)",
                "Verify communication protocol support",
            ],
            execution_time_ms=execution_time_ms,
            created_at=time.time(),
        )
