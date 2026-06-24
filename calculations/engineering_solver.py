"""
Engineering solver for multi-domain calculations.
Provides domain-specific solvers for mechanical, aerospace, and electrical problems.
"""
from physics.mechanics_engine import MechanicsEngine
from physics.fluid_engine import FluidEngine
from physics.thermodynamics_engine import ThermodynamicsEngine
from physics.electromagnetics_engine import ElectromagneticsEngine
from math_engine.numerical_solver import NumericalSolver


class EngineeringSolver:
    """Domain-specific engineering solvers."""

    def __init__(self):
        self.mechanics = MechanicsEngine()
        self.fluid = FluidEngine()
        self.thermal = ThermodynamicsEngine()
        self.electrical = ElectromagneticsEngine()
        self.numerical = NumericalSolver()

    def solve_mechanical(self, problem_type: str, params: dict) -> dict:
        """Solve mechanical engineering problems."""
        solvers = {
            "bending": lambda: self.mechanics.beam_bending_stress(
                params.get("M", 0), params.get("c", 0), params.get("I", 1)),
            "buckling": lambda: self.mechanics.column_buckling(
                params.get("E", 200e9), params.get("I", 1e-6), params.get("L", 1)),
            "deflection": lambda: self.mechanics.beam_deflection(
                params.get("P", 0), params.get("L", 1), params.get("E", 200e9),
                params.get("I", 1e-6), params.get("load_type", "point_center")),
            "safety": lambda: self.mechanics.safety_factor(
                params.get("yield_strength", 250e6), params.get("working_stress", 100e6)),
        }
        solver = solvers.get(problem_type)
        if solver:
            result = solver()
            return {"domain": "mechanical", "problem": problem_type, **result.result}
        return {"error": f"Unknown mechanical problem: {problem_type}"}

    def solve_aerospace(self, problem_type: str, params: dict) -> dict:
        """Solve aerospace engineering problems."""
        solvers = {
            "lift": lambda: self.fluid.lift_force(
                params.get("Cl", 0), params.get("rho", 1.225),
                params.get("v", 0), params.get("S", 0)),
            "drag": lambda: self.fluid.drag_force(
                params.get("Cd", 0), params.get("rho", 1.225),
                params.get("v", 0), params.get("S", 0)),
            "reynolds": lambda: self.fluid.reynolds_number(
                params.get("rho", 0), params.get("v", 0),
                params.get("L", 0), params.get("mu", 0)),
            "mach": lambda: self.fluid.mach_number(
                params.get("v", 0), params.get("T", 288)),
        }
        solver = solvers.get(problem_type)
        if solver:
            result = solver()
            return {"domain": "aerospace", "problem": problem_type, **result.result}
        return {"error": f"Unknown aerospace problem: {problem_type}"}

    def solve_thermal(self, problem_type: str, params: dict) -> dict:
        """Solve thermal engineering problems."""
        solvers = {
            "conduction": lambda: self.thermal.heat_conduction(
                params.get("k", 0), params.get("A", 0),
                params.get("dT", 0), params.get("L", 0)),
            "convection": lambda: self.thermal.heat_convection(
                params.get("h", 0), params.get("A", 0), params.get("dT", 0)),
            "gas_law": lambda: self.thermal.ideal_gas_law(
                params.get("P", 0), params.get("V", 0), params.get("n", 1)),
        }
        solver = solvers.get(problem_type)
        if solver:
            result = solver()
            return {"domain": "thermal", "problem": problem_type, **result.result}
        return {"error": f"Unknown thermal problem: {problem_type}"}

    def solve_electrical(self, problem_type: str, params: dict) -> dict:
        """Solve electrical engineering problems."""
        solvers = {
            "ohms_law": lambda: self.electrical.ohms_law(
                params.get("V"), params.get("I"), params.get("R")),
            "power": lambda: self.electrical.power_electrical(
                params.get("V"), params.get("I"), params.get("R")),
            "resonance": lambda: self.electrical.resonant_frequency(
                params.get("L", 0), params.get("C", 0)),
        }
        solver = solvers.get(problem_type)
        if solver:
            result = solver()
            return {"domain": "electrical", "problem": problem_type, **result.result}
        return {"error": f"Unknown electrical problem: {problem_type}"}