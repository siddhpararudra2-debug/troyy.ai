from app.schematic_engine.schemas.engineering_report import ReportContext, EngineeringReport
from app.schematic_engine.schemas.schematic_models import PowerTree, PowerRail

class PowerTreeService:
    def generate_tree(self, input_voltage: float, power_rails: dict) -> EngineeringReport:
        with ReportContext(
            requirements=["Generate power distribution architecture and regulator selection"],
            assumptions=["Buck converters for large step-downs (>1.5V diff)", "LDOs for small step-downs and low noise"],
            constraints=["Efficiency > 80%", "Output voltage tolerance < 3%"],
            formula_selection="P_out = V_out * I_out, Efficiency = P_out / P_in",
            formula_explanation="Calculates power dissipation and selects regulator topology based on voltage differential.",
            unit_analysis="Voltage in V, Current in A, Power in W."
        ) as ctx:
            rails = []
            regulators = []
            
            # Sort rails by voltage descending to cascade regulators efficiently
            sorted_rails = sorted(power_rails.items(), key=lambda x: x[1]['voltage'], reverse=True)
            
            for name, specs in sorted_rails:
                v_out = specs['voltage']
                i_out = specs['current']
                p_out = v_out * i_out
                
                # Simple heuristic: Buck if delta V > 1.5V, else LDO
                reg_type = "LDO" if (input_voltage - v_out) <= 1.5 else "BUCK"
                efficiency = 0.95 if reg_type == "BUCK" else (v_out / input_voltage)
                p_diss = (p_out / efficiency) - p_out
                
                rail = PowerRail(name=name, voltage=v_out, max_current_a=i_out, source_component=f"U_REG_{name}")
                rails.append(rail)
                regulators.append({"name": name, "type": reg_type, "v_out": v_out, "p_dissipation_w": p_diss})
                
                ctx.add_intermediate(f"Regulator {name}", "P_diss = (P_out / η) - P_out", {"type": reg_type, "p_diss": p_diss})
                
            tree = PowerTree(input_voltage=input_voltage, rails=rails, regulators=regulators)
            
            # Use model_dump() for Pydantic v2
            ctx.finalize(
                final_results=tree.model_dump(),
                interpretation=f"Generated power tree with {len(rails)} rails. Total estimated dissipation: {sum(r['p_dissipation_w'] for r in regulators):.2f}W."
            )
        return ctx.report
