from typing import List, Dict, Tuple
from supplier_network.schemas.supplier_models import ProcurementRecord, Component
from supplier_network.schemas.enums import ProcurementStatus

class ProcurementOptimizer:
    """Optimizes procurement across multiple components to minimize cost and risk."""
    
    def __init__(self, sourcing_engine):
        self.sourcing = sourcing_engine
        self.orders: List[ProcurementRecord] = []
        
    def optimize_bom(self, bom: List[Dict], budget_usd: float,
                    max_lead_time_days: int) -> Dict:
        """Optimize Bill of Materials procurement.
        bom: [{"component_id": "...", "quantity": N}, ...]"""
        
        # For each component, get best quote
        selections = []
        total_cost = 0.0
        max_lead = 0
        
        for item in bom:
            quote = self.sourcing.find_best_supplier(item["component_id"])
            if not quote:
                selections.append({
                    "component_id": item["component_id"],
                    "status": "NO_QUOTE",
                    "reason": "No supplier found"
                })
                continue
                
            quantity = max(item["quantity"], quote.moq)
            line_cost = quote.unit_price_usd * quantity
            total_cost += line_cost
            max_lead = max(max_lead, quote.lead_time_days)
            
            selections.append({
                "component_id": item["component_id"],
                "supplier_id": quote.supplier_id,
                "quantity": quantity,
                "unit_price": quote.unit_price_usd,
                "line_cost": line_cost,
                "lead_time_days": quote.lead_time_days
            })
            
        # Check constraints
        within_budget = total_cost <= budget_usd
        within_lead_time = max_lead <= max_lead_time_days
        
        return {
            "selections": selections,
            "total_cost_usd": total_cost,
            "budget_usd": budget_usd,
            "within_budget": within_budget,
            "max_lead_time_days": max_lead,
            "within_lead_time": within_lead_time,
            "feasible": within_budget and within_lead_time
        }
        
    def consolidate_suppliers(self, selections: List[Dict]) -> Dict[str, List[Dict]]:
        """Group selections by supplier to minimize shipments."""
        by_supplier: Dict[str, List[Dict]] = {}
        for s in selections:
            if "supplier_id" in s:
                by_supplier.setdefault(s["supplier_id"], []).append(s)
        return by_supplier
