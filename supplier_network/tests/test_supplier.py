import pytest
from datetime import datetime, timedelta
from supplier_network.schemas.enums import SupplierCategory, RiskLevel, ProcurementStatus
from supplier_network.schemas.supplier_models import Supplier, Component, Quote
from supplier_network.adapters.octopart_adapter import OctopartAdapter
from supplier_network.services.sourcing_engine import SourcingEngine
from supplier_network.services.procurement_optimizer import ProcurementOptimizer
from supplier_network.services.supply_chain_risk_engine import SupplyChainRiskEngine
from supplier_network.services.supplier_orchestrator import SupplierOrchestrator

@pytest.mark.asyncio
async def test_sourcing_engine_search():
    octopart = OctopartAdapter()
    engine = SourcingEngine(octopart)
    
    # Test searching for mock electronics
    results = await engine.search_components("stm32")
    assert len(results) > 0
    assert results[0]["mpn"].startswith("STM32")

def test_sourcing_engine_best_supplier():
    octopart = OctopartAdapter()
    engine = SourcingEngine(octopart)
    
    # Add dummy quotes
    # Supplier DigiKey is US (reliable, standard price)
    # Supplier PCBWay is CN (less reliable, cheap)
    comp_id = "comp-1"
    
    # Get DigiKey and PCBWay from seeded suppliers
    dk = next(s for s in engine.suppliers.values() if s.name == "DigiKey")
    pcb = next(s for s in engine.suppliers.values() if s.name == "PCBWay")
    
    q1 = engine.add_quote(comp_id, dk.id, unit_price=10.0, lead_time_days=3)
    q2 = engine.add_quote(comp_id, pcb.id, unit_price=5.0, lead_time_days=7)
    
    # Weight on price
    best_price = engine.find_best_supplier(comp_id, {"price": 1.0, "lead_time_days": 0.0, "reliability": 0.0})
    assert best_price.supplier_id == pcb.id
    
    # Weight on reliability/lead time
    best_reliability = engine.find_best_supplier(comp_id, {"price": 0.0, "lead_time_days": 0.0, "reliability": 1.0})
    assert best_reliability.supplier_id == dk.id

def test_procurement_optimizer():
    octopart = OctopartAdapter()
    engine = SourcingEngine(octopart)
    optimizer = ProcurementOptimizer(engine)
    
    dk = next(s for s in engine.suppliers.values() if s.name == "DigiKey")
    comp_id = "comp-1"
    engine.add_quote(comp_id, dk.id, unit_price=2.0, lead_time_days=3)
    
    bom = [{"component_id": comp_id, "quantity": 100}]
    
    opt_result = optimizer.optimize_bom(bom, budget_usd=500.0, max_lead_time_days=10)
    assert opt_result["feasible"]
    assert opt_result["total_cost_usd"] == 200.0
    
    opt_result_infeasible = optimizer.optimize_bom(bom, budget_usd=100.0, max_lead_time_days=10)
    assert not opt_result_infeasible["feasible"]

def test_risk_engine():
    octopart = OctopartAdapter()
    engine = SourcingEngine(octopart)
    risk_engine = SupplyChainRiskEngine()
    
    # Geopolitically high risk supplier (e.g. PCBWay in CN)
    cn_supplier = next(s for s in engine.suppliers.values() if s.name == "PCBWay")
    risks = risk_engine.assess_supplier(cn_supplier)
    assert any(r.risk_type == "GEOGRAPHIC" for r in risks)
    
    # Test portfolio risk
    portfolio = list(engine.suppliers.values())
    portfolio_risk = risk_engine.compute_portfolio_risk(portfolio)
    assert portfolio_risk["overall_risk"] > 0
    assert portfolio_risk["supplier_count"] == len(portfolio)

@pytest.mark.asyncio
async def test_supplier_orchestrator():
    orchestrator = SupplierOrchestrator()
    # Add dummy quote for testing
    comp_id = "comp-1"
    dk = next(s for s in orchestrator.sourcing.suppliers.values() if s.name == "DigiKey")
    orchestrator.sourcing.add_quote(comp_id, dk.id, unit_price=2.0, lead_time_days=3)
    
    bom = [{"component_id": comp_id, "quantity": 10}]
    analysis = await orchestrator.full_sourcing_analysis("stm32", bom=bom)
    
    assert len(analysis["search_results"]) > 0
    assert analysis["procurement"] is not None
    assert analysis["risk_assessment"] is not None
