import numpy as np
from advanced_simulation.schemas.engineering_report import ReportContext, EngineeringReport
from advanced_simulation.schemas.requests import MonteCarloRequest

class MonteCarloService:
    def run_analysis(self, req: MonteCarloRequest) -> EngineeringReport:
        with ReportContext(
            requirements=["Perform Monte Carlo statistical analysis to quantify yield and risk"],
            assumptions=["Parameters follow independent normal distributions", "Linear system response"],
            constraints=["N >= 1000 for statistical significance"],
            formula_selection="Vectorized Random Sampling & Statistical Aggregation",
            formula_explanation="Generates N samples from tolerance distributions and evaluates system performance using NumPy broadcasting.",
            unit_analysis="Parameters in native units, outputs in native units, probabilities dimensionless."
        ) as ctx:
            n = req.n_runs
            # Vectorized sampling
            samples = {}
            for param, base_val in req.base_params.items():
                tol = req.tolerances.get(param, 0.05) # Default 5%
                sigma = base_val * tol
                samples[param] = np.random.normal(base_val, sigma, n)
                
            # Vectorized evaluation (Example: Simple power P = V^2 / R)
            if 'voltage' in samples and 'resistance' in samples:
                power = samples['voltage']**2 / samples['resistance']
                mean_p = np.mean(power)
                std_p = np.std(power)
                yield_pct = np.sum(power < 10.0) / n * 100 # Example spec limit
                
                ctx.add_matrix_op("Vectorized Evaluation", "P = V^2 / R", {"n_samples": n})
                
                ctx.finalize(
                    final_results={"mean": mean_p, "std_dev": std_p, "yield_pct": yield_pct, "samples": n},
                    interpretation=f"Monte Carlo ({n} runs) complete. Mean Power: {mean_p:.2f}W, Yield: {yield_pct:.1f}%."
                )
            else:
                ctx.finalize(final_results={"error": "Unsupported parameter combination for vectorized eval"}, interpretation="Failed.")
        return ctx.report
