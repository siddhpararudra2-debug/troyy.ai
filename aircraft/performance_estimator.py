"""
Performance Estimator - Aircraft Performance Analysis.

Capabilities:
- Takeoff and landing performance
- Climb performance
- Cruise performance
- Fuel burn analysis
- Payload-range diagrams
"""

from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
import math
import uuid
from datetime import datetime

from aircraft.aircraft_designer import AircraftConfiguration


@dataclass
class TakeoffPerformance:
    """Takeoff performance metrics."""
    ground_roll_m: float = 0.0
    total_takeoff_distance_m: float = 0.0
    liftoff_speed_ms: float = 0.0
    takeoff_time_s: float = 0.0


@dataclass
class ClimbPerformance:
    """Climb performance metrics."""
    rate_of_climb_ms: float = 0.0
    climb_gradient: float = 0.0
    time_to_altitude_s: float = 0.0
    fuel_to_climb_kg: float = 0.0
    distance_to_climb_km: float = 0.0


@dataclass
class CruisePerformance:
    """Cruise performance metrics."""
    true_airspeed_ms: float = 0.0
    mach_number: float = 0.0
    lift_to_drag_ratio: float = 0.0
    specific_range_km_kg: float = 0.0
    fuel_flow_kg_s: float = 0.0
    range_at_cruise_km: float = 0.0
    endurance_hours: float = 0.0


@dataclass
class LandingPerformance:
    """Landing performance metrics."""
    approach_speed_ms: float = 0.0
    ground_roll_m: float = 0.0
    total_landing_distance_m: float = 0.0


