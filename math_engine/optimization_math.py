"""
Optimization engine for Engineering OS.
Provides gradient-based and gradient-free optimization methods.
"""
import logging
import numpy as np
from typing import Optional, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Result of an optimization run."""
    optimal_value: float
    optimal_point: list[float]
    iterations: int
    converged: bool
    objective_history: list[float]
    constraint_violations: Optional[list[float]] = None


class OptimizationEngine:
    """
    Mathematical optimization for engineering problems.
    Supports gradient descent, constrained optimization, and more.
    """

    def __init__(self, tolerance: float = 1e-8, max_iterations: int = 1000):
        self.tolerance = tolerance
        self.max_iterations = max_iterations

    def gradient_descent(
        self,
        f: Callable[[np.ndarray], float],
        grad_f: Callable[[np.ndarray], np.ndarray],
        x0: np.ndarray,
        learning_rate: float = 0.01,
        momentum: float = 0.0,
    ) -> OptimizationResult:
        """Gradient descent optimization."""
        x = np.array(x0, dtype=float)
        v = np.zeros_like(x)
        history = [float(f(x))]
        
        for i in range(self.max_iterations):
            g = grad_f(x)
            
            # Gradient descent with momentum
            v = momentum * v + (1 - momentum) * g
            x_new = x - learning_rate * v
            
            fx = f(x_new)
            history.append(float(fx))
            
            if np.linalg.norm(x_new - x) < self.tolerance:
                return OptimizationResult(
                    optimal_value=float(fx),
                    optimal_point=x_new.tolist(),
                    iterations=i + 1,
                    converged=True,
                    objective_history=history,
                )
            
            x = x_new
        
        return OptimizationResult(
            optimal_value=float(f(x)),
            optimal_point=x.tolist(),
            iterations=self.max_iterations,
            converged=False,
            objective_history=history,
        )

    def golden_section_search(
        self, f: Callable[[float], float], a: float, b: float
    ) -> OptimizationResult:
        """Golden section search for 1D unimodal minimization."""
        phi = (np.sqrt(5) - 1) / 2  # Golden ratio
        history = []
        
        c = b - phi * (b - a)
        d = a + phi * (b - a)
        fc, fd = f(c), f(d)
        
        for i in range(self.max_iterations):
            if fc < fd:
                b, d, fd = d, c, fc
                c = b - phi * (b - a)
                fc = f(c)
            else:
                a, c, fc = c, d, fd
                d = a + phi * (b - a)
                fd = f(d)
            
            history.append(float(f((a + b) / 2)))
            
            if abs(b - a) < self.tolerance:
                x_opt = (a + b) / 2
                return OptimizationResult(
                    optimal_value=float(f(x_opt)),
                    optimal_point=[x_opt],
                    iterations=i + 1,
                    converged=True,
                    objective_history=history,
                )
        
        x_opt = (a + b) / 2
        return OptimizationResult(
            optimal_value=float(f(x_opt)),
            optimal_point=[x_opt],
            iterations=self.max_iterations,
            converged=False,
            objective_history=history,
        )

    def quadratic_programming(
        self, Q: np.ndarray, c: np.ndarray,
        A: Optional[np.ndarray] = None, b: Optional[np.ndarray] = None
    ) -> OptimizationResult:
        """Solve quadratic program: minimize 0.5*x^T*Q*x + c^T*x subject to A*x <= b."""
        from scipy.optimize import minimize
        
        def objective(x):
            return 0.5 * x.T @ Q @ x + c.T @ x
        
        def constraint_func(x):
            if A is not None:
                return b - A @ x
            return np.array([])
        
        x0 = np.zeros(len(c))
        
        constraints = []
        if A is not None and b is not None:
            for i in range(len(b)):
                constraints.append({
                    'type': 'ineq',
                    'fun': lambda x, i=i: b[i] - A[i] @ x
                })
        
        result = minimize(
            objective, x0, method='SLSQP',
            constraints=constraints,
            options={'maxiter': self.max_iterations, 'ftol': self.tolerance}
        )
        
        return OptimizationResult(
            optimal_value=float(result.fun),
            optimal_point=result.x.tolist(),
            iterations=result.nit,
            converged=result.success,
            objective_history=[float(result.fun)],
        )

    def least_squares(
        self,
        residuals: Callable[[np.ndarray], np.ndarray],
        jacobian: Optional[Callable[[np.ndarray], np.ndarray]],
        x0: np.ndarray,
    ) -> OptimizationResult:
        """Non-linear least squares optimization."""
        from scipy.optimize import least_squares
        
        result = least_squares(
            residuals, x0, jac=jacobian,
            ftol=self.tolerance, max_nfev=self.max_iterations,
        )
        
        return OptimizationResult(
            optimal_value=float(result.cost),
            optimal_point=result.x.tolist(),
            iterations=result.nfev,
            converged=result.success,
            objective_history=[float(result.cost)],
        )