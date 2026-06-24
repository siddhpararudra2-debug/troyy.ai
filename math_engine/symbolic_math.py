"""
Symbolic mathematics engine for Engineering OS.
Provides symbolic algebra, calculus, and equation manipulation using SymPy.
"""
import logging
from typing import Optional
from sympy import (
    symbols, solve, diff, integrate, limit, series, expand, factor,
    simplify, collect, apart, together, trigsimp, expand_trig,
    Piecewise, Eq, Symbol, Function, Derivative, Integral, oo,
    pretty, latex, init_printing, parse_expr, sympify,
    solveset, nonlinsolve, linear_eq_to_matrix, linsolve,
    dsolve, classify_ode, checkodesol,
    Matrix, eye, zeros, ones, diag, transpose, det, trace,
    sqrt, Abs, re, im,
)

logger = logging.getLogger(__name__)
init_printing(use_unicode=True)


class Step:
    """A single step in a symbolic derivation."""
    def __init__(self, description: str, expression: str, latex_expr: str):
        self.description = description
        self.expression = expression
        self.latex = latex_expr

    def to_dict(self) -> dict:
        return {
            "description": self.description,
            "expression": self.expression,
            "latex": self.latex,
        }


class DerivationResult:
    """Result of a symbolic derivation with step-by-step breakdown."""
    def __init__(self, result: str, steps: list[Step], latex_result: str = ""):
        self.result = result
        self.steps = steps
        self.latex_result = latex_result or result

    def to_dict(self) -> dict:
        return {
            "result": self.result,
            "latex_result": self.latex_result,
            "steps": [s.to_dict() for s in self.steps],
        }


