from advanced_simulation.schemas.engineering_report import ReportContext, EngineeringReport
from advanced_simulation.schemas.requests import MissionRequest

class MissionSimulationService:
    def simulate_profile(self, req: MissionRequest) -> EngineeringReport:
        with ReportContext(
            requirements=["Simulate vehicle mission profile integrating power draw against battery capacity"],
            assumptions=["Constant power draw per phase", "Linear battery discharge", "No regeneration"],
            constraints=["Total energy < Battery capacity", "SOC >= 0 at all times"],
            formula_selection="E_phase = P_phase * t_phase, SOC_final = SOC_initial - Σ(E_phase) / E_total",
            formula_explanation="Time-stepped energy integration to determine mission feasibility and final state of charge.",
            unit_analysis="Power in W, Time in s, Energy in Wh, Mass in kg."
        ) as ctx:
            total_energy_wh = 0.0
            timeline = []
            
            for phase in req.mission_profile:
                p_w = req.cruise_power_w if phase['phase'] == 'cruise' else req.hover_power_w
                e_wh = (p_w * phase['duration_s']) / 3600.0
                total_energy_wh += e_wh
                timeline.append({"phase": phase['phase'], "energy_wh": e_wh, "cumulative_wh": total_energy_wh})
                
            soc_remaining = 1.0 - (total_energy_wh / req.battery_capacity_wh)
            
            ctx.add_intermediate("Energy Integration", "E_total = Σ(P*t)", {"total_energy_wh": total_energy_wh})
            
            status = "PASS" if soc_remaining > 0.1 else "FAIL"
            
            ctx.finalize(
                final_results={"total_energy_wh": total_energy_wh, "final_soc": soc_remaining, "timeline": timeline, "status": status},
                interpretation=f"Mission requires {total_energy_wh:.1f}Wh. Final SOC: {soc_remaining*100:.1f}%. Status: {status}."
            )
        return ctx.report
