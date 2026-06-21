import asyncio
from typing import Dict
from engineering_swarm.agents.base_agent import MechanicalAgent, ElectronicsAgent, SimulationAgent, ComplianceAgent
from engineering_swarm.services.debate_engine import DebateEngine
from engineering_swarm.services.consensus_engine import ConsensusEngine

class SwarmOrchestrator:
    def __init__(self):
        self.agents = [
            MechanicalAgent(),
            ElectronicsAgent(),
            SimulationAgent(),
            ComplianceAgent()
        ]
        self.debate_engine = DebateEngine(max_rounds=5)
        self.consensus_engine = ConsensusEngine(threshold=0.7)
        
    async def solve_engineering_problem(self, problem: Dict) -> Dict:
        positions = await asyncio.gather(*[
            asyncio.to_thread(agent.analyze, problem) for agent in self.agents
        ])
        
        debate_result = self.debate_engine.conduct_debate(positions, problem.get('topic', 'Design'))
        
        agent_weights = {a.agent_id: a.expertise_weight for a in self.agents}
        consensus = self.consensus_engine.reach_consensus(
            positions, 
            problem.get('topic', 'Design'),
            agent_weights
        )
        
        for agent in self.agents:
            agent.update_memory(f"consensus_{problem.get('topic', 'design')}", consensus.dict())
            
        return {
            "problem": problem,
            "positions": [p.dict() for p in positions],
            "debate": debate_result,
            "consensus": consensus.dict(),
            "agent_memories": {a.agent_id: {"facts": a.memory.facts, "version": a.memory.version} for a in self.agents}
        }
