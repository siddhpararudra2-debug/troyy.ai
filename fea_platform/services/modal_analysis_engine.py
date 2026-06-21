import numpy as np
from fea_platform.schemas.fea_models import FEAResult

class ModalAnalysisEngine:
    """Computes natural frequencies and mode shapes."""
    
    def compute_natural_frequencies(self, mass_matrix: np.ndarray,
                                    stiffness_matrix: np.ndarray,
                                    n_modes: int = 10) -> list:
        """Solve generalized eigenvalue problem K*phi = omega^2 * M*phi."""
        try:
            eigenvalues, _ = np.linalg.eig(np.linalg.inv(mass_matrix) @ stiffness_matrix)
            # Filter real positive eigenvalues
            frequencies = []
            for val in eigenvalues:
                real_val = val.real
                if real_val > 0:
                    omega = np.sqrt(real_val)
                    freq_hz = omega / (2.0 * np.pi)
                    frequencies.append(float(freq_hz))
            frequencies.sort()
            return frequencies[:n_modes]
        except np.linalg.LinAlgError:
            return []
