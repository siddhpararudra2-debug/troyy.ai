from app.schematic_engine.schemas.engineering_report import EngineeringReport

class SchematicGenerator:
    def __init__(self, topo, pwr, pin, conn, net, erc, rev):
        self.topo = topo
        self.pwr = pwr
        self.pin = pin
        self.conn = conn
        self.net = net
        self.erc = erc
        self.rev = rev

    def generate_full_schematic(self, req: dict) -> dict:
        # 1. Topology
        topo_report = self.topo.generate_topology(req['required_functions'])
        
        # 2. Power Tree
        pwr_report = self.pwr.generate_tree(req['input_voltage'], req['power_rails'])
        
        # 3. Pin Mapping
        pin_report = self.pin.assign_pins(req['mcu_pinout'], req['required_functions'])
        
        # 4. Connections
        conn_report = self.conn.build_nets(pin_report.final_results['pin_mapping'], pwr_report.final_results)
        
        # 5. Netlist
        # Mock components for the netlist generator
        mock_components = [{"ref": "U1_MCU", "value": "STM32F4", "footprint": "LQFP-64", "pins": []}]
        net_report = self.net.generate(mock_components, conn_report.final_results['nets'])
        
        # 6. ERC
        erc_report = self.erc.run_erc(net_report.final_results['json_netlist'])
        
        # 7. Review
        rev_report = self.rev.review(net_report.final_results['json_netlist'], erc_report.final_results)
        
        return {
            "topology": topo_report.final_results,
            "power_tree": pwr_report.final_results,
            "pin_mapping": pin_report.final_results,
            "connections": conn_report.final_results,
            "netlist": net_report.final_results,
            "erc": erc_report.final_results,
            "review": rev_report.final_results
        }
