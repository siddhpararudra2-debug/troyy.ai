"""
Numerical solver for Engineering OS.
Provides numerical methods for root finding, integration, and ODE solving.
"""
import logging
import numpy as np
from typing import Optional, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class NumericalResult:
    """Result of a numerical computation with steps."""
    result: float
    steps: list[dict]
    iterations: int
    error_estimate: Optional[float] = None
    converged: bool = True


class NumericalSolver:
    """
    Numerical methods for engineering calculations.
    Provides root finding, numerical integration, and ODE solving.
    """

    def __init__(self, tolerance: float = 1e-10, max_iterations: int = 1000):
        self.tolerance = tolerance
        self.max_iterations = max_iterations

    def bisection(
        self, f: Callable[[float], float], a: float, b: float
    ) -> NumericalResult:
        """Bisection method for root finding."""
        steps = []
        fa, fb = f(a), f(b)
        
        if fa * fb > 0:
            raise ValueError(f"f(a)={fa} and f(b)={fb} have same sign")
        
        steps.append({
            "iteration": 0,
            "a": a, "b": b,
            "fa": fa, "fb": fb,
            "description": f"Initial interval [{a}, {b}]",
        })
        
        for i in range(self.max_iterations):
            c = (a + b) / 2
            fc = f(c)
            
            steps.append({
                "iteration": i + 1,
                "a": a, "b": b, "c": c,
                "fa": fa, "fb": fb, "fc": fc,
                "error": abs(b - a) / 2,
            })
            
            if abs(fc) < self.tolerance or (b - a) / 2 < self.tolerance:
                return NumericalResult(
                    result=c,
                    steps=steps,
                    iterations=i + 1,
                    error_estimate=(b - a) / 2,
                    converged=True,
                )
            
            if fa * fc < 0:
                b, fb = c, fc
            else:
                a, fa = c, fc
        
        c = (a + b) / 2
        return NumericalResult(
            result=c,
            steps=steps,
            iterations=self.max_iterations,
            error_estimate=(b - a) / 2,
            converged=False,
        )

    def newton_raphson(
        self, f: Callable[[float], float], df: Callable[[float], float],
        x0: float
    ) -> NumericalResult:
        """Newton-Raphson method for root finding."""
        steps = []
        x = x0
        
        steps.append({
            "iteration": 0,
            "x": x,
            "f(x)": f(x),
            "description": f"Initial guess x₀ = {x}",
        })
        
        for i in range(self.max_iterations):
            fx = f(x)
            dfx = df(x)
            
            if abs(dfx) < 1e-15:
                raise ValueError(f"Derivative near zero at x={x}")
            
            x_new = x - fx / dfx
            
            steps.append({
                "iteration": i + 1,
                "x": x_new,
                "f(x)": f(x_new),
                "step": fx / dfx,
            })
            
            if abs(x_new - x) < self.tolerance:
                return NumericalResult(
                    result=x_new,
                    steps=steps,
                    iterations=i + 1,
                    error_estimate=abs(x_new - x),
                    converged=True,
                )
            
            x = x_new
        
        return NumericalResult(
            result=x,
            steps=steps,
            iterations=self.max_iterations,
            converged=False,
        )

    def simpson_integrate(
        self, f: Callable[[float], float], a: float, b: float, n: int = 100
    ) -> NumericalResult:
        """Numerical integration using Simpson's rule."""
        if n % 2 == 1:
            n += 1  # n must be even
        
        h = (b - a) / n
        x = np.linspace(a, b, n + 1)
        y = np.array([f(xi) for xi in x])
        
        steps = [
            {
                "description": f"Simpson's rule with n={n} subintervals",
                "h": h,
                "interval": f"[{a}, {b}]",
            }
        ]
        
        # Simpson's rule: (h/3) * [f0 + fn + 4*(f1+f3+...) + 2*(f2+f4+...)]
        integral = (h / 3) * (
            y[0] + y[-1] +
            4 * np.sum(y[1:-1:2]) +
            2 * np.sum(y[2:-2:2])
        )
        
        result = NumericalResult(
            result=float(integral),
            steps=steps,
            iterations=n,
        )
        
        return result

    def euler_ode(
        self, f: Callable[[float, float], float],
        t0: float, y0: float, h: float, n_steps: int
    ) -> list[dict]:
        """Forward Euler method for ODE solving."""
        results = [{"t": t0, "y": y0}]
        t, y = t0, y0
        
        for i in range(n_steps):
            y = y + h * f(t, y)
            t = t + h
            results.append({"t": t, "y": y, "step": i + 1})
        
        return results

    def rk4_ode(
        self, f: Callable[[float, float], float],
        t0: float, y0: float, h: float, n_steps: int
    ) -> list[dict]:
        """Runge-Kutta 4th order method for ODE solving."""
        results = [{"t": t0, "y": y0}]
        t, y = t0, y0
        
        for i in range(n_steps):
            k1 = h * f(t, y)
            k2 = h * f(t + h/2, y + k1/2)
            k3 = h * f(t + h/2, y + k2/2)
            k4 = h * f(t + h, y + k3)
            
            y = y + (k1 + 2*k2 + 2*k3 + k4) / 6
            t = t + h
            
            results.append({
                "t": t, "y": y, "step": i + 1,
                "k1": k1, "k2": k2, "k3": k3, "k4": k4,
            })
        
        return results