class SymbolicMathEngine:
    """
    Symbolic mathematics engine using SymPy.
    Provides step-by-step derivations, algebra, calculus, and more.
    """

    @staticmethod
    def parse_expression(expr_str: str) -> tuple:
        """Parse a string into a SymPy expression."""
        try:
            return sympify(expr_str)
        except Exception as e:
            logger.error(f"Failed to parse '{expr_str}': {e}")
            raise ValueError(f"Cannot parse expression: {expr_str}")

    @staticmethod
    def parse_equation(eq_str: str) -> Eq:
        """Parse a string like 'x + 1 = 2' into a SymPy Eq."""
        if "=" in eq_str:
            left_str, right_str = eq_str.split("=", 1)
            left = SymbolicMathEngine.parse_expression(left_str.strip())
            right = SymbolicMathEngine.parse_expression(right_str.strip())
            return Eq(left, right)
        # No equals sign, treat as expression = 0
        expr = SymbolicMathEngine.parse_expression(eq_str)
        return Eq(expr, 0)

    def simplify_expression(self, expr_str: str) -> DerivationResult:
        """Simplify an algebraic expression with steps."""
        expr = self.parse_expression(expr_str)
        steps = []
        steps.append(Step(
            "Original expression",
            str(expr),
            latex(expr),
        ))
        
        # Try successive simplifications
        simplified = simplify(expr)
        if str(simplified) != str(expr):
            steps.append(Step(
                "After simplification",
                str(simplified),
                latex(simplified),
            ))
        
        expanded = expand(simplified)
        if str(expanded) != str(simplified):
            steps.append(Step(
                "After expansion",
                str(expanded),
                latex(expanded),
            ))
        
        factored = factor(expanded)
        if str(factored) != str(expanded) and str(factored) != str(simplified):
            steps.append(Step(
                "After factoring",
                str(factored),
                latex(factored),
            ))
        
        final = factored if str(factored) != str(expanded) else expanded
        return DerivationResult(
            result=str(final),
            steps=steps,
            latex_result=latex(final),
        )

    def expand_expression(self, expr_str: str) -> DerivationResult:
        """Expand an algebraic expression."""
        expr = self.parse_expression(expr_str)
        steps = [
            Step("Original expression", str(expr), latex(expr)),
        ]
        result = expand(expr)
        steps.append(Step("After expansion", str(result), latex(result)))
        return DerivationResult(
            result=str(result),
            steps=steps,
            latex_result=latex(result),
        )

    def factor_expression(self, expr_str: str) -> DerivationResult:
        """Factor an algebraic expression."""
        expr = self.parse_expression(expr_str)
        steps = [
            Step("Original expression", str(expr), latex(expr)),
        ]
        result = factor(expr)
        steps.append(Step("After factoring", str(result), latex(result)))
        return DerivationResult(
            result=str(result),
            steps=steps,
            latex_result=latex(result),
        )

    def differentiate(self, expr_str: str, var: str = "x", 
                      order: int = 1) -> DerivationResult:
        """Compute symbolic derivative with steps."""
        expr = self.parse_expression(expr_str)
        x = symbols(var)
        steps = [
            Step(f"Original function f({var})", str(expr), latex(expr)),
        ]
        
        current = expr
        for i in range(order):
            deriv = diff(current, x)
            order_str = "st" if i == 0 else "nd" if i == 1 else "rd" if i == 2 else "th"
            steps.append(Step(
                f"{i+1}{order_str} derivative",
                str(deriv),
                latex(deriv),
            ))
            current = deriv
        
        final = current
        simplified = simplify(final)
        if str(simplified) != str(final):
            steps.append(Step(
                "Simplified result",
                str(simplified),
                latex(simplified),
            ))
            final = simplified
        
        return DerivationResult(
            result=str(final),
            steps=steps,
            latex_result=latex(final),
        )

    def integrate(self, expr_str: str, var: str = "x",
                  bounds: Optional[tuple] = None) -> DerivationResult:
        """Compute symbolic integral with steps."""
        expr = self.parse_expression(expr_str)
        x = symbols(var)
        steps = [
            Step("Integrand", str(expr), latex(expr)),
        ]
        
        if bounds:
            a, b = bounds
            a_expr = self.parse_expression(str(a)) if isinstance(a, str) else a
            b_expr = self.parse_expression(str(b)) if isinstance(b, str) else b
            integral = integrate(expr, (x, a_expr, b_expr))
            steps.append(Step(
                f"Definite integral from {a} to {b}",
                str(integral),
                latex(integral),
            ))
        else:
            integral = integrate(expr, x)
            steps.append(Step(
                "Indefinite integral (+ C)",
                str(integral),
                latex(integral),
            ))
        
        simplified = simplify(integral)
        if str(simplified) != str(integral):
            steps.append(Step(
                "Simplified result",
                str(simplified),
                latex(simplified),
            ))
            integral = simplified
        
        return DerivationResult(
            result=str(integral),
            steps=steps,
            latex_result=latex(integral),
        )

    def limit_calc(self, expr_str: str, var: str = "x",
                   approach: str = "0") -> DerivationResult:
        """Compute limit of an expression."""
        expr = self.parse_expression(expr_str)
        x = symbols(var)
        a = self.parse_expression(approach)
        steps = [
            Step(f"Original expression as {var}→{approach}",
                 str(expr), latex(expr)),
        ]
        
        result = limit(expr, x, a)
        steps.append(Step(
            "Limit result",
            str(result),
            latex(result),
        ))
        
        return DerivationResult(
            result=str(result),
            steps=steps,
            latex_result=latex(result),
        )

    def series_expand(self, expr_str: str, var: str = "x",
                      point: str = "0", order: int = 5) -> DerivationResult:
        """Compute series expansion."""
        expr = self.parse_expression(expr_str)
        x = symbols(var)
        pt = self.parse_expression(point)
        steps = [
            Step(f"Original function around {var}={point}",
                 str(expr), latex(expr)),
        ]
        
        result = series(expr, x, pt, order).removeO()
        steps.append(Step(
            f"Series expansion up to order {order}",
            str(result),
            latex(result),
        ))
        
        return DerivationResult(
            result=str(result),
            steps=steps,
            latex_result=latex(result),
        )

    def partial_fractions(self, expr_str: str, var: str = "x") -> DerivationResult:
        """Compute partial fraction decomposition."""
        expr = self.parse_expression(expr_str)
        x = symbols(var)
        steps = [
            Step("Original rational expression", str(expr), latex(expr)),
        ]
        
        result = apart(expr, x)
        steps.append(Step(
            "Partial fractions decomposition",
            str(result),
            latex(result),
        ))
        
        return DerivationResult(
            result=str(result),
            steps=steps,
            latex_result=latex(result),
        )