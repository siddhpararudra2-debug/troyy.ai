"""
Mechanics engine for Engineering OS.
Provides statics, dynamics, strength of materials, and structural analysis.
"""
import logging
import numpy as np
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Force:
    """A force vector in 2D or 3D space."""
    fx: float = 0.0
    fy: float = 0.0
    fz: float = 0.0
    unit: str = "N"


@dataclass
class Moment:
    """A moment/torque vector."""
    mx: float = 0.0
    my: float = 0.0
    mz: float = 0.0
    unit: str = "N·m"


@dataclass
class StressState:
    """Stress state at a point."""
    sigma_x: float = 0.0  # Pa
    sigma_y: float = 0.0
    sigma_z: float = 0.0
    tau_xy: float = 0.0
    tau_yz: float = 0.0
    tau_zx: float = 0.0
    unit: str = "Pa"


@dataclass
class MechanicsResult:
    """Result of a mechanics calculation with steps."""
    result: dict
    steps: list[dict]
    assumptions: list[str]


class MechanicsEngine:
    """
    Engineering mechanics calculations for statics, dynamics, and structures.
    """

    GRAVITY = 9.80665  # m/s²

    def sum_forces(self, forces: list[Force]) -> MechanicsResult:
        """Compute resultant force from multiple forces."""
        fx = sum(f.fx for f in forces)
        fy = sum(f.fy for f in forces)
        fz = sum(f.fz for f in forces)
        
        magnitude = np.sqrt(fx**2 + fy**2 + fz**2)
        
        steps = [
            {
                "description": "Sum forces in x-direction",
                "formula": "ΣFx = ΣF_xi",
                "result": f"{fx:.4f} N",
            },
            {
                "description": "Sum forces in y-direction",
                "formula": "ΣFy = ΣF_yi",
                "result": f"{fy:.4f} N",
            },
            {
                "description": "Sum forces in z-direction",
                "formula": "ΣFz = ΣF_zi",
                "result": f"{fz:.4f} N",
            },
            {
                "description": "Resultant magnitude",
                "formula": "|F| = √(Fx² + Fy² + Fz²)",
                "result": f"{magnitude:.4f} N",
            },
        ]
        
        return MechanicsResult(
            result={
                "fx": fx, "fy": fy, "fz": fz,
                "magnitude": float(magnitude),
            },
            steps=steps,
            assumptions=["Forces are concurrent"],
        )

    def beam_bending_stress(
        self, moment: float, c: float, I: float
    ) -> MechanicsResult:
        """Calculate bending stress in a beam: σ = Mc/I."""
        stress = moment * c / I
        
        steps = [
            {
                "description": "Apply flexure formula",
                "formula": "σ = M × c / I",
                "values": f"σ = {moment} × {c} / {I}",
                "result": f"{stress:.4e} Pa",
            },
        ]
        
        return MechanicsResult(
            result={"bending_stress": float(stress), "unit": "Pa"},
            steps=steps,
            assumptions=[
                "Linear elastic material",
                "Plane sections remain plane",
                "Homogeneous isotropic material",
            ],
        )

    def shear_stress_beam(
        self, V: float, Q: float, I: float, b: float
    ) -> MechanicsResult:
        """Calculate shear stress: τ = VQ/(Ib)."""
        stress = V * Q / (I * b)
        
        steps = [
            {
                "description": "Apply shear stress formula",
                "formula": "τ = V × Q / (I × b)",
                "values": f"τ = {V} × {Q} / ({I} × {b})",
                "result": f"{stress:.4e} Pa",
            },
        ]
        
        return MechanicsResult(
            result={"shear_stress": float(stress), "unit": "Pa"},
            steps=steps,
            assumptions=["Rectangular cross-section", "Elastic behavior"],
        )

    def torsional_stress(self, T: float, r: float, J: float) -> MechanicsResult:
        """Calculate torsional shear stress: τ = Tr/J."""
        stress = T * r / J
        
        steps = [
            {
                "description": "Apply torsion formula",
                "formula": "τ = T × r / J",
                "values": f"τ = {T} × {r} / {J}",
                "result": f"{stress:.4e} Pa",
            },
        ]
        
        return MechanicsResult(
            result={"torsional_stress": float(stress), "unit": "Pa"},
            steps=steps,
            assumptions=["Circular cross-section", "Elastic torsion"],
        )

    def beam_deflection(
        self, load: float, length: float, E: float, I: float,
        load_type: str = "point_center"
    ) -> MechanicsResult:
        """Calculate beam deflection for common loading cases."""
        steps = []
        
        if load_type == "point_center":
            # Simply supported, point load at center
            deflection = load * length**3 / (48 * E * I)
            formula = "δ = PL³/(48EI)"
            steps.append({
                "description": f"Simply supported beam, point load at center",
                "formula": formula,
                "values": f"δ = {load} × {length}³ / (48 × {E} × {I})",
                "result": f"{deflection:.4e} m",
            })
        elif load_type == "uniform":
            # Simply supported, uniformly distributed load
            deflection = 5 * load * length**4 / (384 * E * I)
            formula = "δ = 5wL⁴/(384EI)"
            steps.append({
                "description": f"Simply supported beam, UDL",
                "formula": formula,
                "values": f"δ = 5 × {load} × {length}⁴ / (384 × {E} × {I})",
                "result": f"{deflection:.4e} m",
            })
        elif load_type == "cantilever_point":
            # Cantilever, point load at free end
            deflection = load * length**3 / (3 * E * I)
            formula = "δ = PL³/(3EI)"
            steps.append({
                "description": f"Cantilever beam, point load at end",
                "formula": formula,
                "values": f"δ = {load} × {length}³ / (3 × {E} × {I})",
                "result": f"{deflection:.4e} m",
            })
        else:
            raise ValueError(f"Unknown load type: {load_type}")
        
        return MechanicsResult(
            result={"deflection": float(deflection), "unit": "m"},
            steps=steps,
            assumptions=[
                "Small deflections (linear)",
                "Elastic material",
                "Euler-Bernoulli beam theory",
            ],
        )

    def column_buckling(
        self, E: float, I: float, length: float,
        end_condition: str = "pinned_pinned"
    ) -> MechanicsResult:
        """Calculate Euler buckling load for columns."""
        if end_condition == "pinned_pinned":
            K = 1.0
            desc = "Both ends pinned (K=1.0)"
        elif end_condition == "fixed_fixed":
            K = 0.5
            desc = "Both ends fixed (K=0.5)"
        elif end_condition == "fixed_free":
            K = 2.0
            desc = "One end fixed, one free (K=2.0)"
        elif end_condition == "fixed_pinned":
            K = 0.7
            desc = "One end fixed, one pinned (K=0.7)"
        else:
            raise ValueError(f"Unknown end condition: {end_condition}")
        
        P_cr = (np.pi**2 * E * I) / ((K * length)**2)
        
        steps = [
            {
                "description": f"Euler buckling analysis: {desc}",
                "formula": "P_cr = π²EI/(KL)²",
                "values": f"P_cr = π² × {E} × {I} / ({K} × {length})²",
                "result": f"{P_cr:.4e} N",
            },
        ]
        
        return MechanicsResult(
            result={"critical_load": float(P_cr), "unit": "N",
                    "effective_length_factor": K},
            steps=steps,
            assumptions=[
                "Long slender column",
                "Elastic material",
                "Concentric axial load",
                "No imperfections",
            ],
        )

    def von_mises_stress(self, stress: StressState) -> MechanicsResult:
        """Calculate von Mises equivalent stress."""
        s = stress
        sigma_vm = np.sqrt(
            0.5 * ((s.sigma_x - s.sigma_y)**2 +
                    (s.sigma_y - s.sigma_z)**2 +
                    (s.sigma_z - s.sigma_x)**2 +
                    6 * (s.tau_xy**2 + s.tau_yz**2 + s.tau_zx**2))
        )
        
        steps = [
            {
                "description": "Apply von Mises yield criterion",
                "formula": "σ_v = √(0.5[(σ₁-σ₂)² + (σ₂-σ₃)² + (σ₃-σ₁)²])",
                "result": f"{sigma_vm:.4e} Pa",
            },
        ]
        
        return MechanicsResult(
            result={"von_mises_stress": float(sigma_vm), "unit": "Pa"},
            steps=steps,
            assumptions=["Ductile material", "Isotropic hardening"],
        )

    def safety_factor(self, yield_strength: float, working_stress: float) -> MechanicsResult:
        """Calculate factor of safety."""
        fs = yield_strength / working_stress
        
        steps = [
            {
                "description": "Calculate factor of safety",
                "formula": "FS = σ_yield / σ_working",
                "values": f"FS = {yield_strength} / {working_stress}",
                "result": f"{fs:.4f}",
            },
        ]
        
        return MechanicsResult(
            result={"safety_factor": float(fs)},
            steps=steps,
            assumptions=["Static loading", "Yield-based failure"],
        )