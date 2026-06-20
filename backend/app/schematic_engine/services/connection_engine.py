from app.schematic_engine.schemas.engineering_report import ReportContext, EngineeringReport
from app.schematic_engine.schemas.schematic_models import Component, ComponentPin, Net, NetConnection

class ConnectionEngine:
    def build_nets(self, pin_mapping: dict, power_tree: dict) -> EngineeringReport:
        with ReportContext(
            requirements=["Generate logical electrical connections (nets) between components"],
            assumptions=["Components with the same net name are electrically connected", "Power nets are globally shared"],
            constraints=["No floating signal nets", "Power nets must have a source"],
            formula_selection="Netlist Graph Flattening",
            formula_explanation="Aggregates component pins into unified electrical nodes (nets).",
            unit_analysis="Nets are logical groupings, no physical units."
        ) as ctx:
            nets = {}
            
            # Create Power Nets
            for rail in power_tree.get('rails', []):
                net_name = rail['name']
                nets[net_name] = Net(name=net_name, net_type="POWER", voltage=rail['voltage'])
            nets["GND"] = Net(name="GND", net_type="GROUND", voltage=0.0)
            
            # Create Signal Nets from Pin Mapping
            for func, pin in pin_mapping.items():
                net_name = f"NET_{func}"
                # Determine net type based on function
                n_type = "BIDIRECTIONAL" if "I2C" in func or "SPI" in func else "SIGNAL"
                nets[net_name] = Net(name=net_name, net_type=n_type)
                
                # Mock adding connections (in reality, this links MCU pins to peripheral pins)
                nets[net_name].connections.append(NetConnection(comp_ref="U1_MCU", pin_name=pin, direction="OUTPUT"))
                nets[net_name].connections.append(NetConnection(comp_ref=f"J_{func}", pin_name="1", direction="INPUT"))
                
            ctx.add_intermediate("Net Aggregation", "N = Union(P_i)", {"total_nets": len(nets)})
            
            # Use model_dump() for Pydantic v2
            ctx.finalize(
                final_results={"nets": [n.model_dump() for n in nets.values()]},
                interpretation=f"Generated {len(nets)} logical nets, including {sum(1 for n in nets.values() if n.net_type == 'POWER')} power rails."
            )
        return ctx.report
