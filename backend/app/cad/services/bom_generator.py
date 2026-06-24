"""
BOM Generator - Generates Bill of Materials
"""
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
from pathlib import Path
import csv
import logging

logger = logging.getLogger(__name__)


class BOMGenerator:
    """Generates Bill of Materials from assemblies."""
    
    def __init__(self):
        self.cost_estimator = CostEstimator()
        self.procurement_export = ProcurementExport()
    
    def generate_bom(
        self, 
        assembly: Dict[str, Any],
        include_subassemblies: bool = True
    ) -> Dict[str, Any]:
        """Generate a BOM from an assembly."""
        bom_items = []
        
        # Process all parts in assembly
        for part_instance in assembly.get("parts", []):
            part = part_instance.get("part", {})
            bom_item = self._create_bom_item(part)
            bom_items.append(bom_item)
        
        # Group by part ID and count quantities
        grouped_items = self._group_bom_items(bom_items)
        
        # Calculate costs
        total_cost = self.cost_estimator.calculate_total_cost(grouped_items)
        
        bom = {
            "id": str(uuid.uuid4()),
            "assembly_id": assembly.get("id"),
            "assembly_name": assembly.get("name"),
            "items": grouped_items,
            "total_cost": total_cost,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        return bom
    
    def _create_bom_item(self, part: Dict[str, Any]) -> Dict[str, Any]:
        """Create a BOM item from a part."""
        return {
            "part_id": part.get("id"),
            "part_number": part.get("part_number", part.get("id")),
            "name": part.get("name", "Unnamed Part"),
            "quantity": 1,
            "material": part.get("material", "unknown"),
            "cost": part.get("cost", 0.0),
            "supplier": part.get("supplier", "unknown"),
        }
    
    def _group_bom_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group BOM items by part ID and sum quantities."""
        grouped = {}
        
        for item in items:
            part_id = item["part_id"]
            if part_id in grouped:
                grouped[part_id]["quantity"] += 1
            else:
                grouped[part_id] = item.copy()
        
        return list(grouped.values())
    
    def export_bom(
        self, 
        bom: Dict[str, Any],
        format: str = "csv",
        output_path: Optional[str] = None
    ) -> str:
        """Export BOM to specified format."""
        if format == "csv":
            return self.procurement_export.export_csv(bom, output_path)
        elif format == "excel":
            return self.procurement_export.export_excel(bom, output_path)
        elif format == "pdf":
            return self.procurement_export.export_pdf(bom, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")


class CostEstimator:
    """Estimates costs for BOM items."""
    
    def calculate_total_cost(self, bom_items: List[Dict[str, Any]]) -> float:
        """Calculate total cost of all BOM items."""
        total = 0.0
        
        for item in bom_items:
            item_total = self.calculate_item_total(item)
            total += item_total
        
        return total
    
    def calculate_item_total(self, item: Dict[str, Any]) -> float:
        """Calculate total cost for a single BOM item."""
        unit_cost = item.get("cost", 0.0)
        quantity = item.get("quantity", 1)
        return unit_cost * quantity
    
    def add_cost_breakdown(self, bom: Dict[str, Any]) -> Dict[str, Any]:
        """Add detailed cost breakdown to BOM."""
        breakdown = {
            "material_cost": 0.0,
            "labor_cost": 0.0,
            "overhead_cost": 0.0,
            "total_cost": bom["total_cost"],
        }
        
        # Simplified breakdown
        breakdown["material_cost"] = bom["total_cost"] * 0.6
        breakdown["labor_cost"] = bom["total_cost"] * 0.25
        breakdown["overhead_cost"] = bom["total_cost"] * 0.15
        
        bom["cost_breakdown"] = breakdown
        return bom


class ProcurementExport:
    """Exports BOM for procurement purposes."""
    
    def export_csv(
        self, 
        bom: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """Export BOM to CSV format."""
        if not output_path:
            output_path = f"/exports/bom_{bom['id']}.csv"
        
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", newline="") as csvfile:
            fieldnames = [
                "part_number", "name", "quantity", "material", 
                "cost", "total_cost", "supplier"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for item in bom["items"]:
                writer.writerow({
                    "part_number": item["part_number"],
                    "name": item["name"],
                    "quantity": item["quantity"],
                    "material": item["material"],
                    "cost": item["cost"],
                    "total_cost": item["cost"] * item["quantity"],
                    "supplier": item["supplier"],
                })
        
        logger.info(f"Exported BOM to {path}")
        return str(path)
    
    def export_excel(
        self, 
        bom: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """Export BOM to Excel format (placeholder)."""
        if not output_path:
            output_path = f"/exports/bom_{bom['id']}.xlsx"
        
        # In real implementation, use openpyxl or pandas
        logger.info(f"Exported BOM to {output_path}")
        return output_path
    
    def export_pdf(
        self, 
        bom: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """Export BOM to PDF format (placeholder)."""
        if not output_path:
            output_path = f"/exports/bom_{bom['id']}.pdf"
        
        # In real implementation, use ReportLab or WeasyPrint
        logger.info(f"Exported BOM to {output_path}")
        return output_path
