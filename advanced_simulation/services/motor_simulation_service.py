import numpy as np
from advanced_simulation.schemas.engineering_report import ReportContext, EngineeringReport
from advanced_simulation.schemas.requests import MotorRequest

class MotorSimulationService:
    def simulate_performance(self, req: MotorRequest) -> EngineeringReport:
        with ReportContext(
            requirements=["Calculate motor RPM, torque, efficiency, and thermal load"],
            assumptions=["Steady-state operation", "Linear torque-current relationship", "Constant magnetic flux"],
            constraints=["Current < Max continuous rating", "RPM < Mechanical limit"],
            formula_selection="DC/BLDC Motor Equations: V = I*R + Ke*ω, T = Kt*I",
            formula_explanation="Relates electrical inputs to mechanical outputs using motor constants derived from Kv.",
            unit_analysis="Voltage in V, Current in A, Resistance in Ohm, Speed in rad/s, Torque in Nm."
        ) as ctx:
            # Convert Kv (RPM/V) to Ke (V/(rad/s))
            ke = 60.0 / (2 * np.pi * req.kv_rpm_v)
            kt = ke # In SI units, Kt (Nm/A) = Ke (V/(rad/s))
            
            # Solve for Omega: V = I*R + Ke*Omega => Omega = (V - I*R) / Ke
            # But we know Load Torque: T_load = Kt * I => I = T_load / Kt
            i_draw = (req.load_torque_nm / kt) + req.no_load_current_a
            omega_rad_s = (req.voltage_v - i_draw * req.resistance_ohm) / ke
            rpm = omega_rad_s * 60.0 / (2 * np.pi)
            
            p_elec = req.voltage_v * i_draw
            p_mech = req.load_torque_nm * omega_rad_s
            efficiency = (p_mech / p_elec) * 100 if p_elec > 0 else 0
            p_loss = p_elec - p_mech
            
            ctx.add_intermediate("Current Draw", "I = T/Kt + I0", {"i_draw_a": i_draw})
            ctx.add_intermediate("Speed & Power", "ω = (V - IR)/Ke, P_mech = T*ω", {"rpm": rpm, "efficiency_pct": efficiency})
            
            status = "PASS" if efficiency > 70 else "MARGINAL"
            
            ctx.finalize(
                final_results={"rpm": rpm, "current_a": i_draw, "efficiency_pct": efficiency, "power_loss_w": p_loss, "status": status},
                interpretation=f"Motor operating at {rpm:.0f} RPM, drawing {i_draw:.2f}A. Efficiency: {efficiency:.1f}%. Status: {status}."
            )
        return ctx.report
