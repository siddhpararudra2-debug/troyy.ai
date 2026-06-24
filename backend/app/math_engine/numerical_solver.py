"""
Numerical Solver — numerical methods for engineering
Bisection, Newton-Raphson, Simpson's rule, Euler/RK4
"""
from typing import Callable, List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class NumericalResult:
    value: float
    iterations: int
    tolerance: float
    converged: bool
    history: List[float]


class NumericalSolver:
    """Numerical methods solver"""

    def bisection(
        self,
        func: Callable[[float], float],
        a: float,
        b: float,
        tol: float = 1e-6,
        max_iter: int = 100,
    ) -> NumericalResult:
        """Bisection method root finding"""
        history = []
        for i in range(max_iter):
            c = (a + b) / 2
            history.append(c)
            fc = func(c)

            if abs(fc) < tol or (b - a) / 2 < tol:
                return NumericalResult(
                    value=c,
                    iterations=i + 1,
                    tolerance=tol,
                    converged=True,
                    history=history,
                )

            if func(a) * fc < 0:
                b = c
            else:
                a = c

        return NumericalResult(
            value=(a + b) / 2,
            iterations=max_iter,
            tolerance=tol,
            converged=False,
            history=history,
        )

    def newton_raphson(
        self,
        func: Callable[[float], float],
        deriv: Callable[[float], float],
        x0: float,
        tol: float = 1e-6,
        max_iter: int = 100,
    ) -> NumericalResult:
        """Newton-Raphson root finding"""
        x = x0
        history = [x]

        for i in range(max_iter):
            fx = func(x)
            dfx = deriv(x)

            if abs(dfx) < 1e-12:
                return NumericalResult(
                    value=x,
                    iterations=i + 1,
                    tolerance=tol,
                    converged=False,
                    history=history,
                )

            x_new = x - fx / dfx
            history.append(x_new)

            if abs(x_new - x) < tol:
                return NumericalResult(
                    value=x_new,
                    iterations=i + 1,
                    tolerance=tol,
                    converged=True,
                    history=history,
                )
            x = x_new

        return NumericalResult(
            value=x,
            iterations=max_iter,
            tolerance=tol,
            converged=False,
            history=history,
        )

    def simpsons_rule(
        self,
        func: Callable[[float], float],
        a: float,
        b: float,
        n: int = 100,
    ) -> Dict[str, Any]:
        """Simpson's rule numerical integration"""
        if n % 2 != 0:
            n += 1
        h = (b - a) / n
        x = np.linspace(a, b, n + 1)
        y = func(x)

        integral = h / 3 * (y[0] + 2 * sum(y[2:-1:2]) + 4 * sum(y[1:-1:2]) + y[-1])

        return {"integral": float(integral), "n": n, "h": h}

    def euler_method(
        self,
        deriv: Callable[[float, float], float],
        y0: float,
        t0: float,
        tf: float,
        dt: float,
    ) -> Dict[str, Any]:
        """Euler method for ODE solving"""
        t_values = [t0]
        y_values = [y0]
        t = t0
        y = y0
        while t < tf:
            y = y + dt * deriv(t, y)
            t = t + dt
            y_values.append(y)
            t_values.append(t)
        return {"t": t_values, "y": y_values, "dt": dt}

    def rk4_method(
        self,
        deriv: Callable[[float, float], float],
        y0: float,
        t0: float,
        tf: float,
        dt: float,
    ) -> Dict[str, Any]:
        """Runge-Kutta 4th order for ODE solving"""
        t_values = [t0]
        y_values = [y0]
        t = t0
        y = y0
        while t < tf:
            k1 = dt * deriv(t, y)
            k2 = dt * deriv(t + dt/2, y + k1/2)
            k3 = dt * deriv(t + dt/2, y + k2/2)
            k4 = dt * deriv(t + dt, y + k3)
            y = y + (k1 + 2*k2 + 2*k3 + k4) / 6
            t = t + dt
            y_values.append(y)
            t_values.append(t)
        return {"t": t_values, "y": y_values, "dt": dt}
