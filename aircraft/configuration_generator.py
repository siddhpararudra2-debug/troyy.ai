"""
Configuration Generator - Generates complete aircraft configurations.

Capabilities:
- Generate CAD-ready configuration parameters
- Generate configuration variants
- Optimize configuration for mission profiles
"""

from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import math

from aircraft.aircraft_designer import AircraftConfiguration, AircraftDesigner


@dataclass
class WingGeometry:
    """Detailed wing geometry parameters."""
    span_m: float = 0.0
    root_chord_m: float = 0.0
    tip_chord_m: float = 0.0
    mean_aerodynamic_chord_m: float = 0.0
    sweep_angle_deg: float = 0.0
    dihedral_angle_deg: float = 0.0
    incidence_angle_deg: float = 0.0
    taper_ratio: float = 0.0
    area_m2: float = 0.0
    aspect_ratio: float = 0.0
    wing_type: str = "rectangular"  # rectangular, tapered, swept, delta, elliptical
    airfoil_section: str = "NACA_2412"
    twist_angle_deg: float = 0.0


@dataclass
class FuselageGeometry:
    """Detailed fuselage geometry."""
    length_m: float = 0.0
    max_width_m: float = 0.0
    max_height_m: float = 0.0
    fineness_ratio: float = 0.0
    cross_section_area_m2: float = 0.0
    cabin_length_m: float = 0.0
    nose_length_m: float = 0.0
    tail_length_m: float = 0.0
    cargo_volume_m3: float = 0.0


@dataclass
class EmpennageGeometry:
    """Tail geometry."""
    horizontal_tail_area_m2: float = 0.0
    horizontal_tail_span_m: float = 0.0
    horizontal_tail_aspect_ratio: float = 0.0
    vertical_tail_area_m2: float = 0.0
    vertical_tail_height_m: float = 0.0
    vertical_tail_aspect_ratio: float = 0.0
    tail_arm_m: float = 0.0


@dataclass
class LandingGearGeometry:
    """Landing gear configuration."""
    gear_type: str = "tricycle"  # tricycle, tail_dragger, tandem
    nose_gear_length_m: float = 0.0
    main_gear_length_m: float = 0.0
    wheel_base_m: float = 0.0
    wheel_track_m: float = 0.0
    tire_size: str = ""


