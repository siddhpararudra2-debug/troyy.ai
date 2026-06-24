"""
Aerodynamic Engine - Core Aerodynamics Analysis.

Capabilities:
- Lift Analysis
- Drag Analysis
- Stability Analysis
- Control Surface Analysis
- Performance Prediction
"""

from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
import math
import uuid
from datetime import datetime


@dataclass
class AerodynamicResult:
    """Complete aerodynamic analysis result."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    design_name: str = ""
    altitude_m: float = 0.0
    air_density_kg_m3: float = 0.0
    speed_ms: float = 0.0
    mach_number: float = 0.0
    reynolds_number: float = 0.0
    lift_coefficient_cl: float = 0.0
    drag_coefficient_cd: float = 0.0
    induced_drag_coefficient_cdi: float = 0.0
    parasite_drag_coefficient_cd0: float = 0.0
    lift_to_drag_ratio: float = 0.0
    moment_coefficient_cm: float = 0.0
    lift_force_n: float = 0.0
    drag_force_n: float = 0.0
    center_of_pressure_m: float = 0.0
    aerodynamic_center_m: float = 0.0
    stability_margin: float = 0.0
    analysis_type: str = "full"
    warnings: List[str] = field(default_factory=list)


class AerodynamicEngine:
    """
    Core aerodynamic analysis engine.
    Computes lift, drag, stability, and performance characteristics.
    """

    def __init__(self):
        self._gravity = 9.80665
        self._results: Dict[str, AerodynamicResult] = {}

    def analyze_wing(
        self,
        wing_area_m2: float,
        aspect_ratio: float,
        speed_ms: float,
        angle_of_attack_deg: float,
        altitude_m: float = 0.0,
        wing_span_m: Optional[float] = None,
        taper_ratio: float = 0.5,
        sweep_angle_deg: float = 0.0,
    ) -> AerodynamicResult:
        """Analyze wing aerodynamics."""
        result = AerodynamicResult(
            speed_ms=speed_ms,
            altitude_m=altitude_m,
        )

        air_density = self._air_density_at_altitude(altitude_m)
        result.air_density_kg_m3 = air_density
        result.mach_number = speed_ms / 340.0
        result.reynolds_number = self._calculate_reynolds(speed_ms, wing_area_m2 ** 0.5, air_density)

        # Convert AoA to radians
        alpha = math.radians(angle_of_attack_deg)

        # Lift curve slope (subsonic)
        cl_alpha = 2 * math.pi * aspect_ratio / (2 + math.sqrt(4 + aspect_ratio**2))
        # Sweep correction
        sweep_correction = math.cos(math.radians(sweep_angle_deg))
        cl_alpha *= sweep_correction

        result.lift_coefficient_cl = cl_alpha * alpha

        # Drag components
        cd0 = 0.015 * (1 + 0.1 * math.radians(sweep_angle_deg))
        oswald = 0.85 * sweep_correction
        cdi = result.lift_coefficient_cl**2 / (math.pi * aspect_ratio * oswald) if aspect_ratio > 0 else 0.0

        result.parasite_drag_coefficient_cd0 = cd0
        result.induced_drag_coefficient_cdi = cdi
        result.drag_coefficient_cd = cd0 + cdi

        # Lift and drag forces
        dynamic_pressure = 0.5 * air_density * speed_ms**2
        result.lift_force_n = dynamic_pressure * wing_area_m2 * result.lift_coefficient_cl
        result.drag_force_n = dynamic_pressure * wing_area_m2 * result.drag_coefficient_cd

        # L/D ratio
        result.lift_to_drag_ratio = result.lift_coefficient_cl / result.drag_coefficient_cd if result.drag_coefficient_cd > 0 else 0.0

        # Moment coefficient (simplified)
        result.moment_coefficient_cm = -0.05 - 0.1 * result.lift_coefficient_cl

        # Centers
        if wing_span_m:
            mac = wing_area_m2 / wing_span_m if wing_span_m > 0 else 0.0
            result.aerodynamic_center_m = mac * 0.25
            result.center_of_pressure_m = mac * (0.25 + result.moment_coefficient_cm / result.lift_coefficient_cl) if result.lift_coefficient_cl != 0 else 0.0

        # Static margin (simplified)
        result.stability_margin = -result.moment_coefficient_cm / result.lift_coefficient_cl if result.lift_coefficient_cl != 0 else 0.0

        self._results[result.id] = result
        return result

    def analyze_full_aircraft(
        self,
        wing_area_m2: float,
        aspect_ratio: float,
        speed_ms: float,
        angle_of_attack_deg: float,
        altitude_m: float = 0.0,
        wing_span_m: Optional[float] = None,
        fuselage_length_m: float = 0.0,
        fuselage_diameter_m: float = 0.0,
        wetted_area_m2: Optional[float] = None,
        sweep_angle_deg: float = 0.0,
    ) -> AerodynamicResult:
        """Perform full aircraft aerodynamic analysis."""
        result = AerodynamicResult(
            speed_ms=speed_ms,
            altitude_m=altitude_m,
            analysis_type="full_aircraft",
        )

        air_density = self._air_density_at_altitude(altitude_m)
        result.air_density_kg_m3 = air_density
        result.mach_number = speed_ms / 340.0
        result.reynolds_number = self._calculate_reynolds(speed_ms, wing_area_m2 ** 0.5, air_density)

        alpha = math.radians(angle_of_attack_deg)
        sweep_rad = math.radians(sweep_angle_deg)

        # Lift curve slope
        cl_alpha = 2 * math.pi * aspect_ratio / (2 + math.sqrt(4 + aspect_ratio**2))
        cl_alpha *= math.cos(sweep_rad)
        result.lift_coefficient_cl = cl_alpha * alpha

        # Parasite drag (includes fuselage, tail, etc.)
        if wetted_area_m2:
            cf = 0.074 / result.reynolds_number**0.2 if result.reynolds_number > 0 else 0.003
            cd0_fuselage = cf * (1 + 1.5 * (fuselage_diameter_m / fuselage_length_m)**1.5 + 7 * (fuselage_diameter_m / fuselage_length_m)**3) * \
                           (wetted_area_m2 / wing_area_m2) if wing_area_m2 > 0 else 0.0
        else:
            cd0_fuselage = 0.010

        cd0_wing = 0.008 * (1 + 0.1 * math.degrees(sweep_rad))
        result.parasite_drag_coefficient_cd0 = cd0_wing + cd0_fuselage

        # Induced drag
        oswald = 0.85 * math.cos(sweep_rad)
        result.induced_drag_coefficient_cdi = result.lift_coefficient_cl**2 / (math.pi * aspect_ratio * oswald) if aspect_ratio > 0 else 0.0

        # Compressibility drag (transonic)
        cd_wave = 0.0
        if result.mach_number > 0.7:
            cd_wave = 0.05 * (result.mach_number - 0.7)**2

        result.drag_coefficient_cd = result.parasite_drag_coefficient_cd0 + result.induced_drag_coefficient_cdi + cd_wave

        # Forces
        dynamic_pressure = 0.5 * air_density * speed_ms**2
        result.lift_force_n = dynamic_pressure * wing_area_m2 * result.lift_coefficient_cl
        result.drag_force_n = dynamic_pressure * wing_area_m2 * result.drag_coefficient_cd
        result.lift_to_drag_ratio = result.lift_coefficient_cl / result.drag_coefficient_cd if result.drag_coefficient_cd > 0 else 0.0

        # Pitch moment
        result.moment_coefficient_cm = -0.02 - 0.08 * result.lift_coefficient_cl

        # Stability
        if wing_span_m:
            mac = wing_area_m2 / wing_span_m if wing_span_m > 0 else 0.0
            result.aerodynamic_center_m = mac * 0.25
            result.stability_margin = -result.moment_coefficient_cm / result.lift_coefficient_cl if result.lift_coefficient_cl != 0 else 0.0

        # Warnings
        if result.mach_number > 0.85:
            result.warnings.append("Transonic regime: compressibility effects significant")
        if result.lift_coefficient_cl > 1.5:
            result.warnings.append("High CL: possible flow separation")
        if result.stability_margin < 0.05:
            result.warnings.append("Low static margin: stability concern")

        self._results[result.id] = result
        return result

    def get_result(self, result_id: str) -> Optional[AerodynamicResult]:
        """Get analysis result by ID."""
        return self._results.get(result_id)

    def list_results(self) -> List[Dict[str, Any]]:
        """List all analysis results."""
        return [{"id": r.id, "speed_ms": r.speed_ms, "cl": r.lift_coefficient_cl, "cd": r.drag_coefficient_cd, "ld": r.lift_to_drag_ratio} for r in self._results.values()]

    def _calculate_reynolds(self, speed_ms: float, char_length_m: float, air_density: float) -> float:
        """Calculate Reynolds number."""
        viscosity = 1.789e-5  # kg/(m*s)
        return air_density * speed_ms * char_length_m / viscosity if viscosity > 0 else 0.0

    def _air_density_at_altitude(self, altitude_m: float) -> float:
        """ISA air density model."""
        if altitude_m < 11000:
            temp = 288.15 - 0.0065 * altitude_m
            pressure = 101325 * (temp / 288.15) ** 5.2561
        else:
            temp = 216.65
            pressure = 22632 * math.exp(-0.000157 * (altitude_m - 11000))
        return pressure / (287.058 * temp)