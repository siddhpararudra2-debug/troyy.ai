"""
Wing Designer - Wing Design and Optimization.

Capabilities:
- Airfoil selection
- Wing planform design
- High-lift device design
"""

from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
import math
import uuid
from datetime import datetime


@dataclass
class AirfoilData:
    """Airfoil characteristics."""
    name: str = ""
    cl_max: float = 1.5
    cl_alpha_slope: float = 6.28
    cd0: float = 0.006
    cm_quarter: float = -0.05
    stall_angle_deg: float = 15.0
    thickness_ratio: float = 0.12
    camber_ratio: float = 0.02
    family: str = "naca"


@dataclass
class WingDesign:
    """Complete wing design definition."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    wing_type: str = "tapered"
    span_m: float = 0.0
    area_m2: float = 0.0
    aspect_ratio: float = 0.0
    root_chord_m: float = 0.0
    tip_chord_m: float = 0.0
    mac_m: float = 0.0
    sweep_angle_deg: float = 0.0
    dihedral_angle_deg: float = 0.0
    incidence_angle_deg: float = 2.0
    twist_angle_deg: float = -1.0
    taper_ratio: float = 0.0
    airfoil_root: str = "NACA_2412"
    airfoil_tip: str = "NACA_0012"
    washout_deg: float = -2.0
    high_lift_devices: List[Dict[str, Any]] = field(default_factory=list)


class WingDesigner:
    """Wing design and analysis engine."""

    def __init__(self):
        self.designs: Dict[str, WingDesign] = {}
        self._airfoil_library = self._init_airfoil_library()

    def design_wing(
        self,
        span_m: float,
        area_m2: float,
        wing_type: str = "tapered",
        taper_ratio: float = 0.4,
        sweep_angle_deg: float = 0.0,
        airfoil: str = "NACA_2412",
    ) -> WingDesign:
        """Design a wing from high-level parameters."""
        design = WingDesign(
            wing_type=wing_type,
            span_m=span_m,
            area_m2=area_m2,
            taper_ratio=taper_ratio,
            sweep_angle_deg=sweep_angle_deg,
            airfoil_root=airfoil,
            airfoil_tip=airfoil,
        )

        design.aspect_ratio = span_m**2 / area_m2 if area_m2 > 0 else 0.0
        design.root_chord_m = 2 * area_m2 / (span_m * (1 + taper_ratio)) if span_m > 0 else 0.0
        design.tip_chord_m = design.root_chord_m * taper_ratio if design.root_chord_m > 0 else 0.0

        # Mean aerodynamic chord
        if taper_ratio > 0:
            design.mac_m = (2.0 / 3.0) * design.root_chord_m * ((1 + taper_ratio + taper_ratio**2) / (1 + taper_ratio))
        else:
            design.mac_m = design.root_chord_m

        design.washout_deg = -2.0 if sweep_angle_deg > 10 else -1.0
        self.designs[design.id] = design
        return design

    def design_rectangular_wing(self, span_m: float, chord_m: float) -> WingDesign:
        """Design a simple rectangular wing."""
        return self.design_wing(span_m, span_m * chord_m, "rectangular", 1.0, 0.0)

    def design_delta_wing(self, span_m: float, root_chord_m: float) -> WingDesign:
        """Design a delta wing."""
        return self.design_wing(span_m, 0.5 * span_m * root_chord_m, "delta", 0.1, 60.0)

    def get_design(self, design_id: str) -> Optional[WingDesign]:
        return self.designs.get(design_id)

    def _init_airfoil_library(self) -> Dict[str, AirfoilData]:
        return {
            "NACA_2412": AirfoilData("NACA_2412", 1.6, 6.28, 0.006, -0.05, 16, 0.12, 0.02),
            "NACA_4412": AirfoilData("NACA_4412", 1.7, 6.28, 0.007, -0.08, 15, 0.12, 0.04),
            "NACA_0012": AirfoilData("NACA_0012", 1.4, 6.28, 0.005, 0.0, 14, 0.12, 0.0),
            "NACA_23012": AirfoilData("NACA_23012", 1.6, 6.15, 0.006, -0.02, 15, 0.12, 0.018),
            "NACA_6412": AirfoilData("NACA_6412", 1.8, 6.28, 0.008, -0.10, 14, 0.12, 0.06),
        }