import pytest
from engineering_org.services.engineering_operations import EngineeringOperations
from engineering_org.services.ceo_agent import CEOAgent
from engineering_org.schemas.org_models import EngineeringOrganization

@pytest.mark.asyncio
async def test_full_organization_execution():
    ops = EngineeringOperations()
    result = await ops.execute_full_project(
        "Test VTOL",
        {"domain": "DRONE", "payload_kg": 5, "endurance_min": 60},
        "HIGH"
    )
    assert result["status"] == "EXECUTED"
    assert len(result["execution"]) > 0

def test_ceo_initiation():
    org = EngineeringOrganization()
    ceo = CEOAgent(org)
    report = ceo.initiate_project("Test", {"domain": "DRONE"}, "HIGH")
    assert report.final_results['priority'] == "HIGH"
    assert len(report.final_results['departments']) > 0

def test_strategic_directive():
    org = EngineeringOrganization()
    ceo = CEOAgent(org)
    report = ceo.set_strategic_directive("Q3 Goals", ["Launch 3 products"], {"budget": 100000})
    assert report.final_results['title'] == "Q3 Goals"
