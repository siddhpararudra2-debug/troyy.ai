"""
Calculus Engine — derivatives, integrals, limits, series
"""
import sympy as sp
from typing import Any, Dict, List


class CalculusEngine:
    """Calculus operations engine"""

    def derivative(self, expr: Any, var: Any, order: int = 1) -> Dict[str, Any]:
        """Compute derivative"""
        deriv = sp.diff(expr, var, order)
        return {
            "original": expr,
            "derivative": deriv,
            "order": order,
            "original_latex": sp.latex(expr),
            "derivative_latex": sp.latex(deriv),
        }

    def integral(
        self,
        expr: Any,
        var: Any,
        lower: Any = None,
        upper: Any = None,
    ) -> Dict[str, Any]:
        """Compute indefinite or definite integral"""
        if lower is not None and upper is not None:
            integ = sp.integrate(expr, (var, lower, upper))
            return {
                "type": "definite",
                "limits": (lower, upper),
                "original": expr,
                "result": integ,
                "original_latex": sp.latex(expr),
                "result_latex": sp.latex(integ),
            }
        else:
            integ = sp.integrate(expr, var)
            return {
                "type": "indefinite",
                "original": expr,
                "antiderivative": integ,
                "original_latex": sp.latex(expr),
                "antiderivative_latex": sp.latex(integ),
            }

    def limit(
        self,
        expr: Any,
        var: Any,
        point: Any,
        side: str = "",
    ) -> Dict[str, Any]:
        """Compute limit"""
        lim = sp.limit(expr, var, point, side) if side else sp.limit(expr, var, point)
        return {
            "original": expr,
            "limit_point": point,
            "side": side,
            "result": lim,
            "original_latex": sp.latex(expr),
            "result_latex": sp.latex(lim),
        }

    def taylor_series(
        self,
        expr: Any,
        var: Any,
        point: Any,
        order: int,
    ) -> Dict[str, Any]:
        """Compute Taylor series expansion"""
        series = sp.series(expr, var, point, order).removeO()
        return {
            "original": expr,
            "point": point,
            "order": order,
            "series": series,
            "original_latex": sp.latex(expr),
            "series_latex": sp.latex(series),
        }
