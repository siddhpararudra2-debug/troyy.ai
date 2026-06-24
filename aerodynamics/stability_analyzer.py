"""
Stability Analyzer - Aircraft Stability and Control Analysis.

Capabilities:
- Static stability analysis
- Dynamic stability analysis
- Longitudinal/lateral-directional stability
"""

from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
import math
import uuid


@dataclass
class StabilityResult:
    """Stability analysis result."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    longitudinal_static_margin: float = 0.0
    longitudinal_natural_freq_rad_s: float = 0.0
    longitudinal_damping_ratio: float = 0.0
    lateral_dutch_roll_freq_rad_s: float = 0.0
    lateral_dutch_roll_damping: float = 0.0
    lateral_roll_time_constant_s: float = 0.0
    lateral_spiral_mode_time_constant_s: float = 0.0
    cg_position_m: float = 0.0
    neutral_point_m: float = 0.0
    is_longitudinally_stable: bool = False
    is_laterally_stable: bool = False
    stability_rating: str = "unknown"


class StabilityAnalyzer:
    """Aircraft stability analysis engine."""

    def __init__(self):
        self.results: Dict[str, StabilityResult] = {}

    def analyze_longitudinal_stability(
        self,
        wing_area_m2: float,
        wing_mac_m: float,
        horizontal_tail_area_m2: float,
        tail_arm_m: float,
        cg_position_fraction: float = 0.30,
        lift_curve_slope_wing: float = 5.0,
        lift_curve_slope_tail: float = 4.0,
        downwash_gradient: float = 0.4,
    ) -> StabilityResult:
        """Analyze longitudinal static and dynamic stability."""
        result = StabilityResult()

        # Neutral point (aerodynamic center of aircraft)
        vh = (horizontal_tail_area_m2 * tail_arm_m) / (wing_area_m2 * wing_mac_m) if wing_area_m2 * wing_mac_m > 0 else 0.0
        neutral_point = 0.25 + vh * (lift_curve_slope_tail / lift_curve_slope_wing) * (1 - downwash_gradient)
        result.neutral_point_m = neutral_point * wing_mac_m

        # CG position
        cg_pos = cg_position_fraction * wing_mac_m
        result.cg_position_m = cg_pos

        # Static margin
        result.longitudinal_static_margin = neutral_point - cg_position_fraction
        result.is_longitudinally_stable = result.longitudinal_static_margin > 0.05

        # Short period approximation
        if result.longitudinal_static_margin > 0:
            result.longitudinal_natural_freq_rad_s = math.sqrt(2 * 9.81 * result.longitudinal_static_margin / wing_mac_m) if wing_mac_m > 0 else 0.0
            result.longitudinal_damping_ratio = 0.3 + 0.1 * result.longitudinal_static_margin
        else:
            result.longitudinal_natural_freq_rad_s = 0.0
            result.longitudinal_damping_ratio = -0.1

        result.is_laterally_stable = True
        result.stability_rating = "stable" if result.is_longitudinally_stable else "unstable"

        if result.longitudinal_static_margin > 0.15:
            result.stability_rating = "very_stable"
        elif result.longitudinal_static_margin < 0.0:
            result.stability_rating = "unstable"

        self.results[result.id] = result
        return result

    def analyze_lateral_stability(
        self,
        wing_span_m: float,
        vertical_tail_area_m2: float,
        tail_arm_m: float,
        wing_area_m2: float,
        speed_ms: float = 100.0,
    ) -> StabilityResult:
        """Analyze lateral-directional stability."""
        # Use default longitudinal values for complete result
        result = self.analyze_longitudinal_stability(wing_area_m2, wing_span_m / 8, vertical_tail_area_m2, tail_arm_m)

        # Dutch roll approximation
        result.lateral_dutch_roll_freq_rad_s = speed_ms / wing_span_m * 2.0 if wing_span_m > 0 else 0.0
        result.lateral_dutch_roll_damping = 0.15

        # Roll mode time constant
        result.lateral_roll_time_constant_s = 0.5

        # Spiral mode
        result.lateral_spiral_mode_time_constant_s = 30.0

        result.is_laterally_stable = True
        return result

    def get_result(self, result_id: str) -> Optional[StabilityResult]:
        return self.results.get(result_id)