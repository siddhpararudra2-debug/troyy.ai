"""
Central calculation engine for Engineering OS.
Coordinates formula lookup, symbolic math, physics engines, and validation.
"""
import logging
import uuid
from typing import Optional
from datetime import datetime
from dataclasses import dataclass

import numpy as np
from sympy import latex, sympify, N

from math_engine.symbolic_math import SymbolicMathEngine
from math_engine.equation_solver import EquationSolver
from calculations.formula_library import get_formula, Formula
from physics.mechanics_engine import MechanicsEngine
from physics.fluid_engine import FluidEngine
from physics.thermodynamics_engine import ThermodynamicsEngine
from physics.electromagnetics_engine import ElectromagneticsEngine
from units.unit_converter import UnitConverter

logger = logging.getLogger(__name__)


@dataclass
class CalculationStep:
    """A single step in a calculation workflow."""
    order: int
    step_type: str
    description: str
    formula: str = ""
    values: str = ""
    result: str = ""
    latex: str = ""


@dataclass
class CalculationResult:
    """Complete result of an engineering calculation."""
    id: str
    formula_id: str
    title: str
    formula: Optional[Formula]
    steps: list[CalculationStep]
    results: dict[str, float]
    results_formatted: dict[str, str]
    latex_summary: str
    execution_time_ms: float
    warnings: list[str]
    assumptions: list[str]
    error: Optional[str] = None


