from typing import List, Dict
from supplier_network.services.sourcing_engine import SourcingEngine
from supplier_network.services.procurement_optimizer import ProcurementOptimizer
from supplier_network.services.supply_chain_risk_engine import SupplyChainRiskEngine
from supplier_network.adapters.octopart_adapter import OctopartAdapter

class SupplierOrchestrator:
    """Top-level orchestrator for supplier network operations."""
    
    def __init__(self):
        self.octopart = OctopartAdapter()
        self.sourcing = SourcingEngine(self.octopart)
        self.procurement = ProcurementOptimizer(self.sourcing)
        self.risk = SupplyChainRiskEngine()
        
    async def full_sourcing_analysis(self, query: str, bom: List[Dict] = None,
                                    budget_usd: float = 10000.0,
                                    max_lead_time_days: int = 30) -> Dict:
        """Complete sourcing workflow: search → quote → optimize → risk assess."""
        # 1. Search for components
        search_results = await self.sourcing.search_components(query, limit=5)
        
        result = {
            "search_results": search_results,
            "procurement": None,
            "risk_assessment": None
        }
        
        # 2. Optimize BOM if provided
        if bom:
            optimization = self.procurement.optimize_bom(bom, budget_usd, max_lead_time_days)
            result["procurement"] = optimization
            
            # 3. Risk assessment
            supplier_ids = list(set(s.get("supplier_id") for s in optimization["selections"]
                                   if "supplier_id" in s))
            suppliers = [self.sourcing.suppliers[sid] for sid in supplier_ids
                        if sid in self.sourcing.suppliers]
                        
            portfolio_risk = self.risk.compute_portfolio_risk(suppliers)
            
            # Get detailed risk reports for each supplier
            detailed_risks = []
            for s in suppliers:
                detailed_risks.extend(self.risk.assess_supplier(s))
                
            # Check single-source risk for each component in BOM
            for item in bom:
                quotes = self.sourcing.quotes.get(item["component_id"], [])
                s_ids = [q.supplier_id for q in quotes]
                detailed_risks.extend(self.risk.assess_single_source_risk(item["component_id"], s_ids))
                
            result["risk_assessment"] = {
                "portfolio_risk": portfolio_risk,
                "detailed_risks": [r.model_dump() for r in detailed_risks]
            }
            
        return result
