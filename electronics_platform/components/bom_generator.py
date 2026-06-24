"""
BOM Generator — creates Bill of Materials from schematics.
"""
from typing import List, Dict
from collections import defaultdict
from electronics_platform.schemas.models import Schematic, BOM, BOMLine
from electronics_platform.schemas.enums import ComponentStatus

class BOMGenerator:
    """Generates Bill of Materials from schematics."""
    
    def __init__(self, component_db):
        self.db = component_db
        
    def generate(self, schematic: Schematic, project_name: str = "Project") -> BOM:
        """Generate BOM from a schematic."""
        # Group components by (value, footprint)
        groups = defaultdict(list)
        for comp in schematic.components:
            key = (comp.value, comp.footprint)
            groups[key].append(comp.ref)
            
        lines = []
        total_cost = 0.0
        unique_parts = 0
        
        for (value, footprint), refs in groups.items():
            # Find matching component in database
            matching = [c for c in self.db.components.values()
                       if c.footprint == footprint]
            
            if matching:
                comp_info = matching[0]
                mpn = comp_info.mpn
                manufacturer = comp_info.manufacturer
                description = comp_info.description
                unit_price = comp_info.price_usd
                status = comp_info.status
                alternatives = comp_info.alternatives
            else:
                # Generic entry
                mpn = f"GENERIC-{value}"
                manufacturer = "Generic"
                description = f"{value} {footprint}"
                unit_price = 0.01
                status = ComponentStatus.UNKNOWN
                alternatives = []
                
            quantity = len(refs)
            total_price = unit_price * quantity
            total_cost += total_price
            unique_parts += 1
            
            line = BOMLine(
                ref_des=sorted(refs),
                quantity=quantity,
                value=value,
                footprint=footprint,
                mpn=mpn,
                manufacturer=manufacturer,
                description=description,
                unit_price_usd=unit_price,
                total_price_usd=total_price,
                status=status,
                alternatives=alternatives
            )
            lines.append(line)
            
        # Sort by reference designator prefix
        lines.sort(key=lambda l: (l.ref_des[0][0], l.ref_des[0]))
        
        bom = BOM(
            project_name=project_name,
            lines=lines,
            total_cost_usd=total_cost,
            unique_parts=unique_parts,
            total_components=sum(l.quantity for l in lines)
        )
        
        return bom
        
    def check_obsolescence(self, bom: BOM) -> Dict:
        """Check BOM for obsolete or at-risk components."""
        at_risk = []
        obsolete = []
        
        for line in bom.lines:
            lifecycle = self.db.check_lifecycle(line.mpn)
            if lifecycle["risk"] == "CRITICAL":
                obsolete.append(line)
            elif lifecycle["risk"] == "MEDIUM":
                at_risk.append(line)
                
        return {
            "at_risk_count": len(at_risk),
            "obsolete_count": len(obsolete),
            "at_risk": [l.mpn for l in at_risk],
            "obsolete": [l.mpn for l in obsolete],
            "overall_risk": "HIGH" if obsolete else ("MEDIUM" if at_risk else "LOW")
        }
        
    def format_markdown(self, bom: BOM) -> str:
        """Format BOM as Markdown table."""
        lines = [f"# Bill of Materials — {bom.project_name}",
                f"\n**Version:** {bom.version}  ",
                f"**Generated:** {bom.created_at.strftime('%Y-%m-%d %H:%M')}  ",
                f"**Total Cost:** ${bom.total_cost_usd:.2f}  ",
                f"**Unique Parts:** {bom.unique_parts}  ",
                f"**Total Components:** {bom.total_components}\n"]
                
        lines.append("| Ref Des | Qty | Value | Footprint | MPN | Manufacturer | Unit $ | Total $ | Status |")
        lines.append("|---------|-----|-------|-----------|-----|--------------|--------|---------|--------|")
        
        for line in bom.lines:
            refs = ", ".join(line.ref_des)
            lines.append(f"| {refs} | {line.quantity} | {line.value} | {line.footprint} | "
                        f"{line.mpn} | {line.manufacturer} | ${line.unit_price_usd:.4f} | "
                        f"${line.total_price_usd:.2f} | {line.status.value} |")
                        
        return "\n".join(lines)
