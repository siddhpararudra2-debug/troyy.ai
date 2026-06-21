import pytest
from engineering_swarm.services.swarm_orchestrator import SwarmOrchestrator
from engineering_swarm.services.debate_engine import DebateEngine
from engineering_swarm.services.consensus_engine import ConsensusEngine
from engineering_swarm.schemas.swarm_models import DebatePosition, AgentRole

@pytest.mark.asyncio
async def test_swarm_orchestration():
    orch = SwarmOrchestrator()
    problem = {"topic": "VTOL_Design", "payload_kg": 5.0, "power_budget_w": 500, "domain": "DRONE"}
    result = await orch.solve_engineering_problem(problem)
    
    assert "consensus" in result
    assert result["consensus"]["confidence"] > 0
    assert len(result["positions"]) == 4

def test_debate_engine():
    engine = DebateEngine(max_rounds=3)
    positions = [
        DebatePosition(agent_id="A1", role=AgentRole.MECHANICAL, claim="Use aluminum", confidence=0.8),
        DebatePosition(agent_id="A2", role=AgentRole.ELECTRONICS, claim="Use titanium", confidence=0.7)
    ]
    result = engine.conduct_debate(positions, "Material Selection")
    assert result["rounds"] >= 1

def test_consensus_engine():
    engine = ConsensusEngine(threshold=0.7)
    positions = [
        DebatePosition(agent_id="A1", role=AgentRole.MECHANICAL, claim="Aluminum", confidence=0.9),
        DebatePosition(agent_id="A2", role=AgentRole.ELECTRONICS, claim="Aluminum", confidence=0.85),
        DebatePosition(agent_id="A3", role=AgentRole.SIMULATION, claim="Titanium", confidence=0.6)
    ]
    result = engine.reach_consensus(positions, "Material", {"A1": 2.0, "A2": 2.0, "A3": 1.5})
    assert result.decision == "Aluminum"
    assert result.confidence > 0.5