@dataclass
class CompleteConfiguration:
    """Complete aircraft configuration for CAD / manufacturing."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    aircraft_config: Optional[AircraftConfiguration] = None
    wing: Optional[WingGeometry] = None
    fuselage: Optional[FuselageGeometry] = None
    empennage: Optional[EmpennageGeometry] = None
    landing_gear: Optional[LandingGearGeometry] = None
    engine_nacelles: List[Dict[str, Any]] = field(default_factory=list)
    control_surfaces: List[Dict[str, Any]] = field(default_factory=list)
    structural_layout: Dict[str, Any] = field(default_factory=dict)
    configuration_variant: str = "baseline"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class ConfigurationGenerator:
    """
    Generates complete aircraft configurations from design parameters.
    Produces CAD-ready geometry definitions.
    """

    def __init__(self):
        self.configurations: Dict[str, CompleteConfiguration] = {}

    def generate_from_design(
        self,
        design: AircraftConfiguration,
        wing_type: str = "tapered",
        gear_type: str = "tricycle",
    ) -> CompleteConfiguration:
        """Generate a complete configuration from an aircraft design."""
        wing = self._generate_wing_geometry(design, wing_type)
        fuselage = self._generate_fuselage_geometry(design)
        empennage = self._generate_empennage_geometry(design, wing)
        landing_gear = self._get_landing_gear(design, gear_type)

        config = CompleteConfiguration(
            name=f"{design.name}_config",
            aircraft_config=design,
            wing=wing,
            fuselage=fuselage,
            empennage=empennage,
            landing_gear=landing_gear,
            structural_layout=self._generate_structural_layout(design, wing),
            control_surfaces=self._generate_control_surfaces(design, wing),
        )

        self.configurations[config.id] = config
        return config

    def generate_variants(self, base_config_id: str, variants: List[str]) -> List[CompleteConfiguration]:
        """Generate multiple configuration variants from a base."""
        if base_config_id not in self.configurations:
            raise ValueError(f"Base configuration {base_config_id} not found")

        base = self.configurations[base_config_id]
        generated = []

        for variant in variants:
            new_config = self._apply_variant_transform(base, variant)
            self.configurations[new_config.id] = new_config
            generated.append(new_config)

        return generated

    def get_configuration(self, config_id: str) -> Optional[CompleteConfiguration]:
        """Get a configuration by ID."""
        return self.configurations.get(config_id)

    def export_configuration(self, config_id: str) -> Dict[str, Any]:
        """Export configuration as a structured dictionary for CAD integration."""
        config = self.get_configuration(config_id)
        if not config:
            raise ValueError(f"Configuration {config_id} not found")

        return {
            "id": config.id,
            "name": config.name,
            "variant": config.configuration_variant,
            "wing": {
                "span_m": config.wing.span_m if config.wing else 0.0,
                "root_chord_m": config.wing.root_chord_m if config.wing else 0.0,
                "tip_chord_m": config.wing.tip_chord_m if config.wing else 0.0,
                "mac_m": config.wing.mean_aerodynamic_chord_m if config.wing else 0.0,
                "sweep_deg": config.wing.sweep_angle_deg if config.wing else 0.0,
                "dihedral_deg": config.wing.dihedral_angle_deg if config.wing else 0.0,
                "area_m2": config.wing.area_m2 if config.wing else 0.0,
                "aspect_ratio": config.wing.aspect_ratio if config.wing else 0.0,
                "taper_ratio": config.wing.taper_ratio if config.wing else 0.0,
                "airfoil": config.wing.airfoil_section if config.wing else "NACA_2412",
                "type": config.wing.wing_type if config.wing else "rectangular",
            },
            "fuselage": {
                "length_m": config.fuselage.length_m if config.fuselage else 0.0,
                "max_width_m": config.fuselage.max_width_m if config.fuselage else 0.0,
                "max_height_m": config.fuselage.max_height_m if config.fuselage else 0.0,
                "fineness_ratio": config.fuselage.fineness_ratio if config.fuselage else 0.0,
            },
            "empennage": {
                "ht_area_m2": config.empennage.horizontal_tail_area_m2 if config.empennage else 0.0,
                "vt_area_m2": config.empennage.vertical_tail_area_m2 if config.empennage else 0.0,
            },
            "landing_gear": {
                "type": config.landing_gear.gear_type if config.landing_gear else "tricycle",
                "wheel_base_m": config.landing_gear.wheel_base_m if config.landing_gear else 0.0,
                "wheel_track_m": config.landing_gear.wheel_track_m if config.landing_gear else 0.0,
            },
            "control_surfaces": config.control_surfaces,
            "structural_layout": config.structural_layout,
            "created_at": config.created_at,
        }

    def _generate_wing_geometry(self, design: AircraftConfiguration, wing_type: str) -> WingGeometry:
        """Generate wing geometry from design parameters."""
        wing = WingGeometry()
        wing.span_m = design.wing_span_m
        wing.area_m2 = design.wing_area_m2
        wing.aspect_ratio = design.aspect_ratio
        wing.wing_type = wing_type

        if wing_type == "rectangular":
            wing.root_chord_m = design.wing_area_m2 / design.wing_span_m if design.wing_span_m > 0 else 0.0
            wing.tip_chord_m = wing.root_chord_m
            wing.taper_ratio = 1.0
            wing.sweep_angle_deg = 0.0
        elif wing_type == "tapered":
            wing.taper_ratio = 0.4
            wing.root_chord_m = 2 * design.wing_area_m2 / (design.wing_span_m * (1 + wing.taper_ratio)) if design.wing_span_m > 0 else 0.0
            wing.tip_chord_m = wing.root_chord_m * wing.taper_ratio
            wing.sweep_angle_deg = 5.0 if design.cruise_speed_ms < 200 else 15.0
        elif wing_type == "swept":
            wing.taper_ratio = 0.3
            wing.root_chord_m = 2 * design.wing_area_m2 / (design.wing_span_m * (1 + wing.taper_ratio)) if design.wing_span_m > 0 else 0.0
            wing.tip_chord_m = wing.root_chord_m * wing.taper_ratio
            wing.sweep_angle_deg = 25.0 if design.cruise_speed_ms < 250 else 35.0
        elif wing_type == "delta":
            wing.taper_ratio = 0.1
            wing.root_chord_m = 2 * design.wing_area_m2 / (design.wing_span_m * (1 + wing.taper_ratio)) if design.wing_span_m > 0 else 0.0
            wing.tip_chord_m = wing.root_chord_m * wing.taper_ratio
            wing.sweep_angle_deg = 60.0

        # Mean aerodynamic chord (MAC)
        if wing.taper_ratio > 0:
            wing.mean_aerodynamic_chord_m = (2.0 / 3.0) * wing.root_chord_m * \
                ((1 + wing.taper_ratio + wing.taper_ratio**2) / (1 + wing.taper_ratio))
        else:
            wing.mean_aerodynamic_chord_m = wing.root_chord_m

        # Dihedral
        wing.dihedral_angle_deg = 3.0 if design.aircraft_type == "fixed_wing" else 0.0

        # UAV-specific
        if design.aircraft_type == "uav":
            wing.dihedral_angle_deg = 5.0
            wing.airfoil_section = "NACA_4412"

        return wing

    def _generate_fuselage_geometry(self, design: AircraftConfiguration) -> FuselageGeometry:
        """Generate fuselage geometry from design parameters."""
        fuselage = FuselageGeometry()

        # Fuselage length estimation
        if design.max_takeoff_mass_kg > 0:
            fuselage.length_m = 0.8 * (design.max_takeoff_mass_kg ** 0.333)
        else:
            fuselage.length_m = 5.0

        # Max width and height
        fuselage.max_width_m = fuselage.length_m * 0.12
        fuselage.max_height_m = fuselage.length_m * 0.14

        # Fineness ratio
        fuselage.fineness_ratio = fuselage.length_m / fuselage.max_width_m if fuselage.max_width_m > 0 else 0.0

        # Cross section area (approximate ellipse)
        fuselage.cross_section_area_m2 = math.pi * (fuselage.max_width_m / 2) * (fuselage.max_height_m / 2)

        # Cabin, nose, tail lengths
        fuselage.cabin_length_m = fuselage.length_m * 0.5
        fuselage.nose_length_m = fuselage.length_m * 0.15
        fuselage.tail_length_m = fuselage.length_m * 0.35

        # Cargo volume (approximate)
        fuselage.cargo_volume_m3 = fuselage.cross_section_area_m2 * fuselage.cabin_length_m * 0.6

        return fuselage

    def _generate_empennage_geometry(self, design: AircraftConfiguration, wing: WingGeometry) -> EmpennageGeometry:
        """Generate empennage geometry."""
        emp = EmpennageGeometry()

        # Tail sizing ratios
        ht_volume_coeff = 0.8  # Horizontal tail volume coefficient
        vt_volume_coeff = 0.06  # Vertical tail volume coefficient

        # Tail arm (distance from wing to tail)
        fuselage_length = 0.8 * (design.max_takeoff_mass_kg ** 0.333) if design.max_takeoff_mass_kg > 0 else 5.0
        emp.tail_arm_m = fuselage_length * 0.55

        # Horizontal tail
        if emp.tail_arm_m > 0:
            emp.horizontal_tail_area_m2 = (ht_volume_coeff * wing.mean_aerodynamic_chord_m * design.wing_area_m2) / emp.tail_arm_m
        else:
            emp.horizontal_tail_area_m2 = design.wing_area_m2 * 0.2

        emp.horizontal_tail_aspect_ratio = 4.0
        emp.horizontal_tail_span_m = math.sqrt(emp.horizontal_tail_area_m2 * emp.horizontal_tail_aspect_ratio)

        # Vertical tail
        if emp.tail_arm_m > 0:
            emp.vertical_tail_area_m2 = (vt_volume_coeff * design.wing_span_m * design.wing_area_m2) / emp.tail_arm_m
        else:
            emp.vertical_tail_area_m2 = design.wing_area_m2 * 0.12

        emp.vertical_tail_aspect_ratio = 1.5
        emp.vertical_tail_height_m = math.sqrt(emp.vertical_tail_area_m2 * emp.vertical_tail_aspect_ratio)

        return emp

    def _get_landing_gear(self, design: AircraftConfiguration, gear_type: str) -> LandingGearGeometry:
        """Generate landing gear geometry."""
        gear = LandingGearGeometry()
        gear.gear_type = gear_type

        if gear_type == "tricycle":
            gear.wheel_base_m = 0.7 * (0.8 * (design.max_takeoff_mass_kg ** 0.333) if design.max_takeoff_mass_kg > 0 else 5.0)
            gear.wheel_track_m = gear.wheel_base_m * 0.3
            gear.nose_gear_length_m = 0.5
            gear.main_gear_length_m = 0.6
        elif gear_type == "tail_dragger":
            gear.wheel_base_m = 0.65 * (0.8 * (design.max_takeoff_mass_kg ** 0.333) if design.max_takeoff_mass_kg > 0 else 5.0)
            gear.wheel_track_m = gear.wheel_base_m * 0.35
            gear.main_gear_length_m = 0.5

        # Tire size estimation
        if design.max_takeoff_mass_kg < 1000:
            gear.tire_size = "15x6"
        elif design.max_takeoff_mass_kg < 10000:
            gear.tire_size = "22x8"
        else:
            gear.tire_size = "30x10"

        return gear

    def _generate_structural_layout(self, design: AircraftConfiguration, wing: WingGeometry) -> Dict[str, Any]:
        """Generate structural layout definition."""
        return {
            "fuselage_frames": max(15, int(0.8 * (design.max_takeoff_mass_kg ** 0.333) / 0.5) if design.max_takeoff_mass_kg > 0 else 10),
            "wing_ribs": max(10, int(design.wing_span_m / 0.5) if design.wing_span_m > 0 else 10),
            "wing_spars": 2,
            "stringers": 20,
            "bulkheads": 4,
            "primary_material": "aluminum_2024",
            "skin_material": "aluminum_clad",
            "wing_structure": "two_spar",
            "fuselage_structure": "semi_monocoque",
        }

    def _generate_control_surfaces(self, design: AircraftConfiguration, wing: WingGeometry) -> List[Dict[str, Any]]:
        """Generate control surface definitions."""
        surfaces = [
            {
                "name": "aileron_left",
                "type": "aileron",
                "span_m": wing.span_m * 0.15,
                "chord_ratio": 0.25,
                "deflection_deg": 25,
                "location": "outboard_trailing_edge",
            },
            {
                "name": "aileron_right",
                "type": "aileron",
                "span_m": wing.span_m * 0.15,
                "chord_ratio": 0.25,
                "deflection_deg": 25,
                "location": "outboard_trailing_edge",
            },
            {
                "name": "elevator",
                "type": "elevator",
                "span_m": 1.0,
                "chord_ratio": 0.30,
                "deflection_deg": 30,
                "location": "horizontal_tail",
            },
            {
                "name": "rudder",
                "type": "rudder",
                "span_m": 1.0,
                "chord_ratio": 0.30,
                "deflection_deg": 30,
                "location": "vertical_tail",
            },
        ]

        if design.mission_profile == "aerobatic":
            surfaces.append({
                "name": "flaps",
                "type": "flap",
                "span_m": wing.span_m * 0.40,
                "chord_ratio": 0.20,
                "deflection_deg": 40,
                "location": "inboard_trailing_edge",
            })

        return surfaces

    def _apply_variant_transform(self, base: CompleteConfiguration, variant: str) -> CompleteConfiguration:
        """Apply a variant transformation to a base configuration."""
        import copy
        new_config = copy.deepcopy(base)
        new_config.id = str(uuid.uuid4())
        new_config.configuration_variant = variant

        if variant == "long_range":
            if new_config.wing:
                new_config.wing.sweep_angle_deg = base.wing.sweep_angle_deg + 5 if base.wing else 0
                new_config.wing.span_m = base.wing.span_m * 1.15 if base.wing else 0
                new_config.wing.area_m2 = base.wing.area_m2 * 1.10 if base.wing else 0
        elif variant == "high_payload":
            if new_config.fuselage:
                new_config.fuselage.length_m = base.fuselage.length_m * 1.2 if base.fuselage else 0
                new_config.fuselage.max_width_m = base.fuselage.max_width_m * 1.15 if base.fuselage else 0
        elif variant == "high_speed":
            if new_config.wing:
                new_config.wing.sweep_angle_deg = base.wing.sweep_angle_deg + 10 if base.wing else 0
                new_config.wing.taper_ratio = base.wing.taper_ratio * 0.9 if base.wing else 0
        elif variant == "stealth":
            if new_config.wing:
                new_config.wing.sweep_angle_deg = 45
            new_config.structural_layout["skin_material"] = "radar_absorbent"

        new_config.name = f"{base.name}_{variant}"
        return new_config