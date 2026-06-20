"""
Cost Optimizer — Component Selection & BOM Cost Reduction
Optimizes:
  - Component substitution (equivalent specs, lower cost)
  - Manufacturing process selection
  - Supply chain risk scoring
  - Volume pricing curves
  - Assembly cost estimation

Integrates with Day 27 Manufacturing schemas.
"""
from __future__ import annotations

import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

from app.optimization.schemas import (
    CostOptimizationRequest, CostOptimizationResponse,
    OptimizationDomain,
)


# ── Component Cost Database ───────────────────────────────────────────────────

_COMPONENT_COSTS: Dict[str, Dict[str, Any]] = {
    # Drone components
    "brushless_motor_400w_premium":    {"cost": 85.0,  "substitute": "brushless_motor_400w_std",  "sub_cost": 45.0,  "perf_delta": -0.05},
    "brushless_motor_400w_std":        {"cost": 45.0,  "substitute": None,                        "sub_cost": None,  "perf_delta": 0.0},
    "lipo_4s_5000mah_premium":         {"cost": 120.0, "substitute": "lipo_4s_5000mah_std",       "sub_cost": 65.0,  "perf_delta": -0.08},
    "esc_40a_premium":                 {"cost": 55.0,  "substitute": "esc_40a_std",               "sub_cost": 25.0,  "perf_delta": -0.03},
    "flight_controller_pixhawk":       {"cost": 250.0, "substitute": "flight_controller_ardupilot","sub_cost": 80.0, "perf_delta": -0.10},
    # Electronics
    "stm32h7_mcu":                     {"cost": 18.0,  "substitute": "stm32f4_mcu",               "sub_cost": 8.0,   "perf_delta": -0.20},
    "premium_mosfet":                  {"cost": 4.5,   "substitute": "std_mosfet",                "sub_cost": 1.2,   "perf_delta": -0.02},
    "premium_sensor":                  {"cost": 35.0,  "substitute": "std_sensor",                "sub_cost": 12.0,  "perf_delta": -0.05},
    # Mechanical
    "carbon_fiber_frame":              {"cost": 450.0, "substitute": "aluminum_frame",            "sub_cost": 180.0, "perf_delta": 0.15},  # heavier
    "titanium_fasteners":              {"cost": 80.0,  "substitute": "steel_fasteners",           "sub_cost": 15.0,  "perf_delta": 0.08},  # heavier
    "premium_bearing":                 {"cost": 25.0,  "substitute": "std_bearing",               "sub_cost": 8.0,   "perf_delta": -0.03},
}

_MANUFACTURING_COSTS: Dict[str, Dict[str, float]] = {
    "cnc_machining":    {"setup": 500.0, "per_hour": 85.0,  "typical_hours": 4.0},
    "3d_printing_fdm":  {"setup": 50.0,  "per_hour": 15.0,  "typical_hours": 6.0},
    "3d_printing_sla":  {"setup": 100.0, "per_hour": 25.0,  "typical_hours": 4.0},
    "casting":          {"setup": 2000.0,"per_hour": 120.0, "typical_hours": 2.0},
    "pcb_fabrication":  {"setup": 200.0, "per_board": 15.0, "typical_hours": 0.0},
    "pcb_assembly":     {"setup": 300.0, "per_component": 0.05, "typical_hours": 0.0},
}

_VOLUME_DISCOUNT_CURVES: Dict[int, float] = {
    1: 1.00, 5: 0.95, 10: 0.88, 50: 0.78, 100: 0.68, 500: 0.55, 1000: 0.45
}


