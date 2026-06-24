"""
Equation solver for Engineering OS.
Solves algebraic, differential, and systems of equations with step-by-step output.
"""
import logging
from typing import Optional
from sympy import (
    symbols, solve, solveset, nonlinsolve, linsolve, Eq,
    linear_eq_to_matrix, dsolve, classify_ode, checkodesol,
    simplify, latex, sympify, sqrt, Abs, oo, S,
    Symbol, Function, Derivative,
)

from math_engine.symbolic_math import SymbolicMathEngine, Step, DerivationResult

logger = logging.getLogger(__name__)


class EquationSolver:
    """
    Solves algebraic equations, ODEs, and systems of equations.
    Provides step-by-step solutions for engineering problems.
    """

    def __init__(self):
        self.parser = SymbolicMathEngine()

    def solve_linear(self, equation_str: str, variable: str = "x") -> DerivationResult:
        """Solve a single linear equation."""
        eq = self.parser.parse_equation(equation_str)
        var = symbols(variable)
        steps = [
            Step("Equation to solve", str(eq), latex(eq)),
        ]
        
        solution = solve(eq, var)
        steps.append(Step(
            "Isolate variable and solve",
            str(solution),
            latex(solution),
        ))
        
        return DerivationResult(
            result=str(solution),
            steps=steps,
            latex_result=latex(solution),
        )

    def solve_quadratic(self, equation_str: str, variable: str = "x") -> DerivationResult:
        """Solve a quadratic equation with step-by-step quadratic formula."""
        eq = self.parser.parse_equation(equation_str)
        var = symbols(variable)
        
        # Standard form: ax^2 + bx + c = 0
        from sympy import Poly, degree
        poly = Poly(eq.lhs - eq.rhs, var)
        coeffs = poly.all_coeffs()
        
        steps = [
            Step("Equation in standard form", str(eq), latex(eq)),
        ]
        
        a, b, c = coeffs[0], coeffs[1], coeffs[2]
        steps.append(Step(
            f"Identify coefficients: a={a}, b={b}, c={c}",
            f"a={a}, b={b}, c={c}",
            f"a={latex(a)}, b={latex(b)}, c={latex(c)}",
        ))
        
        # Quadratic formula
        discriminant = b**2 - 4*a*c
        steps.append(Step(
            f"Discriminant Δ = b² - 4ac = {discriminant}",
            str(discriminant),
            latex(discriminant),
        ))
        
        solution = solve(eq, var)
        steps.append(Step(
            "Apply quadratic formula: x = (-b ± √Δ) / (2a)",
            str(solution),
            latex(solution),
        ))
        
        return DerivationResult(
            result=str(solution),
            steps=steps,
            latex_result=latex(solution),
        )

    def solve_system(
        self, equations: list[str], variables: list[str]
    ) -> DerivationResult:
        """Solve a system of linear equations."""
        sym_vars = symbols(variables)
        
        eqs = []
        steps = []
        
        for i, eq_str in enumerate(equations):
            eq = self.parser.parse_equation(eq_str)
            eqs.append(eq)
            steps.append(Step(
                f"Equation {i+1}",
                str(eq),
                latex(eq),
            ))
        
        # Try linear system first
        try:
            A, b = linear_eq_to_matrix([e.lhs - e.rhs for e in eqs], sym_vars)
            steps.append(Step(
                "Write in matrix form Ax = b",
                f"A={A}, b={b}",
                f"A={latex(A)}, b={latex(b)}",
            ))
            
            solution = linsolve((A, b), sym_vars)
            steps.append(Step(
                "Solution",
                str(solution),
                latex(solution),
            ))
        except Exception:
            # Non-linear system
            solution = solve(eqs, sym_vars, dict=True)
            steps.append(Step(
                "Solution (non-linear system)",
                str(solution),
                latex(solution),
            ))
        
        return DerivationResult(
            result=str(solution),
            steps=steps,
            latex_result=latex(solution),
        )

    def solve_ode(self, ode_str: str, function_str: str = "f(x)",
                  ics: Optional[dict] = None) -> DerivationResult:
        """Solve an ordinary differential equation."""
        # Parse ODE: e.g., "diff(f(x), x, 2) + 3*diff(f(x), x) + 2*f(x) = 0"
        x = symbols("x")
        f = Function("f")
        eq = self.parser.parse_equation(ode_str)
        
        steps = [
            Step("Original ODE", str(eq), latex(eq)),
        ]
        
        # Classify the ODE
        ode_type = classify_ode(eq, f(x))
        steps.append(Step(
            f"ODE classification: {ode_type}",
            str(ode_type),
            latex(ode_type),
        ))
        
        # Solve
        if ics:
            solution = dsolve(eq, f(x), ics=ics)
        else:
            solution = dsolve(eq, f(x))
        
        steps.append(Step(
            "General solution",
            str(solution),
            latex(solution),
        ))
        
        return DerivationResult(
            result=str(solution),
            steps=steps,
            latex_result=latex(solution),
        )

    def solve_polynomial(self, equation_str: str, variable: str = "x") -> DerivationResult:
        """Solve a polynomial equation of any degree."""
        eq = self.parser.parse_equation(equation_str)
        var = symbols(variable)
        
        steps = [
            Step("Polynomial equation", str(eq), latex(eq)),
        ]
        
        from sympy import degree, Poly
        poly = Poly(eq.lhs - eq.rhs, var)
        deg = degree(poly)
        steps.append(Step(
            f"Degree of polynomial: {deg}",
            str(deg),
            str(deg),
        ))
        
        if deg <= 2:
            return self.solve_quadratic(equation_str, variable)
        
        solution = solve(eq, var)
        steps.append(Step(
            f"Solutions (degree {deg})",
            str(solution),
            latex(solution),
        ))
        
        return DerivationResult(
            result=str(solution),
            steps=steps,
            latex_result=latex(solution),
        )