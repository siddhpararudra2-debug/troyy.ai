"""
Uncertainty Engine — propagates measurement uncertainty through calculations.
Uses both analytical (first-order Taylor) and Monte Carlo methods.
"""
import numpy as np
from typing import Dict, List, Tuple, Callable
from physics_engine.schemas.physics_models import PhysicalQuantity

class UncertaintyEngine:
    """Propagates uncertainty through engineering calculations."""
    
    def __init__(self, n_monte_carlo: int = 10000, seed: int = 42):
        self.n_mc = n_monte_carlo
        self.rng = np.random.default_rng(seed)
        
    def analytical_propagation(self, func: Callable, inputs: Dict[str, PhysicalQuantity]) -> Tuple[float, float]:
        """
        First-order Taylor expansion uncertainty propagation.
        σ_y² = Σ (∂f/∂x_i)² σ_i²
        Returns: (nominal_value, uncertainty)
        """
        # Compute nominal value
        nominal_inputs = {k: v.value for k, v in inputs.items()}
        y_nominal = func(**nominal_inputs)
        
        # Compute partial derivatives numerically
        variance = 0.0
        for name, qty in inputs.items():
            if qty.uncertainty is None or qty.uncertainty == 0:
                continue
                
            # Central difference for partial derivative
            h = max(abs(qty.value) * 1e-6, 1e-10)
            inputs_plus = nominal_inputs.copy()
            inputs_plus[name] = qty.value + h
            inputs_minus = nominal_inputs.copy()
            inputs_minus[name] = qty.value - h
            
            partial = (func(**inputs_plus) - func(**inputs_minus)) / (2 * h)
            variance += (partial * qty.uncertainty) ** 2
            
        y_uncertainty = np.sqrt(variance)
        return y_nominal, y_uncertainty
        
    def monte_carlo_propagation(self, func: Callable, inputs: Dict[str, PhysicalQuantity],
                                distribution: str = "normal") -> Dict:
        """
        Monte Carlo uncertainty propagation.
        Samples inputs from their distributions, evaluates function, returns statistics.
        """
        samples = {name: [] for name in inputs}
        results = []
        
        for _ in range(self.n_mc):
            sample_inputs = {}
            for name, qty in inputs.items():
                if qty.uncertainty is None or qty.uncertainty == 0:
                    sample_inputs[name] = qty.value
                else:
                    if distribution == "normal":
                        sample = self.rng.normal(qty.value, qty.uncertainty)
                    elif distribution == "uniform":
                        # ±3σ covers 99.7% for normal, use as uniform bounds
                        sample = self.rng.uniform(
                            qty.value - 3 * qty.uncertainty,
                            qty.value + 3 * qty.uncertainty
                        )
                    else:
                        sample = qty.value
                    sample_inputs[name] = sample
                samples[name].append(sample_inputs[name])
                
            try:
                results.append(func(**sample_inputs))
            except Exception:
                continue
                
        results = np.array(results)
        
        return {
            "nominal": float(np.mean(results)),
            "mean": float(np.mean(results)),
            "std": float(np.std(results)),
            "median": float(np.median(results)),
            "p05": float(np.percentile(results, 5)),
            "p50": float(np.percentile(results, 50)),
            "p95": float(np.percentile(results, 95)),
            "min": float(np.min(results)),
            "max": float(np.max(results)),
            "n_samples": len(results),
            "input_samples": {k: np.array(v).tolist() for k, v in samples.items()},
            "output_samples": results.tolist()
        }
        
    def sensitivity_analysis(self, func: Callable, inputs: Dict[str, PhysicalQuantity]) -> Dict[str, float]:
        """
        Compute Sobol-like sensitivity indices.
        Returns: {input_name: sensitivity_index}
        Higher index = more influential input.
        """
        # Variance-based sensitivity
        mc_result = self.monte_carlo_propagation(func, inputs)
        total_variance = mc_result["std"] ** 2
        
        if total_variance < 1e-20:
            return {name: 0.0 for name in inputs}
            
        sensitivities = {}
        for name, qty in inputs.items():
            if qty.uncertainty is None or qty.uncertainty == 0:
                sensitivities[name] = 0.0
                continue
                
            # Zero out this input's uncertainty
            reduced_inputs = inputs.copy()
            reduced_inputs[name] = PhysicalQuantity(
                value=qty.value, unit=qty.unit, uncertainty=0.0
            )
            reduced_result = self.monte_carlo_propagation(func, reduced_inputs)
            reduced_variance = reduced_result["std"] ** 2
            
            # First-order sensitivity: fraction of variance due to this input
            sensitivities[name] = (total_variance - reduced_variance) / total_variance
            
        return sensitivities
        
    def compute_margin_with_uncertainty(self, capacity: PhysicalQuantity,
                                        demand: PhysicalQuantity,
                                        required_margin: float = 0.2) -> Dict:
        """
        Compute probability that margin requirement is met given uncertainties.
        margin = (capacity - demand) / demand
        """
        def margin_func(cap, dem):
            return (cap - dem) / dem if dem > 0 else float('inf')
            
        inputs = {
            'capacity': capacity,
            'demand': demand
        }
        
        mc = self.monte_carlo_propagation(margin_func, inputs)
        
        # Probability of meeting margin requirement
        margins = np.array(mc["output_samples"])
        prob_meeting = float(np.mean(margins >= required_margin))
        
        return {
            "nominal_margin": margin_func(capacity.value, demand.value),
            "mean_margin": mc["mean"],
            "std_margin": mc["std"],
            "probability_of_meeting_requirement": prob_meeting,
            "required_margin": required_margin,
            "percentile_5": mc["p05"],
            "percentile_95": mc["p95"]
        }