class CostOptimizer:

    @staticmethod
    def optimize(request: CostOptimizationRequest) -> CostOptimizationResponse:
        t_start = time.perf_counter()

        domain = request.domain
        design = request.design
        volume = request.production_volume

        # ── Estimate Original BOM Cost ───────────────────────────────────────
        original_cost, original_breakdown = CostOptimizer._estimate_bom_cost(design, domain, volume)

        # ── Component Substitutions ──────────────────────────────────────────
        substitutions: List[Dict[str, Any]] = []
        total_savings = 0.0

        for comp_key, comp_data in _COMPONENT_COSTS.items():
            if CostOptimizer._component_present(comp_key, design):
                if comp_data["substitute"] and comp_data["sub_cost"]:
                    savings = comp_data["cost"] - comp_data["sub_cost"]
                    perf_delta = comp_data["perf_delta"]
                    if savings > 0 and (perf_delta > -0.15 or request.optimize_for == "unit_cost"):
                        substitutions.append({
                            "original": comp_key,
                            "substitute": comp_data["substitute"],
                            "original_cost_usd": comp_data["cost"],
                            "substitute_cost_usd": comp_data["sub_cost"],
                            "savings_usd": round(savings, 2),
                            "performance_impact_percent": round(perf_delta * 100, 1),
                            "recommendation": (
                                "RECOMMEND" if abs(perf_delta) < 0.10 else "REVIEW — perf impact"
                            ),
                        })
                        total_savings += savings

        # ── Manufacturing Cost Optimization ──────────────────────────────────
        mfg_savings: List[str] = []
        mfg_process = design.get("manufacturing_process", "cnc_machining")
        alt_process = "3d_printing_fdm" if mfg_process == "cnc_machining" else None
        if alt_process and alt_process in _MANUFACTURING_COSTS:
            current_mfg = _MANUFACTURING_COSTS.get(mfg_process, {})
            alt_mfg = _MANUFACTURING_COSTS[alt_process]
            current_c = current_mfg.get("setup", 500) + current_mfg.get("per_hour", 85) * current_mfg.get("typical_hours", 4)
            alt_c = alt_mfg.get("setup", 50) + alt_mfg.get("per_hour", 15) * alt_mfg.get("typical_hours", 6)
            if alt_c < current_c:
                mfg_saving = current_c - alt_c
                total_savings += mfg_saving
                mfg_savings.append(
                    f"Switch from {mfg_process} to {alt_process}: saves ${mfg_saving:.0f}/unit for prototype quantities"
                )

        # ── Volume Discount ──────────────────────────────────────────────────
        discount = CostOptimizer._get_volume_discount(volume)
        mfg_savings.append(
            f"Volume {volume} units → {(1-discount)*100:.0f}% discount on component costs"
        )

        # ── Supply Chain Risk ────────────────────────────────────────────────
        supply_risks = CostOptimizer._assess_supply_chain(design, domain)

        # ── Final Cost ───────────────────────────────────────────────────────
        optimized_cost = max(0.0, original_cost - total_savings) * discount
        savings_usd = original_cost - optimized_cost
        savings_pct = (savings_usd / original_cost * 100) if original_cost > 0 else 0.0

        # ── Strategies ───────────────────────────────────────────────────────
        strategies: List[str] = [
            f"Direct component substitution: ${sum(s['savings_usd'] for s in substitutions):.0f} savings",
            f"Volume pricing at {volume} units: {(1-discount)*100:.0f}% reduction",
        ]
        if design.get("pcb_layers", 4) > 2:
            strategies.append("Reduce PCB layer count from 4L to 2L for prototype: saves ~$8/board")
        strategies.append("Consolidate BOM: reduce unique component count to minimize tooling cost")
        strategies.extend(mfg_savings)

        optimized_breakdown = {k: v * discount for k, v in original_breakdown.items()}

        elapsed = (time.perf_counter() - t_start) * 1000
        return CostOptimizationResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            original_cost_usd=round(original_cost, 2),
            optimized_cost_usd=round(optimized_cost, 2),
            savings_usd=round(savings_usd, 2),
            savings_percent=round(savings_pct, 2),
            cost_breakdown=optimized_breakdown,
            component_substitutions=substitutions,
            manufacturing_savings=mfg_savings,
            supply_chain_risks=supply_risks,
            cost_reduction_strategies=strategies,
            trade_off_notes=(
                "Note: Component substitutions may reduce performance by up to 10–15%. "
                "Validate against performance requirements before implementation."
            ),
            elapsed_ms=round(elapsed, 2),
            created_at=datetime.utcnow(),
        )

    @staticmethod
    def _estimate_bom_cost(design: Dict[str, Any], domain: OptimizationDomain, volume: int) -> tuple:
        # Domain-typical BOM cost estimates
        base_costs: Dict[str, Dict[str, float]] = {
            OptimizationDomain.DRONE: {
                "motors": 340.0, "escs": 220.0, "battery": 120.0,
                "flight_controller": 250.0, "frame": 200.0,
                "sensors": 150.0, "misc": 100.0,
            },
            OptimizationDomain.ROBOTICS: {
                "actuators": 800.0, "gearboxes": 400.0, "controller": 200.0,
                "sensors": 300.0, "frame": 350.0, "misc": 150.0,
            },
            OptimizationDomain.ELECTRONICS: {
                "mcu": 25.0, "power_components": 80.0, "sensors": 120.0,
                "communication": 60.0, "pcb": 45.0, "passives": 30.0,
            },
            OptimizationDomain.AEROSPACE: {
                "propulsion": 2000.0, "avionics": 1500.0, "structure": 3000.0,
                "control_surfaces": 800.0, "sensors": 600.0, "misc": 500.0,
            },
        }
        breakdown = base_costs.get(domain, {"components": 500.0, "assembly": 200.0})

        # Override with any explicit cost fields in design
        for key in breakdown:
            if key + "_cost" in design:
                breakdown[key] = float(design[key + "_cost"])

        total = sum(breakdown.values())
        return total, {k: round(v, 2) for k, v in breakdown.items()}

    @staticmethod
    def _component_present(comp_key: str, design: Dict[str, Any]) -> bool:
        design_str = str(design).lower()
        return any(part in design_str for part in comp_key.split("_")[:2])

    @staticmethod
    def _get_volume_discount(volume: int) -> float:
        prev_qty = 1
        prev_discount = 1.0
        for qty, discount in sorted(_VOLUME_DISCOUNT_CURVES.items()):
            if volume <= qty:
                # Linear interpolation
                t = (volume - prev_qty) / max(qty - prev_qty, 1)
                return prev_discount + t * (discount - prev_discount)
            prev_qty, prev_discount = qty, discount
        return 0.45

    @staticmethod
    def _assess_supply_chain(design: Dict[str, Any], domain: OptimizationDomain) -> List[str]:
        risks = []
        if domain in (OptimizationDomain.DRONE, OptimizationDomain.AEROSPACE):
            risks.append(
                "Single-source risk: ESCs and flight controllers often sourced from limited suppliers. "
                "Maintain 3-month safety stock."
            )
        if domain == OptimizationDomain.ELECTRONICS:
            risks.append(
                "Semiconductor lead times: MCUs may have 20–52 week lead times. "
                "Place orders early and qualify pin-compatible alternatives."
            )
        risks.append(
            "Import tariff risk: evaluate domestic vs. international sourcing for cost-sensitive components."
        )
        risks.append(
            "Component obsolescence: verify lifetime buy availability for components on EoL roadmap."
        )
        return risks