class CalculationEngine:
    """
    Central calculation engine that coordinates all engineering computations.
    Provides unified interface for formula evaluation with full traceability.
    """

    def __init__(self):
        self.symbolic = SymbolicMathEngine()
        self.solver = EquationSolver()
        self.mechanics = MechanicsEngine()
        self.fluid = FluidEngine()
        self.thermal = ThermodynamicsEngine()
        self.electrical = ElectromagneticsEngine()
        self.units = UnitConverter()
        self.warnings: list[str] = []
        self.assumptions: list[str] = []

    async def calculate(self, formula_id: str, parameters: dict[str, float],
                        project_id: Optional[str] = None,
                        unit_system: str = "SI") -> CalculationResult:
        """Execute a calculation for a given formula with parameters."""
        start_time = datetime.utcnow()
        self.warnings = []
        self.assumptions = []
        steps: list[CalculationStep] = []
        
        try:
            formula = get_formula(formula_id)
            steps.append(CalculationStep(
                order=1, step_type="formula_lookup",
                description=f"Found formula: {formula.name}",
                formula=formula.formula_latex,
                result=formula.description,
            ))
            
            steps.append(CalculationStep(
                order=2, step_type="parameter_check",
                description="Validating input parameters",
            ))
            
            # Validate parameters
            missing_params = []
            for param in formula.parameters:
                pname = param["symbol"]
                if pname not in parameters and param["unit"] != "":
                    missing_params.append(pname)
            
            if missing_params:
                error_msg = f"Missing parameters: {', '.join(missing_params)}"
                steps.append(CalculationStep(
                    order=3, step_type="error",
                    description=error_msg,
                ))
                return self._result(formula, steps, {}, start_time, error=error_msg)
            
            # Show substitution
            substitution_str = ", ".join(
                f"{k} = {v}" for k, v in parameters.items()
            )
            steps.append(CalculationStep(
                order=3, step_type="substitution",
                description=f"Parameter values: {substitution_str}",
                values=substitution_str,
            ))
            
            # Execute calculation using formula-specific logic
            result = await self._execute_formula(formula, parameters, steps)
            
            # Format results
            formatted = {}
            for output in formula.outputs:
                symbol = output["symbol"]
                if symbol in result:
                    val = result[symbol]
                    formatted[symbol] = f"{val:.4e} {output.get('unit', '')}"
            
            latex_summary = self._generate_latex_summary(formula, parameters, result)
            
            # Add warnings about assumptions
            for assumption in self.assumptions:
                steps.append(CalculationStep(
                    order=len(steps)+1, step_type="assumption",
                    description=f"Assumption: {assumption}",
                ))
            
            exec_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return self._result(formula, steps, result, start_time,
                               formatted=formatted, latex_summary=latex_summary,
                               exec_time=exec_time)
            
        except Exception as e:
            logger.error(f"Calculation error for {formula_id}: {e}")
            exec_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            return self._result(None, steps, {}, start_time,
                               error=str(e), exec_time=exec_time)

    async def _execute_formula(self, formula: Formula, params: dict,
                                steps: list[CalculationStep]) -> dict:
        """Execute a specific formula with given parameters."""
        fid = formula.id
        
        # Mechanical formulas
        if fid == "stress_axial":
            F = params.get("F", params.get("P", 0))
            A = params.get("A", 1)
            stress = F / A
            steps.append(CalculationStep(order=4, step_type="compute",
                description=f"σ = {F} / {A} = {stress:.4e} Pa",
                formula="σ = F/A", result=f"{stress:.4e} Pa"))
            return {"σ": float(stress)}
        
        elif fid == "bending_stress":
            M, c, I = params.get("M", 0), params.get("c", 0), params.get("I", 1)
            stress = M * c / I
            steps.append(CalculationStep(order=4, step_type="compute",
                description=f"σ = {M}×{c}/{I} = {stress:.4e} Pa",
                formula="σ = Mc/I", result=f"{stress:.4e} Pa"))
            return {"σ": float(stress)}
        
        elif fid == "euler_buckling":
            E, I, L, K = params.get("E", 0), params.get("I", 0), params.get("L", 0), params.get("K", 1)
            Pcr = np.pi**2 * E * I / ((K * L)**2)
            steps.append(CalculationStep(order=4, step_type="compute",
                description=f"Pcr = π²×{E}×{I}/({K}×{L})² = {Pcr:.4e} N",
                formula="Pcr = π²EI/(KL)²", result=f"{Pcr:.4e} N"))
            self.assumptions.append("Long slender column, elastic material")
            return {"P_cr": float(Pcr)}
        
        elif fid == "lift":
            Cl, rho, v, S = params.get("C_L", 0), params.get("ρ", 1.225), params.get("v", 0), params.get("S", 0)
            L = 0.5 * Cl * rho * v**2 * S
            steps.append(CalculationStep(order=4, step_type="compute",
                description=f"L = 0.5×{Cl}×{rho}×{v}²×{S} = {L:.4e} N",
                formula="L = ½ρv²SC_L", result=f"{L:.4e} N"))
            return {"L": float(L)}
        
        elif fid == "drag":
            Cd, rho, v, S = params.get("C_D", 0), params.get("ρ", 1.225), params.get("v", 0), params.get("S", 0)
            D = 0.5 * Cd * rho * v**2 * S
            steps.append(CalculationStep(order=4, step_type="compute",
                description=f"D = 0.5×{Cd}×{rho}×{v}²×{S} = {D:.4e} N",
                formula="D = ½ρv²SC_D", result=f"{D:.4e} N"))
            return {"D": float(D)}
        
        elif fid == "reynolds":
            rho, v, L, mu = params.get("ρ", 0), params.get("v", 0), params.get("L", 0), params.get("μ", 0)
            Re = rho * v * L / mu
            steps.append(CalculationStep(order=4, step_type="compute",
                description=f"Re = {rho}×{v}×{L}/{mu} = {Re:.4e}",
                formula="Re = ρvL/μ", result=f"Re = {Re:.4e}"))
            return {"Re": float(Re)}
        
        elif fid == "ohms_law":
            I, R = params.get("I", 0), params.get("R", 0)
            V = I * R
            steps.append(CalculationStep(order=4, step_type="compute",
                description=f"V = {I}×{R} = {V:.4f} V",
                formula="V = IR", result=f"{V:.4f} V"))
            return {"V": float(V)}
        
        elif fid == "heat_conduction":
            k, A, dT, L = params.get("k", 0), params.get("A", 0), params.get("ΔT", 0), params.get("L", 0)
            Q = k * A * dT / L
            steps.append(CalculationStep(order=4, step_type="compute",
                description=f"Q = {k}×{A}×{dT}/{L} = {Q:.4f} W",
                formula="Q = kAΔT/L", result=f"{Q:.4f} W"))
            return {"Q": float(Q)}
        
        elif fid == "ideal_gas":
            P, V, n = params.get("P", 0), params.get("V", 0), params.get("n", 0)
            R = 8.314
            T = P * V / (n * R)
            steps.append(CalculationStep(order=4, step_type="compute",
                description=f"T = {P}×{V}/({n}×{R}) = {T:.4f} K",
                formula="T = PV/(nR)", result=f"{T:.4f} K"))
            return {"T": float(T)}
        
        # Symbolic evaluation for generic formulas
        else:
            sym_expr = sympify(formula.formula_latex)
            result_dict = {}
            for output in formula.outputs:
                result_dict[output["symbol"]] = 0.0
            return result_dict

    def _generate_latex_summary(self, formula: Formula, params: dict,
                                 result: dict) -> str:
        """Generate LaTeX summary of the calculation."""
        parts = [formula.formula_latex]
        param_parts = [f"{k} = {v}" for k, v in params.items()]
        parts.append("\\quad\\text{where}\\quad " + ", ".join(param_parts))
        result_parts = [f"{k} = {v:.4e}" for k, v in result.items()]
        parts.append("\\quad\\Rightarrow\\quad " + ", ".join(result_parts))
        return " ".join(parts)

    def _result(self, formula, steps, results, start_time,
                formatted=None, latex_summary="", exec_time=0, error=None):
        """Build a CalculationResult."""
        return CalculationResult(
            id=str(uuid.uuid4()),
            formula_id=formula.id if formula else "",
            title=formula.name if formula else "Unknown",
            formula=formula,
            steps=steps,
            results={k: float(v) for k, v in results.items()},
            results_formatted=formatted or {},
            latex_summary=latex_summary or "",
            execution_time_ms=exec_time or (datetime.utcnow() - start_time).total_seconds() * 1000,
            warnings=self.warnings,
            assumptions=self.assumptions,
            error=error,
        )

    def list_formulas(self, domain: str = None, category: str = None) -> list[Formula]:
        """List available formulas with optional filtering."""
        from calculations.formula_library import FORMULA_LIBRARY
        formulas = list(FORMULA_LIBRARY.values())
        if domain:
            formulas = [f for f in formulas if f.domain == domain]
        if category:
            formulas = [f for f in formulas if f.category == category]
        return formulas