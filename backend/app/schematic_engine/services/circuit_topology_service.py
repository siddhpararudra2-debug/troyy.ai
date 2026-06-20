import networkx as nx
from app.schematic_engine.schemas.engineering_report import ReportContext, EngineeringReport

class CircuitTopologyService:
    def generate_topology(self, required_functions: dict) -> EngineeringReport:
        with ReportContext(
            requirements=["Determine logical circuit architecture and subsystem relationships"],
            assumptions=["Star topology for power distribution", "Bus topology for I2C/UART"],
            constraints=["MCU is the central controller", "Power flows from source to loads"],
            formula_selection="Directed Graph Theory (DAG)",
            formula_explanation="Models subsystems as nodes and signal/power flows as directed edges.",
            unit_analysis="Nodes are dimensionless, edges represent logical connections."
        ) as ctx:
            G = nx.DiGraph()
            G.add_node("MCU", type="controller")
            G.add_node("POWER_IN", type="source")
            
            for func, count in required_functions.items():
                if "I2C" in func or "UART" in func or "SPI" in func:
                    node_name = f"BUS_{func.split('_')[0]}"
                    if not G.has_node(node_name):
                        G.add_node(node_name, type="bus")
                        G.add_edge("MCU", node_name, signal=func.split('_')[0])
                elif "ADC" in func:
                    G.add_node(f"SENSOR_{func}", type="sensor")
                    G.add_edge(f"SENSOR_{func}", "MCU", signal="ANALOG")
                    
            ctx.add_intermediate("Graph Generation", "G = (V, E)", {"nodes": len(G.nodes), "edges": len(G.edges)})
            
            ctx.finalize(
                final_results={"nodes": list(G.nodes(data=True)), "edges": list(G.edges(data=True))},
                interpretation=f"Generated topology with {len(G.nodes)} subsystems and {len(G.edges)} logical connections."
            )
        return ctx.report
