import numpy as np
from fea_platform.schemas.fea_models import FEAResult

class BucklingEngine:
    """Computes buckling load factors via eigenvalue analysis."""
    
    def compute_buckling_load_factor(self, stiffness_matrix: np.ndarray,
                                     geometric_stiffness: np.ndarray,
                                     n_modes: int = 5) -> list:
        """Solve (K + lambda * Kg) * phi = 0 for eigenvalues lambda."""
        try:
            eigenvalues, _ = np.linalg.eig(np.linalg.inv(stiffness_matrix) @ (-geometric_stiffness))
            eigenvalues = sorted([e.real for e in eigenvalues if e.real > 0])
            return eigenvalues[:n_modes]
        except np.linalg.LinAlgError:
            return []
            
    def euler_buckling_load(self, E: float, I: float, L: float, k: float = 1.0) -> float:
        """Euler critical load for column: P_cr = pi^2 * E * I / (k*L)^2"""
        return (np.pi ** 2 * E * I) / ((k * L) ** 2)
