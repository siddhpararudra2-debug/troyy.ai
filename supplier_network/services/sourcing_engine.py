from typing import List, Dict, Optional
from datetime import datetime, timedelta
from supplier_network.schemas.supplier_models import Component, Quote, Supplier
from supplier_network.schemas.enums import SupplierCategory
from supplier_network.adapters.octopart_adapter import OctopartAdapter

class SourcingEngine:
    """Finds optimal suppliers for components based on price, lead time, and risk."""
    
    def __init__(self, octopart: OctopartAdapter):
        self.octopart = octopart
        self.suppliers: Dict[str, Supplier] = {}
        self.components: Dict[str, Component] = {}
        self.quotes: Dict[str, List[Quote]] = {}
        self._seed_suppliers()
        
    def _seed_suppliers(self):
        """Seed with known suppliers."""
        suppliers = [
            Supplier(name="DigiKey", category=SupplierCategory.ELECTRONICS,
                    country="US", certifications=["ISO9001"], lead_time_days=3,
                    reliability_score=0.98, price_index=1.0),
            Supplier(name="Mouser", category=SupplierCategory.ELECTRONICS,
                    country="US", certifications=["ISO9001"], lead_time_days=3,
                    reliability_score=0.97, price_index=1.02),
            Supplier(name="Arrow", category=SupplierCategory.ELECTRONICS,
                    country="US", certifications=["ISO9001", "AS9120"], lead_time_days=5,
                    reliability_score=0.95, price_index=0.98),
            Supplier(name="PCBWay", category=SupplierCategory.PCB_MANUFACTURER,
                    country="CN", certifications=["ISO9001", "UL"], lead_time_days=7,
                    reliability_score=0.90, price_index=0.6),
            Supplier(name="ProtoLabs", category=SupplierCategory.MACHINING,
                    country="US", certifications=["AS9100", "ISO9001"], lead_time_days=5,
                    reliability_score=0.95, price_index=1.5),
        ]
        for s in suppliers:
            self.suppliers[s.id] = s
            
    async def search_components(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for components across internal DB and external sources."""
        # Search Octopart
        external = await self.octopart.search_components(query, limit)
        
        # Combine with internal matches
        internal = [c.model_dump() for c in self.components.values()
                   if query.lower() in c.description.lower() or query.lower() in c.mpn.lower()]
                   
        return external + internal[:limit]
        
    def find_best_supplier(self, component_id: str, criteria: Dict[str, float] = None) -> Optional[Quote]:
        """Find best supplier using weighted scoring.
        criteria weights: {'price': 0.4, 'lead_time': 0.3, 'reliability': 0.3}"""
        if criteria is None:
            criteria = {"price": 0.4, "lead_time_days": 0.3, "reliability": 0.3}
            
        quotes = self.quotes.get(component_id, [])
        if not quotes:
            return None
            
        # Normalize each dimension
        max_price = max(q.unit_price_usd for q in quotes) or 1
        max_lead = max(q.lead_time_days for q in quotes) or 1
        
        best_quote = None
        best_score = -float('inf')
        
        for quote in quotes:
            supplier = self.suppliers.get(quote.supplier_id)
            if not supplier:
                continue
                
            # Lower is better for price and lead time
            price_score = 1 - (quote.unit_price_usd / max_price)
            lead_score = 1 - (quote.lead_time_days / max_lead)
            reliability_score = supplier.reliability_score
            
            total_score = (
                criteria.get("price", 0) * price_score +
                criteria.get("lead_time_days", 0) * lead_score +
                criteria.get("reliability", 0) * reliability_score
            )
            
            if total_score > best_score:
                best_score = total_score
                best_quote = quote
                
        return best_quote
        
    def add_quote(self, component_id: str, supplier_id: str, unit_price: float,
                 lead_time_days: int, moq: int = 1) -> Quote:
        quote = Quote(
            component_id=component_id,
            supplier_id=supplier_id,
            unit_price_usd=unit_price,
            lead_time_days=lead_time_days,
            moq=moq,
            valid_until=datetime.utcnow() + timedelta(days=30)
        )
        self.quotes.setdefault(component_id, []).append(quote)
        return quote
