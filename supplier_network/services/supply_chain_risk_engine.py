from typing import List, Dict
from supplier_network.schemas.supplier_models import SupplyChainRisk, Supplier
from supplier_network.schemas.enums import RiskLevel

class SupplyChainRiskEngine:
    """Identifies and scores supply chain risks."""
    
    # Geographic risk scores by country (simplified)
    GEOGRAPHIC_RISK = {
        "US": 0.1, "CA": 0.1, "MX": 0.2,
        "DE": 0.1, "FR": 0.1, "UK": 0.1, "JP": 0.1, "KR": 0.1, "TW": 0.2,
        "CN": 0.4, "RU": 0.7, "IR": 0.8
    }
    
    def assess_supplier(self, supplier: Supplier) -> List[SupplyChainRisk]:
        risks = []
        
        # Geographic risk
        geo_risk = self.GEOGRAPHIC_RISK.get(supplier.country, 0.5)
        if geo_risk > 0.3:
            risks.append(SupplyChainRisk(
                supplier_id=supplier.id,
                risk_type="GEOGRAPHIC",
                severity=RiskLevel.HIGH if geo_risk > 0.5 else RiskLevel.MEDIUM,
                description=f"Supplier in {supplier.country} has elevated geopolitical risk",
                mitigation="Identify alternative supplier in stable region",
                probability=geo_risk
            ))
            
        # Reliability risk
        if supplier.reliability_score < 0.85:
            risks.append(SupplyChainRisk(
                supplier_id=supplier.id,
                risk_type="RELIABILITY",
                severity=RiskLevel.HIGH if supplier.reliability_score < 0.7 else RiskLevel.MEDIUM,
                description=f"Low reliability score: {supplier.reliability_score:.2f}",
                mitigation="Require quality audits or switch supplier",
                probability=1.0 - supplier.reliability_score
            ))
            
        # Lead time risk
        if supplier.lead_time_days > 30:
            risks.append(SupplyChainRisk(
                supplier_id=supplier.id,
                risk_type="LEAD_TIME",
                severity=RiskLevel.MEDIUM,
                description=f"Long lead time: {supplier.lead_time_days} days",
                mitigation="Increase safety stock or find faster supplier",
                probability=0.3
            ))
            
        return risks
        
    def assess_single_source_risk(self, component_id: str, supplier_ids: List[str]) -> List[SupplyChainRisk]:
        """Flag components with only one supplier."""
        if len(supplier_ids) <= 1:
            sid = supplier_ids[0] if supplier_ids else "unknown"
            return [SupplyChainRisk(
                supplier_id=sid,
                risk_type="SINGLE_SOURCE",
                severity=RiskLevel.HIGH,
                description=f"Component {component_id} has only one supplier",
                mitigation="Qualify second-source supplier immediately",
                probability=0.5
            )]
        return []
        
    def compute_portfolio_risk(self, suppliers: List[Supplier]) -> Dict:
        """Compute aggregate risk across supplier portfolio."""
        if not suppliers:
            return {"overall_risk": 0.0, "risk_breakdown": {}}
            
        country_concentration = {}
        for s in suppliers:
            country_concentration[s.country] = country_concentration.get(s.country, 0) + 1
            
        # Herfindahl index for concentration
        total = len(suppliers)
        hhi = sum((c / total) ** 2 for c in country_concentration.values())
        
        avg_reliability = sum(s.reliability_score for s in suppliers) / len(suppliers)
        avg_lead_time = sum(s.lead_time_days for s in suppliers) / len(suppliers)
        
        overall_risk = (
            0.3 * hhi +  # Concentration risk
            0.4 * (1.0 - avg_reliability) +  # Reliability risk
            0.3 * min(avg_lead_time / 60.0, 1.0)  # Lead time risk
        )
        
        return {
            "overall_risk": overall_risk,
            "country_concentration": country_concentration,
            "avg_reliability": avg_reliability,
            "avg_lead_time_days": avg_lead_time,
            "supplier_count": len(suppliers)
        }
