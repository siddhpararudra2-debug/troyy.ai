"""
Sizing Engine - Aircraft Sizing and Optimization.

Capabilities:
- Initial sizing from requirements
- Weight and balance analysis
- Sensitivity analysis
- Design space exploration
"""

from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
import math
import uuid
from datetime import datetime

from aircraft.aircraft_designer import AircraftConfiguration, AircraftDesigner


@dataclass
class SizingResult:
    """Result of aircraft sizing analysis."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    design_name: str = ""
    max_takeoff_mass_kg: float = 0.0
    wing_area_m2: float = 0.0
    thrust_n: float = 0.0
    fuel_volume_m3: float = 0.0
    wing_loading_kg_m2: float = 0.0
    thrust_to_weight: float = 0.0
    aspect_ratio: float = 0.0
    wing_span_m: float = 0.0
    empty_mass_fraction: float = 0.0
    fuel_fraction: float = 0.0
    payload_fraction: float = 0.0
    design_iteration: int = 1
    constraints_satisfied: bool = False
    constraint_violations: List[str] = field(default_factory=list)
    sizing_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class SizingConstraint:
    """Constraint for sizing optimization."""
    parameter: str = ""
    min_value: float = 0.0
    max_value: float = float('inf')
    weight: float = 1.0


class SizingEngine:
    """
    Aircraft sizing engine for initial sizing and optimization.
    Uses statistical methods and physics-based equations.
    """

    def __init__(self):
        self.results: Dict[str, SizingResult] = {}
        self._gravity = 9.80665

    def initial_sizing(
        self,
        payload_mass_kg: float,
        design_range_km: float,
        cruise_speed_ms: float,
        aircraft_type: str = "fixed_wing",
        num_passengers: int = 0,
        crew: int = 0,
        constraints: Optional[List[SizingConstraint]] = None,
    ) -> SizingResult:
        """Perform initial sizing from high-level requirements."""
        result = SizingResult()

        # Estimate MTOW from payload and range (statistical regression)
        mtow_kg = self._estimate_mtow(payload_mass_kg, design_range_km, aircraft_type, num_passengers)
        result.max_takeoff_mass_kg = mtow_kg

        # Empty mass fraction
        empty_frac = self._estimate_empty_fraction(aircraft_type, mtow_kg)
        result.empty_mass_fraction = empty_frac

        # Fuel fraction
        fuel_frac = self._estimate_fuel_fraction(design_range_km, aircraft_type)
        result.fuel_fraction = fuel_frac

        # Payload fraction
        result.payload_fraction = payload_mass_kg / mtow_kg if mtow_kg > 0 else 0.0

        # Wing area from wing loading
        wing_loading = self._optimum_wing_loading(aircraft_type, cruise_speed_ms, mtow_kg)
        result.wing_loading_kg_m2 = wing_loading
        result.wing_area_m2 = mtow_kg / wing_loading if wing_loading > 0 else 0.0

        # Aspect ratio and span
        result.aspect_ratio = self._optimum_aspect_ratio(aircraft_type, design_range_km)
        result.wing_span_m = math.sqrt(result.wing_area_m2 * result.aspect_ratio) if result.aspect_ratio > 0 else 0.0

        # Thrust requirements
        tw_ratio = self._required_thrust_to_weight(aircraft_type, cruise_speed_ms, mtow_kg)
        result.thrust_to_weight = tw_ratio
        result.thrust_n = mtow_kg * self._gravity * tw_ratio

        # Fuel volume
        fuel_mass = mtow_kg * fuel_frac
        fuel_density_kg_m3 = 800  # Jet fuel density
        result.fuel_volume_m3 = fuel_mass / fuel_density_kg_m3 if fuel_density_kg_m3 > 0 else 0.0

        # Check constraints
        if constraints:
            violations = self._check_constraints(result, constraints)
            result.constraint_violations = violations
            result.constraints_satisfied = len(violations) == 0

        # Additional metrics
        result.sizing_metrics = {
            "payload_range_efficiency": payload_mass_kg * design_range_km / mtow_kg if mtow_kg > 0 else 0.0,
            "aerodynamic_efficiency": result.aspect_ratio / 10.0,
            "structural_efficiency": 1.0 - empty_frac,
            "mission_efficiency": payload_mass_kg * design_range_km / (mtow_kg * fuel_frac) if fuel_frac > 0 else 0.0,
        }

        self.results[result.id] = result
        return result

    def sizing_from_design(self, design: AircraftConfiguration) -> SizingResult:
        """Perform sizing analysis from an existing design."""
        result = SizingResult(
            design_name=design.name,
            max_takeoff_mass_kg=design.max_takeoff_mass_kg,
            wing_area_m2=design.wing_area_m2,
            thrust_n=design.total_thrust_n,
            wing_loading_kg_m2=design.wing_loading_kg_m2,
            thrust_to_weight=design.total_thrust_n / (design.max_takeoff_mass_kg * self._gravity) if design.max_takeoff_mass_kg > 0 else 0.0,
            aspect_ratio=design.aspect_ratio,
            wing_span_m=design.wing_span_m,
            empty_mass_fraction=design.empty_mass_kg / design.max_takeoff_mass_kg if design.max_takeoff_mass_kg > 0 else 0.0,
            fuel_fraction=design.fuel_mass_kg / design.max_takeoff_mass_kg if design.max_takeoff_mass_kg > 0 else 0.0,
            payload_fraction=design.payload_mass_kg / design.max_takeoff_mass_kg if design.max_takeoff_mass_kg > 0 else 0.0,
        )

        # Fuel volume
        fuel_density_kg_m3 = 800
        result.fuel_volume_m3 = design.fuel_mass_kg / fuel_density_kg_m3 if fuel_density_kg_m3 > 0 else 0.0

        result.sizing_metrics = {
            "payload_range_efficiency": design.payload_mass_kg * design.design_range_km / design.max_takeoff_mass_kg if design.max_takeoff_mass_kg > 0 else 0.0,
            "aerodynamic_efficiency": design.aspect_ratio / 10.0,
            "structural_efficiency": 1.0 - (design.empty_mass_kg / design.max_takeoff_mass_kg) if design.max_takeoff_mass_kg > 0 else 0.0,
        }

        self.results[result.id] = result
        return result

    def design_space_sweep(
        self,
        payload_range: Tuple[float, float],
        range_range: Tuple[float, float],
        aircraft_type: str = "fixed_wing",
        steps: int = 5,
    ) -> List[SizingResult]:
        """Perform a design space exploration sweep."""
        results = []
        payload_values = [payload_range[0] + (payload_range[1] - payload_range[0]) * i / (steps - 1) for i in range(steps)]
        range_values = [range_range[0] + (range_range[1] - range_range[0]) * i / (steps - 1) for i in range(steps)]

        for payload in payload_values:
            for rng in range_values:
                result = self.initial_sizing(
                    payload_mass_kg=payload,
                    design_range_km=rng,
                    cruise_speed_ms=200.0,
                    aircraft_type=aircraft_type,
                )
                results.append(result)

        return results

    def get_sizing(self, sizing_id: str) -> Optional[SizingResult]:
        """Get a sizing result by ID."""
        return self.results.get(sizing_id)

    def _estimate_mtow(self, payload_kg: float, range_km: float, ac_type: str, passengers: int = 0) -> float:
        """Estimate maximum takeoff weight."""
        if ac_type == "uav":
            return payload_kg * (1.5 + range_km / 500)
        elif ac_type == "vtol":
            return payload_kg * (2.0 + range_km / 200)
        elif ac_type == "evtol":
            return payload_kg * (2.5 + range_km / 150)
        else:
            # Fixed wing: statistical regression
            if passengers > 0:
                return payload_kg * (2.0 + range_km / 1000) + passengers * 100
            return payload_kg * (3.0 + range_km / 1500)

    def _estimate_empty_fraction(self, ac_type: str, mtow_kg: float) -> float:
        """Estimate empty mass fraction."""
        fractions = {
            "fixed_wing": 0.45 + math.log10(max(mtow_kg, 1000)) * 0.02,
            "uav": 0.40 + math.log10(max(mtow_kg, 10)) * 0.02,
            "vtol": 0.50 + math.log10(max(mtow_kg, 1000)) * 0.02,
            "evtol": 0.55,
        }
        return min(fractions.get(ac_type, 0.50), 0.80)

    def _estimate_fuel_fraction(self, range_km: float, ac_type: str) -> float:
        """Estimate fuel fraction based on range."""
        if ac_type in ("uav", "evtol"):
            base = 0.05 + range_km / 5000
        else:
            base = 0.10 + range_km / 3000
        return min(max(base, 0.02), 0.60)

    def _optimum_wing_loading(self, ac_type: str, speed_ms: float, mtow_kg: float) -> float:
        """Calculate optimum wing loading."""
        if ac_type == "uav":
            return 30 + speed_ms * 0.5
        elif ac_type in ("vtol", "evtol"):
            return 80 + speed_ms * 0.3
        else:
            return 200 + speed_ms * 2.0 + mtow_kg / 10000 * 50

    def _optimum_aspect_ratio(self, ac_type: str, range_km: float) -> float:
        """Calculate optimum aspect ratio."""
        ratios = {
            "uav": 15 + range_km / 1000,
            "fixed_wing": 8 + range_km / 2000,
            "vtol": 6,
            "evtol": 7,
        }
        return min(max(ratios.get(ac_type, 8), 3), 30)

    def _required_thrust_to_weight(self, ac_type: str, speed_ms: float, mtow_kg: float) -> float:
        """Calculate required thrust-to-weight ratio."""
        if ac_type in ("vtol", "evtol"):
            return 1.15
        elif ac_type == "uav":
            return 0.20 + speed_ms / 500
        else:
            return 0.25 + speed_ms / 400 + mtow_kg / 500000

    def _check_constraints(self, result: SizingResult, constraints: List[SizingConstraint]) -> List[str]:
        """Check sizing against constraints."""
        violations = []
        param_map = {
            "max_takeoff_mass_kg": result.max_takeoff_mass_kg,
            "wing_area_m2": result.wing_area_m2,
            "thrust_n": result.thrust_n,
            "wing_loading_kg_m2": result.wing_loading_kg_m2,
            "thrust_to_weight": result.thrust_to_weight,
            "aspect_ratio": result.aspect_ratio,
            "wing_span_m": result.wing_span_m,
        }

        for constraint in constraints:
            value = param_map.get(constraint.parameter)
            if value is not None:
                if value < constraint.min_value:
                    violations.append(f"{constraint.parameter} ({value:.2f}) < min ({constraint.min_value:.2f})")
                if value > constraint.max_value:
                    violations.append(f"{constraint.parameter} ({value:.2f}) > max ({constraint.max_value:.2f})")

        return violations