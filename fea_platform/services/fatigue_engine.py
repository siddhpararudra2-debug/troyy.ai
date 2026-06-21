import numpy as np
from fea_platform.schemas.fea_models import FEAResult

class FatigueEngine:
    """Computes fatigue life using S-N curve (Basquin) approach."""
    
    def __init__(self, fatigue_strength_coefficient: float = 1000e6,
                 fatigue_strength_exponent: float = -0.1):
        self.sigma_f = fatigue_strength_coefficient  # MPa
        self.b = fatigue_strength_exponent
        
    def compute_life(self, stress_amplitude_pa: float, mean_stress_pa: float = 0.0) -> float:
        """Compute cycles to failure using Basquin equation with Goodman correction."""
        # Convert to MPa
        stress_amp_mpa = stress_amplitude_pa / 1e6
        mean_mpa = mean_stress_pa / 1e6
        
        # Goodman mean stress correction
        ultimate_tensile = abs(self.sigma_f * 2.0)  # Approximate
        if ultimate_tensile - mean_mpa <= 0:
            return 0.0  # Static failure
            
        effective_stress = stress_amp_mpa / (1.0 - mean_mpa / ultimate_tensile)
        
        if effective_stress <= 0:
            return float('inf')
            
        # Basquin: sigma_a = sigma_f' * (2Nf)^b
        # => Nf = 0.5 * (sigma_f' / sigma_a)^(1/b)
        try:
            nf = 0.5 * (abs(self.sigma_f) / effective_stress) ** (1.0 / self.b)
            return float(nf)
        except (OverflowError, ZeroDivisionError):
            return float('inf')
            
    def analyze(self, fea_result: FEAResult) -> FEAResult:
        """Add fatigue life to FEA result."""
        if fea_result.max_von_mises_pa > 0:
            life = self.compute_life(fea_result.max_von_mises_pa / 2.0)  # Fully reversed
            fea_result.fatigue_life_cycles = life
        return fea_result
