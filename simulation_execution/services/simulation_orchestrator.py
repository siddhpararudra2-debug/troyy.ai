import asyncio
from typing import List, Dict
from simulation_execution.schemas.simulation_models import SimulationJob, SimulationResult
from simulation_execution.schemas.enums import JobStatus, SimulationDomain, SolverType
from simulation_execution.services.solver_manager import SolverManager
from simulation_execution.services.simulation_validator import SimulationValidator
from simulation_execution.services.result_processor import ResultProcessor

class SimulationOrchestrator:
    """Coordinates multi-physics simulation campaigns."""
    
    def __init__(self):
        self.solver_manager = SolverManager()
        self.validator = SimulationValidator()
        self.result_processor = ResultProcessor()
        self.jobs: Dict[str, SimulationJob] = {}
        self.results: Dict[str, SimulationResult] = {}
        
    def _select_solver(self, domain: SimulationDomain) -> SolverType:
        """Map simulation domain to appropriate solver."""
        mapping = {
            SimulationDomain.STRUCTURAL: SolverType.CALCULIX,
            SimulationDomain.THERMAL: SolverType.CALCULIX,  # CalculiX handles thermal
            SimulationDomain.CFD: SolverType.OPENFOAM,
            SimulationDomain.CIRCUIT: SolverType.NGSPICE,
            SimulationDomain.MULTIBODY: SolverType.CALCULIX,  # Placeholder
            SimulationDomain.ELECTROMAGNETIC: SolverType.ELMER,
            SimulationDomain.MULTI_PHYSICS: SolverType.ELMER,
        }
        return mapping.get(domain, SolverType.CALCULIX)
        
    async def submit_job(self, job: SimulationJob) -> str:
        """Validate and submit a simulation job."""
        # Validate inputs
        validation = self.validator.validate(job)
        if not validation["valid"]:
            raise ValueError(f"Job validation failed: {validation['errors']}")
            
        self.jobs[job.id] = job
        job.status = JobStatus.QUEUED
        return job.id
        
    async def execute_job(self, job_id: str) -> SimulationResult:
        """Execute a single job synchronously (in production, via Celery worker)."""
        job = self.jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
            
        job.status = JobStatus.RUNNING
        job.started_at = __import__("datetime").datetime.utcnow()
        
        solver_type = self._select_solver(job.domain)
        adapter = self.solver_manager.get(solver_type)
        
        # Run solver in thread pool to avoid blocking
        result = await asyncio.to_thread(adapter.run, job)
        
        job.status = result.status
        job.completed_at = __import__("datetime").datetime.utcnow()
        job.result_ref = str(result.result_files) if result.result_files else None
        
        # Post-process results
        processed = self.result_processor.process(result, job)
        self.results[job_id] = processed
        
        return processed
        
    async def run_campaign(self, jobs: List[SimulationJob]) -> Dict[str, SimulationResult]:
        """Execute multiple jobs, with multi-physics coupling where needed."""
        # Submit all
        job_ids = []
        for job in jobs:
            jid = await self.submit_job(job)
            job_ids.append(jid)
            
        # Execute in parallel (in production, distributed across HPC nodes)
        results = await asyncio.gather(*[self.execute_job(jid) for jid in job_ids])
        
        return {jid: res for jid, res in zip(job_ids, results)}
