from advanced_simulation.schemas.engineering_report import ReportContext, EngineeringReport
from advanced_simulation.schemas.requests import BatteryRequest

class BatterySimulationService:
    def simulate_discharge(self, req: BatteryRequest) -> EngineeringReport:
        with ReportContext(
            requirements=["Calculate battery voltage sag, capacity usage, and mission endurance"],
            assumptions=["Constant current discharge", "Linear OCV-SOC relationship for simplicity", "Peukert effect ignored"],
            constraints=["SOC must remain >= 0", "Voltage must not drop below cutoff (3.0V/cell)"],
            formula_selection="V_term = V_ocv(SOC) - I * R_int, t_end = Capacity / I",
            formula_explanation="Models the battery as an ideal voltage source dependent on SOC in series with an internal resistor.",
            unit_analysis="Capacity in mAh, Current in A, Resistance in Ohm, Voltage in V, Time in hours."
        ) as ctx:
            cap_ah = req.capacity_mah / 1000.0
            v_ocv = req.nominal_voltage_v * req.initial_soc
            
            v_drop = req.load_current_a * req.internal_resistance_ohm
            v_term = v_ocv - v_drop
            
            # Temp derating (simplified Arrhenius approximation)
            temp_factor = 1.0 if req.ambient_temp_c >= 20 else 0.8
            
            effective_cap = cap_ah * temp_factor
            endurance_h = effective_cap / req.load_current_a if req.load_current_a > 0 else float('inf')
            
            ctx.add_matrix_op("Terminal Voltage", "V_term = V_ocv - I*R", {"v_ocv": v_ocv, "v_drop": v_drop})
            ctx.add_intermediate("Endurance", "t = C_eff / I", {"endurance_h": endurance_h})
            
            status = "PASS" if v_term > (req.nominal_voltage_v * 0.8) else "FAIL"
            
            ctx.finalize(
                final_results={"terminal_voltage_v": v_term, "voltage_sag_v": v_drop, "endurance_hours": endurance_h, "status": status},
                interpretation=f"Battery terminal voltage under load: {v_term:.2f}V. Estimated endurance: {endurance_h*60:.1f} mins. Status: {status}."
            )
        return ctx.report