@dataclass
class CompletePerformanceReport:
    """Complete performance analysis report."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    design_id: str = ""
    design_name: str = ""
    takeoff: Optional[TakeoffPerformance] = None
    climb: Optional[ClimbPerformance] = None
    cruise: Optional[CruisePerformance] = None
    landing: Optional[LandingPerformance] = None
    payload_range_curve: List[Dict[str, float]] = field(default_factory=list)
    flight_envelope: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class PerformanceEstimator:
    """
    Aircraft performance estimation engine.
    Computes takeoff, climb, cruise, and landing performance.
    """

    def __init__(self):
        self._gravity = 9.80665
        self._air_density_sl = 1.225
        self._reports: Dict[str, CompletePerformanceReport] = {}

    def estimate_full_performance(
        self,
        design: AircraftConfiguration,
        altitude_m: float = 0.0,
        runway_friction: float = 0.03,
    ) -> CompletePerformanceReport:
        """Compute complete aircraft performance estimate."""
        report = CompletePerformanceReport(
            design_id=design.id,
            design_name=design.name,
        )

        # Takeoff performance
        report.takeoff = self._estimate_takeoff(design, altitude_m, runway_friction)

        # Climb performance
        report.climb = self._estimate_climb(design, altitude_m)

        # Cruise performance
        report.cruise = self._estimate_cruise(design, altitude_m)

        # Landing performance
        report.landing = self._estimate_landing(design, altitude_m, runway_friction)

        # Payload-range curve
        report.payload_range_curve = self._generate_payload_range_curve(design)

        # Flight envelope
        report.flight_envelope = self._generate_flight_envelope(design)

        self._reports[report.id] = report
        return report

    def estimate_takeoff(
        self, design: AircraftConfiguration, altitude_m: float = 0.0
    ) -> TakeoffPerformance:
        """Estimate takeoff performance."""
        return self._estimate_takeoff(design, altitude_m)

    def estimate_climb(
        self, design: AircraftConfiguration, target_altitude_m: float = 10000.0
    ) -> ClimbPerformance:
        """Estimate climb performance."""
        return self._estimate_climb(design, target_altitude_m)

    def estimate_cruise(
        self, design: AircraftConfiguration, altitude_m: float = 10000.0
    ) -> CruisePerformance:
        """Estimate cruise performance."""
        return self._estimate_cruise(design, altitude_m)

    def get_report(self, report_id: str) -> Optional[CompletePerformanceReport]:
        """Get a performance report by ID."""
        return self._reports.get(report_id)

    def list_reports(self) -> List[Dict[str, Any]]:
        """List all performance reports."""
        return [
            {
                "id": r.id,
                "design_id": r.design_id,
                "design_name": r.design_name,
                "created_at": r.created_at,
            }
            for r in self._reports.values()
        ]

    def _estimate_takeoff(
        self, design: AircraftConfiguration, altitude_m: float, mu: float = 0.03
    ) -> TakeoffPerformance:
        """Estimate takeoff distance and speed."""
        perf = TakeoffPerformance()
        air_density = self._air_density_at_altitude(altitude_m)
        weight_n = design.max_takeoff_mass_kg * self._gravity
        wing_area = design.wing_area_m2
        thrust_n = design.total_thrust_n

        if wing_area <= 0 or thrust_n <= 0:
            return perf

        # Liftoff speed (1.2 * stall speed)
        cl_max = 1.5
        stall_speed = math.sqrt(
            (2 * weight_n) / (air_density * wing_area * cl_max)
        )
        perf.liftoff_speed_ms = 1.2 * stall_speed

        # Ground roll distance
        cl_takeoff = 0.8 * cl_max
        cd_takeoff = 0.04 + cl_takeoff**2 / (math.pi * max(design.aspect_ratio, 1) * 0.8)

        ground_force = thrust_n - (cd_takeoff * 0.5 * air_density * perf.liftoff_speed_ms**2 * wing_area) - mu * weight_n
        if ground_force > 0:
            avg_accel = ground_force / design.max_takeoff_mass_kg
            perf.ground_roll_m = perf.liftoff_speed_ms**2 / (2 * avg_accel) if avg_accel > 0 else 0.0
            perf.takeoff_time_s = perf.liftoff_speed_ms / avg_accel if avg_accel > 0 else 0.0
        else:
            perf.ground_roll_m = 1000.0  # Default
            perf.takeoff_time_s = 30.0

        # Total takeoff distance (ground roll * 1.25 for clearance)
        perf.total_takeoff_distance_m = perf.ground_roll_m * 1.25

        return perf

    def _estimate_climb(self, design: AircraftConfiguration, target_altitude_m: float) -> ClimbPerformance:
        """Estimate climb performance."""
        perf = ClimbPerformance()
        weight_n = design.max_takeoff_mass_kg * self._gravity
        thrust_n = design.total_thrust_n
        wing_area = design.wing_area_m2

        if wing_area <= 0:
            return perf

        # Average climb conditions (at 70% of target altitude)
        climb_alt = target_altitude_m * 0.7
        air_density = self._air_density_at_altitude(climb_alt)

        # Rate of climb
        cl_climb = 0.6
        cd_climb = 0.03 + cl_climb**2 / (math.pi * max(design.aspect_ratio, 1) * 0.8)
        drag_n = 0.5 * air_density * cl_climb * wing_area * cd_climb / cl_climb if cl_climb > 0 else 0.0
        excess_thrust = thrust_n - drag_n

        if excess_thrust > 0:
            perf.rate_of_climb_ms = excess_thrust * design.cruise_speed_ms / weight_n if weight_n > 0 else 0.0
        else:
            perf.rate_of_climb_ms = 5.0  # Default

        perf.climb_gradient = perf.rate_of_climb_ms / max(design.cruise_speed_ms, 1) * 100

        if perf.rate_of_climb_ms > 0:
            perf.time_to_altitude_s = target_altitude_m / perf.rate_of_climb_ms
        else:
            perf.time_to_altitude_s = 600.0  # Default 10 min

        # Fuel to climb
        sfc = 0.3  # kg/N/hr
        avg_thrust_climb = thrust_n * 0.8
        perf.fuel_to_climb_kg = (sfc * avg_thrust_climb * perf.time_to_altitude_s) / 3600

        # Distance
        perf.distance_to_climb_km = (design.cruise_speed_ms * 3.6 * perf.time_to_altitude_s) / 3600

        return perf

    def _estimate_cruise(self, design: AircraftConfiguration, altitude_m: float) -> CruisePerformance:
        """Estimate cruise performance."""
        perf = CruisePerformance()
        air_density = self._air_density_at_altitude(altitude_m)
        weight_n = design.max_takeoff_mass_kg * self._gravity
        wing_area = design.wing_area_m2
        speed = design.cruise_speed_ms

        if wing_area <= 0:
            return perf

        perf.true_airspeed_ms = speed
        perf.mach_number = speed / 340.0

        # Lift coefficient at cruise
        dynamic_pressure = 0.5 * air_density * speed**2
        cl = weight_n / (dynamic_pressure * wing_area) if dynamic_pressure > 0 else 0.0
        cl = min(cl, 1.5)

        # Drag
        cd0 = 0.02
        oswald = 0.85
        cd = cd0 + cl**2 / (math.pi * max(design.aspect_ratio, 1) * oswald)

        perf.lift_to_drag_ratio = cl / cd if cd > 0 else 0.0

        # Fuel flow
        sfc = 0.3  # kg/N/hr
        drag_n = dynamic_pressure * wing_area * cd
        perf.fuel_flow_kg_s = (sfc * drag_n) / 3600

        # Specific range
        perf.specific_range_km_kg = (speed * 3.6) / (perf.fuel_flow_kg_s * 3600) if perf.fuel_flow_kg_s > 0 else 0.0

        # Range estimate (Breguet)
        if perf.fuel_flow_kg_s > 0 and design.fuel_mass_kg > 0:
            perf.range_at_cruise_km = (speed * 3.6) * design.fuel_mass_kg / (perf.fuel_flow_kg_s * 3600) if perf.fuel_flow_kg_s > 0 else 0.0
        else:
            perf.range_at_cruise_km = design.design_range_km

        # Endurance
        if perf.fuel_flow_kg_s > 0:
            perf.endurance_hours = design.fuel_mass_kg / (perf.fuel_flow_kg_s * 3600)

        return perf

    def _estimate_landing(
        self, design: AircraftConfiguration, altitude_m: float, mu: float = 0.4
    ) -> LandingPerformance:
        """Estimate landing performance."""
        perf = LandingPerformance()
        air_density = self._air_density_at_altitude(altitude_m)
        weight_n = design.max_takeoff_mass_kg * self._gravity
        wing_area = design.wing_area_m2

        if wing_area <= 0:
            return perf

        # Approach speed (1.3 * stall)
        cl_max = 1.5
        stall_speed = math.sqrt(
            (2 * weight_n) / (air_density * wing_area * cl_max)
        )
        perf.approach_speed_ms = 1.3 * stall_speed

        # Landing ground roll
        cl_land = 0.6 * cl_max
        cd_land = 0.05 + cl_land**2 / (math.pi * max(design.aspect_ratio, 1) * 0.8)
        avg_decel = self._gravity * mu + (air_density * wing_area * cd_land * perf.approach_speed_ms**2) / (2 * design.max_takeoff_mass_kg)
        perf.ground_roll_m = perf.approach_speed_ms**2 / (2 * avg_decel) if avg_decel > 0 else 500.0

        perf.total_landing_distance_m = perf.ground_roll_m * 1.43  # Include flare and air distance

        return perf

    def _generate_payload_range_curve(self, design: AircraftConfiguration) -> List[Dict[str, float]]:
        """Generate payload-range tradeoff curve points."""
        points = []
        max_payload = design.payload_mass_kg
        max_fuel = design.fuel_mass_kg

        # Max payload point
        max_payload_range = design.design_range_km
        points.append({"payload_kg": max_payload, "range_km": max_payload_range})

        # Reduced payload = more range points
        for frac in [0.75, 0.50, 0.25, 0.0]:
            payload = max_payload * frac
            extra_fuel = (max_payload - payload) * 0.8  # Convert payload weight to fuel
            total_fuel = max_fuel + extra_fuel
            extra_range = total_fuel / max_fuel * design.design_range_km if max_fuel > 0 else 0.0
            points.append({"payload_kg": payload, "range_km": extra_range * 1.1})

        # Ferry range (no payload)
        ferry_range = design.design_range_km * 1.5
        points.append({"payload_kg": 0.0, "range_km": ferry_range})

        return sorted(points, key=lambda p: p["range_km"], reverse=True)

    def _generate_flight_envelope(self, design: AircraftConfiguration) -> Dict[str, Any]:
        """Generate flight envelope (V-n diagram) data."""
        weight_n = design.max_takeoff_mass_kg * self._gravity
        wing_area = design.wing_area_m2

        if wing_area <= 0:
            return {}

        # Maneuver load factors
        n_positive = 3.8  # Typical limit load factor
        n_negative = -1.5

        # Stall speeds at various load factors
        cl_max = 1.5
        vs_1g = math.sqrt(
            (2 * weight_n) / (self._air_density_sl * wing_area * cl_max)
        ) if wing_area > 0 else 0.0
        vs_positive = vs_1g * math.sqrt(abs(n_positive)) if vs_1g > 0 else 0.0
        vs_negative = vs_1g * math.sqrt(abs(n_negative))

        # Design cruise speed
        vc = design.cruise_speed_ms

        # Design dive speed
        vd = vc * 1.4

        # Maneuver speed
        va = vs_1g * math.sqrt(n_positive) if vs_1g > 0 else 0.0

        return {
            "positive_load_factor": n_positive,
            "negative_load_factor": n_negative,
            "stall_speed_1g_ms": vs_1g,
            "stall_speed_positive_g_ms": vs_positive,
            "stall_speed_negative_g_ms": vs_negative,
            "design_cruise_speed_ms": vc,
            "design_dive_speed_ms": vd,
            "maneuver_speed_ms": va,
            "never_exceed_speed_ms": vd * 0.9,
        }

    def _air_density_at_altitude(self, altitude_m: float) -> float:
        """Calculate air density at altitude using ISA model."""
        if altitude_m < 11000:
            temp = 288.15 - 0.0065 * altitude_m
            pressure = 101325 * (temp / 288.15) ** 5.2561
        else:
            temp = 216.65
            pressure = 22632 * math.exp(-0.000157 * (altitude_m - 11000))
        return pressure / (287.058 * temp)