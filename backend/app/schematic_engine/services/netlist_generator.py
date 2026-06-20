import json
from app.schematic_engine.schemas.engineering_report import ReportContext, EngineeringReport
from app.schematic_engine.schemas.schematic_models import SchematicNetlist, Net

class NetlistGenerator:
    def generate(self, components: list, nets: list) -> EngineeringReport:
        with ReportContext(
            requirements=["Generate machine-readable netlists for CAD import and simulation"],
            assumptions=["Standard SPICE/KiCad netlist conventions", "Unique reference designators"],
            constraints=["Must support JSON and KiCad S-Expression formats"],
            formula_selection="Hierarchical Data Serialization",
            formula_explanation="Flattens the schematic graph into a standardized list of components and nodes.",
            unit_analysis="Data structures, no physical units."
        ) as ctx:
            netlist = SchematicNetlist(
                components=components,
                nets=[Net(**n) for n in nets],
                metadata={"tool": "Personal Engineering OS", "version": "1.0"}
            )
            
            # Generate KiCad S-Expression (Simplified)
            kicad_sexp = ["(export (version 20230121)"]
            kicad_sexp.append("  (components")
            for comp in components:
                # comp can be a Component object or a dict because SchematicNetlist validation might run
                # but components is passed as list of dicts. Let's handle both.
                ref = comp.ref if hasattr(comp, 'ref') else comp.get('ref')
                val = comp.value if hasattr(comp, 'value') else comp.get('value')
                fp = comp.footprint if hasattr(comp, 'footprint') else comp.get('footprint')
                kicad_sexp.append(f'    (comp (ref "{ref}") (value "{val}") (footprint "{fp}"))')
            kicad_sexp.append("  )")
            kicad_sexp.append("  (nets")
            for net in nets:
                kicad_sexp.append(f'    (net (code "{net["name"]}") (name "{net["name"]}")')
                for conn in net.get("connections", []):
                    # conn can be NetConnection or dict
                    comp_ref = conn.comp_ref if hasattr(conn, 'comp_ref') else conn.get('comp_ref')
                    pin_name = conn.pin_name if hasattr(conn, 'pin_name') else conn.get('pin_name')
                    kicad_sexp.append(f'      (node (ref "{comp_ref}") (pin "{pin_name}"))')
                kicad_sexp.append("    )")
            kicad_sexp.append("  )")
            kicad_sexp.append(")")
            
            ctx.finalize(
                final_results={
                    "json_netlist": netlist.model_dump(),
                    "kicad_sexp": "\n".join(kicad_sexp)
                },
                interpretation=f"Generated netlist with {len(components)} components and {len(nets)} nets. Ready for KiCad import."
            )
        return ctx.report
