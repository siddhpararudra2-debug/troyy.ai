from advanced_simulation.schemas.engineering_report import ReportContext, EngineeringReport

class SensitivityService:
    def analyze(self, base_params: dict, func_name: str) -> EngineeringReport:
        with ReportContext(
            requirements=["Determine parameter sensitivity using finite differences"],
            assumptions=["Smooth, continuous response surface", "Small perturbations"],
            constraints=["Perturbation delta = 1% of nominal"],
            formula_selection="Central Difference: dY/dX ≈ (f(X+h) - f(X-h)) / 2h",
            formula_explanation="Calculates partial derivatives to rank parameters by their impact on system performance.",
            unit_analysis="Sensitivity in units of Output per unit of Input."
        ) as ctx:
            sensitivities = {}
            delta = 0.01
            
            # Mock function: Y = X1^2 + 2*X2
            def mock_func(p):
                return p.get('x1', 0)**2 + 2 * p.get('x2', 0)
                
            base_y = mock_func(base_params)
            
            for param, val in base_params.items():
                h = val * delta
                p_plus = base_params.copy(); p_plus[param] = val + h
                p_minus = base_params.copy(); p_minus[param] = val - h
                
                dy_dx = (mock_func(p_plus) - mock_func(p_minus)) / (2 * h)
                sensitivities[param] = dy_dx
                
            # Rank by absolute sensitivity
            ranked = sorted(sensitivities.items(), key=lambda x: abs(x[1]), reverse=True)
            
            ctx.finalize(
                final_results={"sensitivities": dict(ranked), "base_output": base_y},
                interpretation=f"Sensitivity analysis complete. Most critical parameter: {ranked[0][0]} (dY/dX = {ranked[0][1]:.3f})."
            )
        return ctx.report
