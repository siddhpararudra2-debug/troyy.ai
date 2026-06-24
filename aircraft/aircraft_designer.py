"""
Aircraft Designer - Core Aircraft Design Engine.

Capabilities:
- Fixed Wing Aircraft Design
- VTOL Design
- UAV Design
- Conceptual & Preliminary Design
"""

from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import math


@dataclass
class AircraftConfiguration:
    """Complete aircraft configuration definition."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    aircraft_type: str = "fixed_wing"  # fixed_wing, vtol, uav, evtol
    mission_profile: str = "general"
    overall_length_m: float = 0.0
    overall_height_m: float = 0.0
    max_takeoff_mass_kg: float = 0.0
    empty_mass_kg: float = 0.0
    fuel_mass_kg: float = 0.0
    payload_mass_kg: float = 0.0
    wing_span_m: float = 0.0
    wing_area_m2: float = 0.0
    aspect_ratio: float = 0.0
    wing_loading_kg_m2: float = 0.0
    power_plant_type: str = ""
    total_thrust_n: float = 0.0
    design_range_km: float = 0.0
    cruise_speed_ms: float = 0.0
    stall_speed_ms: float = 0.0
    service_ceiling_m: float = 0.0
    crew: int = 0
    passengers: int = 0
    configuration_data: Dict[str, Any] = field(default_factory=dict)
    subsystems: List[Dict[str, Any]] = field(default_factory=list)
    design_iteration: int = 1
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DesignConstraint:
    """Design constraint for aircraft design."""
    name: str = ""
    constraint_type: str = ""  # geometric, performance, mass, cost
    value: float = 0.0
    unit: str = ""
    tolerance: float = 0.0
    description: str = ""
    is_requirement: bool = False


class AircraftDesigner:
    """
    Core aircraft design engine supporting multiple aircraft types.
    Implements conceptual and preliminary design workflows.
    """

    def __init__(self):
        self.designs: Dict[str, AircraftConfiguration] = {}
        self._default_air_density = 1.225  # kg/m3 at sea level
        self._gravity = 9.80665  # m/s2

    def create_conceptual_design(
        self,
        name: str,
        aircraft_type: str,
        max_takeoff_mass_kg: float,
        payload_mass_kg: float,
        design_range_km: float,
        cruise_speed_ms: float,
        constraints: Optional[List[DesignConstraint]] = None,
    ) -> AircraftConfiguration:
        """Create a conceptual aircraft design from high-level requirements."""
        config = AircraftConfiguration(
            name=name,
            aircraft_type=aircraft_type,
            max_takeoff_mass_kg=max_takeoff_mass_kg,
            payload_mass_kg=payload_mass_kg,
            design_range_km=design_range_km,
            cruise_speed_ms=cruise_speed_ms,
        )

        # Estimate empty mass fraction based on aircraft type
        empty_mass_fraction = self._estimate_empty_mass_fraction(aircraft_type, max_takeoff_mass_kg)
        config.empty_mass_kg = max_takeoff_mass_kg * empty_mass_fraction
        config.fuel_mass_kg = max_takeoff_mass_kg - config.empty_mass_kg - payload_mass_kg

        # Estimate wing loading from aircraft type and mission
        wing_loading = self._estimate_wing_loading(aircraft_type, cruise_speed_ms)
        config.wing_loading_kg_m2 = wing_loading
        config.wing_area_m2 = max_takeoff_mass_kg / wing_loading if wing_loading > 0 else 0.0

        # Estimate aspect ratio based on aircraft type
        config.aspect_ratio = self._estimate_aspect_ratio(aircraft_type, design_range_km)
        if config.aspect_ratio > 0:
            config.wing_span_m = math.sqrt(config.wing_area_m2 * config.aspect_ratio)

        # Estimate thrust-to-weight ratio
        tw_ratio = self._estimate_thrust_to_weight(aircraft_type, cruise_speed_ms)
        config.total_thrust_n = max_takeoff_mass_kg * self._gravity * tw_ratio

        # Performance estimates
        config.stall_speed_ms = self._estimate_stall_speed(config)
        config.service_ceiling_m = self._estimate_service_ceiling(aircraft_type, cruise_speed_ms)

        # Set power plant type
        config.power_plant_type = self._select_power_plant(aircraft_type, design_range_km)

        if constraints:
            config.metadata["constraints"] = [c.__dict__ for c in constraints]

        config.metadata["design_phase"] = "conceptual"
        self.designs[config.id] = config
        return config

    def refine_to_preliminary_design(
        self,
        design_id: str,
        wing_span_m: Optional[float] = None,
        wing_area_m2: Optional[float] = None,
        overall_length_m: Optional[float] = None,
        subsystems: Optional[List[Dict[str, Any]]] = None,
    ) -> AircraftConfiguration:
        """Refine a conceptual design to preliminary design level."""
        if design_id not in self.designs:
            raise ValueError(f"Design {design_id} not found")

        config = self.designs[design_id]

        if wing_span_m:
            config.wing_span_m = wing_span_m
        if wing_area_m2:
            config.wing_area_m2 = wing_area_m2
        if overall_length_m:
            config.overall_length_m = overall_length_m

        if config.wing_area_m2 > 0 and config.max_takeoff_mass_kg > 0:
            config.wing_loading_kg_m2 = config.max_takeoff_mass_kg / config.wing_area_m2

        if config.wing_span_m > 0 and config.wing_area_m2 > 0:
            config.aspect_ratio = config.wing_span_m**2 / config.wing_area_m2

        if subsystems:
            config.subsystems = subsystems

        config.design_iteration += 1
        config.updated_at = datetime.utcnow().isoformat()
        config.metadata["design_phase"] = "preliminary"
        return config

    def design_uav(
        self,
        name: str,
        max_takeoff_mass_kg: float,
        payload_mass_kg: float,
        wing_span_m: float,
        endurance_hours: float,
        cruise_speed_ms: float,
    ) -> AircraftConfiguration:
        """Design a UAV with specialized parameters."""
        config = AircraftConfiguration(
            name=name,
            aircraft_type="uav",
            max_takeoff_mass_kg=max_takeoff_mass_kg,
            payload_mass_kg=payload_mass_kg,
            cruise_speed_ms=cruise_speed_ms,
            wing_span_m=wing_span_m,
        )

        # UAV-specific empty mass fraction (typically 40-60%)
        config.empty_mass_kg = max_takeoff_mass_kg * 0.45
        config.fuel_mass_kg = max_takeoff_mass_kg - config.empty_mass_kg - payload_mass_kg

        # Wing area estimation for UAVs (higher aspect ratio typical)
        config.aspect_ratio = self._estimate_aspect_ratio("uav", endurance_hours * cruise_speed_ms * 3.6 / 1000)
        config.wing_area_m2 = wing_span_m**2 / config.aspect_ratio if config.aspect_ratio > 0 else 0.0

        if config.wing_area_m2 > 0:
            config.wing_loading_kg_m2 = max_takeoff_mass_kg / config.wing_area_m2

        # UAV electric or small engine thrust
        config.power_plant_type = "electric" if max_takeoff_mass_kg < 25 else "piston"
        config.total_thrust_n = max_takeoff_mass_kg * self._gravity * 0.3

        config.stall_speed_ms = self._estimate_stall_speed(config)
        config.design_range_km = endurance_hours * cruise_speed_ms * 3.6 / 1000
        config.service_ceiling_m = 4000  # Typical UAV ceiling

        config.metadata["design_phase"] = "uav_conceptual"
        config.metadata["endurance_hours"] = endurance_hours
        self.designs[config.id] = config
        return config

    def design_vtol(
        self,
        name: str,
        max_takeoff_mass_kg: float,
        payload_mass_kg: float,
        hover_thrust_n: float,
        cruise_speed_ms: float,
        vtol_type: str = "tilt_rotor",
    ) -> AircraftConfiguration:
        """Design a VTOL aircraft."""
        config = AircraftConfiguration(
            name=name,
            aircraft_type="vtol",
            max_takeoff_mass_kg=max_takeoff_mass_kg,
            payload_mass_kg=payload_mass_kg,
            cruise_speed_ms=cruise_speed_ms,
        )

        # VTOL-specific sizing
        config.empty_mass_kg = max_takeoff_mass_kg * 0.50
        config.fuel_mass_kg = max_takeoff_mass_kg - config.empty_mass_kg - payload_mass_kg
        config.total_thrust_n = hover_thrust_n

        # VTOL wing loading (lower for hover capability)
        config.wing_loading_kg_m2 = 100.0  # Typical VTOL wing loading
        config.wing_area_m2 = max_takeoff_mass_kg / config.wing_loading_kg_m2
        config.aspect_ratio = 6.0
        config.wing_span_m = math.sqrt(config.wing_area_m2 * config.aspect_ratio)

        config.power_plant_type = "electric_rotor"
        config.stall_speed_ms = self._estimate_stall_speed(config)
        config.service_ceiling_m = 3000

        config.metadata["design_phase"] = "vtol_conceptual"
        config.metadata["vtol_type"] = vtol_type
        self.designs[config.id] = config
        return config

    def get_design(self, design_id: str) -> Optional[AircraftConfiguration]:
        """Get a design by ID."""
        return self.designs.get(design_id)

    def list_designs(self) -> List[Dict[str, Any]]:
        """List all designs with summary info."""
        return [
            {
                "id": d.id,
                "name": d.name,
                "type": d.aircraft_type,
                "mass_kg": d.max_takeoff_mass_kg,
                "phase": d.metadata.get("design_phase", "unknown"),
                "created_at": d.created_at,
            }
            for d in self.designs.values()
        ]

    def generate_mass_report(self, design_id: str) -> Dict[str, Any]:
        """Generate a detailed mass breakdown report."""
        config = self.get_design(design_id)
        if not config:
            raise ValueError(f"Design {design_id} not found")

        mass_breakdown = {
            "empty_mass_kg": config.empty_mass_kg,
            "fuel_mass_kg": config.fuel_mass_kg,
            "payload_mass_kg": config.payload_mass_kg,
            "max_takeoff_mass_kg": config.max_takeoff_mass_kg,
            "empty_mass_fraction": config.empty_mass_kg / config.max_takeoff_mass_kg if config.max_takeoff_mass_kg > 0 else 0.0,
            "fuel_fraction": config.fuel_mass_kg / config.max_takeoff_mass_kg if config.max_takeoff_mass_kg > 0 else 0.0,
            "payload_fraction": config.payload_mass_kg / config.max_takeoff_mass_kg if config.max_takeoff_mass_kg > 0 else 0.0,
        }
        return mass_breakdown

    def generate_performance_report(self, design_id: str, altitude_m: float = 0.0) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        config = self.get_design(design_id)
        if not config:
            raise ValueError(f"Design {design_id} not found")

        air_density = self._air_density_at_altitude(altitude_m)
        wing_area = config.wing_area_m2
        mass = config.max_takeoff_mass_kg
        weight_n = mass * self._gravity

        # Lift coefficient at cruise
        dynamic_pressure = 0.5 * air_density * config.cruise_speed_ms**2
        cruise_cl = weight_n / (dynamic_pressure * wing_area) if dynamic_pressure * wing_area > 0 else 0.0

        # Drag estimation (simplified)
        cd0 = 0.02  # Zero-lift drag coefficient
        oswald = 0.85  # Oswald efficiency factor
        induced_drag = cruise_cl**2 / (math.pi * config.aspect_ratio * oswald) if config.aspect_ratio > 0 else 0.0
        total_cd = cd0 + induced_drag

        # Drag force
        drag_n = dynamic_pressure * wing_area * total_cd

        # Power required
        power_required_w = drag_n * config.cruise_speed_ms

        # Range estimation (Breguet range equation)
        sfc = 0.3  # Specific fuel consumption (kg/N/hr)
        range_est = (config.cruise_speed_ms * 3.6 / sfc) * (config.aspect_ratio / total_cd) * \
            math.log(config.max_takeoff_mass_kg / (config.max_takeoff_mass_kg - config.fuel_mass_kg)) if \
            config.fuel_mass_kg > 0 and total_cd > 0 else 0.0

        return {
            "design_id": design_id,
            "altitude_m": altitude_m,
            "air_density_kg_m3": air_density,
            "weight_n": weight_n,
            "lift_coefficient_cl": cruise_cl,
            "drag_coefficient_cd": total_cd,
            "induced_drag_coefficient": induced_drag,
            "drag_force_n": drag_n,
            "power_required_w": power_required_w,
            "power_required_kw": power_required_w / 1000,
            "estimated_range_km": range_est,
            "stall_speed_ms": config.stall_speed_ms,
            "mach_number": config.cruise_speed_ms / 340.0,
            "wing_loading_n_m2": config.wing_loading_kg_m2 * self._gravity,
        }

    def _estimate_empty_mass_fraction(self, aircraft_type: str, mass_kg: float) -> float:
        """Estimate empty mass fraction based on aircraft type and mass."""
        fractions = {
            "fixed_wing": 0.45 + (mass_kg / 100000) * 0.05,
            "vtol": 0.50 + (mass_kg / 100000) * 0.03,
            "uav": 0.40 + (mass_kg / 5000) * 0.02,
            "evtol": 0.55,
        }
        return min(fractions.get(aircraft_type, 0.50), 0.85)

    def _estimate_wing_loading(self, aircraft_type: str, cruise_speed_ms: float) -> float:
        """Estimate wing loading based on aircraft type."""
        loadings = {
            "fixed_wing": 400 + cruise_speed_ms * 2,
            "vtol": 100 + cruise_speed_ms * 0.5,
            "uav": 50 + cruise_speed_ms * 1.5,
            "evtol": 80 + cruise_speed_ms * 0.3,
        }
        return max(loadings.get(aircraft_type, 300), 20.0)

    def _estimate_aspect_ratio(self, aircraft_type: str, range_km: float) -> float:
        """Estimate aspect ratio based on aircraft type and range."""
        ratios = {
            "fixed_wing": 8 + range_km / 1000,
            "vtol": 6 + range_km / 500,
            "uav": 12 + range_km / 200,
            "evtol": 7,
        }
        return min(max(ratios.get(aircraft_type, 8), 3.0), 25.0)

    def _estimate_thrust_to_weight(self, aircraft_type: str, cruise_speed_ms: float) -> float:
        """Estimate thrust-to-weight ratio."""
        ratios = {
            "fixed_wing": 0.25 + cruise_speed_ms / 500,
            "vtol": 1.15,
            "uav": 0.20 + cruise_speed_ms / 300,
            "evtol": 1.10,
        }
        return ratios.get(aircraft_type, 0.30)

    def _estimate_stall_speed(self, config: AircraftConfiguration) -> float:
        """Estimate stall speed using wing loading and CL_max."""
        cl_max = 1.5  # Typical maximum lift coefficient
        if config.wing_loading_kg_m2 > 0:
            stall = math.sqrt(
                (2 * config.wing_loading_kg_m2 * self._gravity) /
                (self._default_air_density * cl_max)
            )
            return stall
        return 0.0

    def _estimate_service_ceiling(self, aircraft_type: str, cruise_speed_ms: float) -> float:
        """Estimate service ceiling."""
        ceilings = {
            "fixed_wing": 10000 + cruise_speed_ms * 10,
            "vtol": 3000 + cruise_speed_ms * 5,
            "uav": 4000 + cruise_speed_ms * 8,
            "evtol": 3000,
        }
        return ceilings.get(aircraft_type, 5000)

    def _select_power_plant(self, aircraft_type: str, range_km: float) -> str:
        """Select appropriate power plant type."""
        if aircraft_type == "uav":
            return "electric" if range_km < 100 else "piston"
        elif aircraft_type == "vtol" or aircraft_type == "evtol":
            return "electric_rotor"
        elif range_km < 500:
            return "turboprop"
        elif range_km < 3000:
            return "turbofan"
        else:
            return "high_bypass_turbofan"

    def _air_density_at_altitude(self, altitude_m: float) -> float:
        """Calculate air density at altitude using ISA model."""
        if altitude_m < 11000:
            temp = 288.15 - 0.0065 * altitude_m
            pressure = 101325 * (temp / 288.15) ** 5.2561
        else:
            temp = 216.65
            pressure = 22632 * math.exp(-0.000157 * (altitude_m - 11000))
        return pressure / (287.058 * temp)