import subprocess
import os
import shutil
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from simulation_execution.schemas.simulation_models import SimulationJob, SimulationResult
from simulation_execution.schemas.enums import JobStatus

logger = logging.getLogger(__name__)

class SolverError(Exception):
    pass

class BaseSolverAdapter:
    """Abstract base for all solver adapters. Subclasses implement prepare_input,
    execute, and parse_results for their specific solver."""
    
    solver_name: str = "BASE"
    executable: str = ""
    
    def __init__(self, working_base: str = "/tmp/sim_work"):
        self.working_base = Path(working_base)
        self.working_base.mkdir(parents=True, exist_ok=True)
        
    def prepare_input(self, job: SimulationJob) -> Path:
        """Generate solver-specific input files. Returns working directory."""
        raise NotImplementedError
        
    def execute(self, work_dir: Path, config: Dict) -> Dict:
        """Run the solver subprocess. Returns execution metadata."""
        raise NotImplementedError
        
    def parse_results(self, work_dir: Path) -> SimulationResult:
        """Parse solver output files into SimulationResult."""
        raise NotImplementedError
        
    def run(self, job: SimulationJob) -> SimulationResult:
        """Full pipeline: prepare → execute → parse → cleanup."""
        work_dir = None
        start_time = time.time()
        try:
            work_dir = self.prepare_input(job)
            exec_meta = self.execute(work_dir, job.solver_config.model_dump())  # Use model_dump() for pydantic v2
            result = self.parse_results(work_dir)
            result.job_id = job.id
            result.status = JobStatus.COMPLETED
            result.execution_time_s = time.time() - start_time
            result.peak_memory_mb = exec_meta.get("peak_memory_mb", 0)
            return result
        except Exception as e:
            logger.exception(f"Solver {self.solver_name} failed for job {job.id}")
            return SimulationResult(
                job_id=job.id,
                status=JobStatus.FAILED,
                error_message=str(e),
                execution_time_s=time.time() - start_time
            )
        finally:
            # Cleanup work dir unless debugging
            if work_dir and os.environ.get("SIM_KEEP_WORKDIR") != "1":
                shutil.rmtree(work_dir, ignore_errors=True)
                
    def _run_subprocess(self, cmd: list, work_dir: Path, timeout: int) -> Dict:
        """Run a subprocess with resource limits and timeout."""
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if proc.returncode != 0:
                raise SolverError(f"Solver exited with code {proc.returncode}: {proc.stderr[:500]}")
            return {
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "peak_memory_mb": 0  # Would use resource.getrusage in production
            }
        except subprocess.TimeoutExpired:
            raise SolverError(f"Solver timed out after {timeout}s")
