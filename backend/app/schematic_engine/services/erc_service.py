from app.schematic_engine.schemas.engineering_report import ReportContext, EngineeringReport

class ERCService:
    def run_erc(self, netlist: dict) -> EngineeringReport:
        with ReportContext(
            requirements=["Perform Electrical Rule Checking to detect schematic errors"],
            assumptions=["Netlist is logically complete", "Pin directions are strictly typed"],
            constraints=["No shorted outputs", "No floating signal nets", "Voltage levels must match"],
            formula_selection="Graph Traversal & Rule Evaluation",
            formula_explanation="Iterates through all nets and applies a set of deterministic electrical rules.",
            unit_analysis="Rules evaluate categorical and numerical constraints."
        ) as ctx:
            errors = []
            warnings = []
            
            for net in netlist.get('nets', []):
                net_name = net['name']
                connections = net.get('connections', [])
                
                # Rule 1: Check for shorted outputs
                outputs = []
                for c in connections:
                    # direction can be a string or a PinDirection enum object, check both
                    direction = c.get('direction')
                    if direction and hasattr(direction, 'value'):
                        direction = direction.value
                    if direction == "OUTPUT":
                        outputs.append(c)
                
                if len(outputs) > 1 and net['net_type'] != "BIDIRECTIONAL":
                    errors.append(f"ERC ERROR: Short circuit on net '{net_name}'. Multiple outputs connected: {[c['comp_ref'] for c in outputs]}")
                    
                # Rule 2: Check for floating signal nets
                if net['net_type'] == "SIGNAL" and len(connections) < 2:
                    warnings.append(f"ERC WARNING: Floating net '{net_name}'. Only {len(connections)} connection(s).")
                    
                # Rule 3: Voltage mismatch (simplified)
                if net['net_type'] == "POWER" and net.get('voltage') is None:
                    errors.append(f"ERC ERROR: Power net '{net_name}' has undefined voltage.")
                    
            ctx.add_intermediate("ERC Execution", "Rules Applied", {"errors": len(errors), "warnings": len(warnings)})
            
            status = "PASS" if not errors else "FAIL"
            ctx.finalize(
                final_results={"status": status, "errors": errors, "warnings": warnings},
                interpretation=f"ERC completed. Status: {status}. Found {len(errors)} errors and {len(warnings)} warnings."
            )
        return ctx.report
