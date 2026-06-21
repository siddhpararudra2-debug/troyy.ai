from fastapi import APIRouter
from engineering_swarm.services.swarm_orchestrator import SwarmOrchestrator

router = APIRouter(prefix="/swarm", tags=["Multi-Agent Engineering Swarm"])
orchestrator = SwarmOrchestrator()

@router.post("/solve")
async def solve_problem(problem: dict):
    return await orchestrator.solve_engineering_problem(problem)

@router.get("/agents")
async def list_agents():
    return [{"id": a.agent_id, "role": a.role.value, "weight": a.expertise_weight} 
            for a in orchestrator.agents]
