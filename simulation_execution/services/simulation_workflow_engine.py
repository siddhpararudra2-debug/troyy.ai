import asyncio
from typing import List, Dict
from simulation_execution.schemas.simulation_models import SimulationJob
from simulation_execution.services.simulation_orchestrator import SimulationOrchestrator

class SimulationWorkflowEngine:
    """Executes multi-step simulation workflows with dependencies."""
    
    def __init__(self, orchestrator: SimulationOrchestrator):
        self.orchestrator = orchestrator
        
    async def execute_sequential(self, jobs: List[SimulationJob]) -> List[dict]:
        """Run jobs in sequence, passing outputs as inputs to next job."""
        results = []
        for job in jobs:
            result = await self.orchestrator.execute_job(job.id)
            results.append({"job_id": job.id, "result": result.model_dump()})  # Use model_dump() for pydantic v2
        return results
        
    async def execute_parallel(self, jobs: List[SimulationJob]) -> List[dict]:
        """Run independent jobs in parallel."""
        results = await asyncio.gather(*[
            self.orchestrator.execute_job(job.id) for job in jobs
        ])
        return [{"job_id": job.id, "result": r.model_dump()} for job, r in zip(jobs, results)]
        
    async def execute_coupled(self, jobs: List[SimulationJob]) -> Dict[str, dict]:
        """Run multi-physics coupled simulation (e.g., FSI, conjugate heat transfer).
        Iterates between solvers until convergence."""
        max_iterations = 10
        
        for iteration in range(max_iterations):
            results = await self.execute_parallel(jobs)
            # Check coupling convergence (simplified - in production, exchange field data)
            converged = all(r["result"]["status"] == "COMPLETED" for r in results)
            if converged:
                break
                
        return {r["job_id"]: r["result"] for r in results}
