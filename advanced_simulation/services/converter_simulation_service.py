from advanced_simulation.schemas.engineering_report import ReportContext, EngineeringReport
from advanced_simulation.schemas.requests import ConverterRequest

class ConverterSimulationService:
    def simulate_buck(self, req: ConverterRequest) -> EngineeringReport:
        with ReportContext(
            requirements=["Calculate Buck converter duty cycle, ripple, and efficiency"],
            assumptions=["Continuous Conduction Mode (CCM)", "Ideal switches (except Rds_on)", "Steady state"],
            constraints=["Duty cycle < 1.0", "Current ripple < 30% of I_out"],
            formula_selection="D = V_out/V_in, ΔI_L = (V_in - V_out)*D / (f*L)",
            formula_explanation="Determines switching parameters and passive component sizing for stable power conversion.",
            unit_analysis="Voltage in V, Current in A, Frequency in Hz, Inductance in H, Capacitance in F."
        ) as ctx:
            D = req.v_out / req.v_in
            delta_il = ((req.v_in - req.v_out) * D) / (req.switching_freq_hz * req.inductance_h)
            delta_vout = delta_il / (8 * req.switching_freq_hz * req.capacitance_f)
            
            # Simplified loss model
            i_rms = req.i_out
            rds_on = 0.05 # Assumed MOSFET resistance
            p_cond = i_rms**2 * rds_on
            p_total = p_cond + 0.5 # Switching loss estimate
            eff = (req.v_out * req.i_out) / ((req.v_out * req.i_out) + p_total) * 100
            
            ctx.add_matrix_op("Duty Cycle & Ripple", "D = Vo/Vi, ΔI = (Vi-Vo)D/(fL)", {"D": D, "delta_il": delta_il})
            ctx.add_intermediate("Efficiency", "η = P_out / (P_out + P_loss)", {"efficiency_pct": eff})
            
            status = "PASS" if eff > 85 and delta_il < (0.3 * req.i_out) else "FAIL"
            
            ctx.finalize(
                final_results={"duty_cycle": D, "inductor_ripple_a": delta_il, "output_ripple_v": delta_vout, "efficiency_pct": eff, "status": status},
                interpretation=f"Buck converter D={D:.2f}, η={eff:.1f}%. Inductor ripple: {delta_il:.2f}A. Status: {status}."
            )
        return ctx.report
