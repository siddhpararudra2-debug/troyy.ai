"""
Symbolic Solver — SymPy-based symbolic mathematics
Handles algebra, equation solving, simplification, step-by-step derivation
"""
import sympy as sp
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class DerivationStep:
    """Single step in a symbolic derivation"""
    order: int
    description: str
    expression: Any  # SymPy expression
    latex: str


class SymbolicSolver:
    """Core symbolic math solver"""

    def __init__(self):
        pass

    def define_variable(self, name: str):
        """Define a symbolic variable"""
        return sp.symbols(name)

    def solve_equation(
        self,
        equation: Any,  # SymPy equation
        variable: Any,  # SymPy symbol
    ) -> Dict[str, Any]:
        """Solve symbolic equation for a variable, returns step-by-step"""
        steps: List[DerivationStep] = []
        steps.append(
            DerivationStep(
                order=1,
                description="Original equation",
                expression=equation,
                latex=sp.latex(equation),
            )
        )

        try:
            solutions = sp.solve(equation, variable)
            steps.append(
                DerivationStep(
                    order=2,
                    description="Solutions found",
                    expression=solutions,
                    latex=", ".join([sp.latex(sol) for sol in solutions]),
                )
            )
            return {
                "solutions": solutions,
                "solutions_latex": [sp.latex(sol) for sol in solutions],
                "steps": steps,
            }
        except Exception as e:
            return {"error": str(e), "steps": steps}

    def simplify(self, expression: Any) -> Dict[str, Any]:
        """Simplify an expression"""
        steps: List[DerivationStep] = [
            DerivationStep(
                1, "Original expression", expression, sp.latex(expression)
            )
        ]
        simplified = sp.simplify(expression)
        steps.append(
            DerivationStep(
                2, "Simplified", simplified, sp.latex(simplified)
            )
        )
        return {
            "original": expression,
            "simplified": simplified,
            "steps": steps,
            "original_latex": sp.latex(expression),
            "simplified_latex": sp.latex(simplified),
        }

    def expand(self, expression: Any) -> Dict[str, Any]:
        """Expand an expression"""
        expanded = sp.expand(expression)
        return {
            "original": expression,
            "expanded": expanded,
            "original_latex": sp.latex(expression),
            "expanded_latex": sp.latex(expanded),
        }

    def factor(self, expression: Any) -> Dict[str, Any]:
        """Factor an expression"""
        factored = sp.factor(expression)
        return {
            "original": expression,
            "factored": factored,
            "original_latex": sp.latex(expression),
            "factored_latex": sp.latex(factored),
        }
