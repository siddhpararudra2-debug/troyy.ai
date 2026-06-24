"""
Uncertainty propagation engine for Engineering OS.
"""
import numpy as np
from dataclasses import dataclass


@dataclass
class UncertainValue:
    """A value with associated uncertainty."""
    value: float
    uncertainty: float
    unit: str = ""
    name: str = ""

    def __repr__(self):
        return f"{self.value} ± {self.uncertainty} {self.unit}"


class UncertaintyEngine:
    """Propagates uncertainties through engineering calculations."""

    def propagate_add(self, a: UncertainValue, b: UncertainValue) -> UncertainValue:
        """Uncertainty for addition/subtraction: σ_c = √(σ_a² + σ_b²)."""
        result = a.value + b.value
        unc = np.sqrt(a.uncertainty**2 + b.uncertainty**2)
        return UncertainValue(result, unc, a.unit, f"{a.name}_plus_{b.name}")

    def propagate_multiply(self, a: UncertainValue, b: UncertainValue) -> UncertainValue:
        """Uncertainty for multiplication: (σ_c/c)² = (σ_a/a)² + (σ_b/b)²."""
        result = a.value * b.value
        rel_unc = np.sqrt((a.uncertainty/a.value)**2 + (b.uncertainty/b.value)**2)
        return UncertainValue(result, abs(result) * rel_unc, 
                               f"{a.unit}·{b.unit}" if a.unit and b.unit else "")

    def propagate_divide(self, a: UncertainValue, b: UncertainValue) -> UncertainValue:
        """Uncertainty for division."""
        result = a.value / b.value
        rel_unc = np.sqrt((a.uncertainty/a.value)**2 + (b.uncertainty/b.value)**2)
        return UncertainValue(result, abs(result) * rel_unc,
                               f"{a.unit}/{b.unit}" if a.unit and b.unit else "")

    def propagate_power(self, a: UncertainValue, n: float) -> UncertainValue:
        """Uncertainty for power law: σ_c/c = |n| * σ_a/a."""
        result = a.value ** n
        rel_unc = abs(n) * a.uncertainty / a.value
        return UncertainValue(result, abs(result) * rel_unc, f"{a.unit}^{n}" if a.unit else "")

    def propagate_log(self, a: UncertainValue) -> UncertainValue:
        """Uncertainty for natural log: σ_c = σ_a / a."""
        result = np.log(a.value)
        unc = a.uncertainty / a.value
        return UncertainValue(result, unc)