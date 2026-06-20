import numpy as np
from advanced_simulation.schemas.engineering_report import ReportContext, EngineeringReport

class ReliabilityPredictionService:
    def predict_life(self, stress_factor: float, temp_c: float) -> EngineeringReport:
        with ReportContext(
            requirements=["Predict component remaining useful life (RUL) using physics-of-failure models"],
            assumptions=["Arrhenius model for temperature", "Inverse Power Law for stress"],
            constraints=["Activation energy Ea = 0.7 eV (typical for electronics)"],
            formula_selection="Arrhenius: AF = exp((Ea/k)*(1/T_use - 1/T_test)), Weibull R(t) = exp(-(t/eta)^beta)",
            formula_explanation="Calculates acceleration factors to map test life to operational life under specific environmental stresses.",
            unit_analysis="Temperature in Kelvin, Energy in eV, Time in hours, Reliability dimensionless (0-1)."
        ) as ctx:
            k_b = 8.617e-5 # eV/K
            ea = 0.7
            t_use = temp_c + 273.15
            t_test = 85.0 + 273.15 # 85C test standard
            
            af = np.exp((ea / k_b) * (1/t_use - 1/t_test))
            base_life_h = 10000 # Base test life
            operational_life_h = base_life_h * af
            
            # Weibull R(t) at 1 year (8760h)
            beta = 2.5 # Shape parameter
            eta = operational_life_h
            r_1yr = np.exp(- (8760 / eta)**beta)
            
            ctx.add_intermediate("Acceleration Factor", "AF = exp((Ea/k)*(1/Tu - 1/Tt))", {"af": af})
            ctx.add_intermediate("1-Year Reliability", "R(t) = exp(-(t/eta)^beta)", {"r_1yr": r_1yr})
            
            status = "PASS" if r_1yr > 0.95 else "FAIL"
            
            ctx.finalize(
                final_results={"operational_life_h": operational_life_h, "reliability_1yr": r_1yr, "status": status},
                interpretation=f"Predicted 1-year reliability: {r_1yr*100:.1f}%. Expected life: {operational_life_h:.0f}h. Status: {status}."
            )
        return ctx.report
