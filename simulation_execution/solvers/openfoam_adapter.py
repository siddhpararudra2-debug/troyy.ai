from pathlib import Path
from typing import Dict
from simulation_execution.solvers.base_solver import BaseSolverAdapter, SolverError
from simulation_execution.schemas.simulation_models import SimulationJob, SimulationResult
from simulation_execution.schemas.enums import JobStatus, TurbulenceModel
import re

class OpenFOAMAdapter(BaseSolverAdapter):
    """Adapter for OpenFOAM CFD solver."""
    solver_name = "OpenFOAM"
    executable = "simpleFoam"  # Steady-state incompressible
    
    def prepare_input(self, job: SimulationJob) -> Path:
        work_dir = self.working_base / f"foam_{job.id}"
        work_dir.mkdir(parents=True, exist_ok=True)
        
        # Create OpenFOAM case structure
        (work_dir / "system").mkdir(exist_ok=True)
        (work_dir / "constant").mkdir(exist_ok=True)
        (work_dir / "0").mkdir(exist_ok=True)
        
        # Generate controlDict
        self._write_control_dict(work_dir, job)
        # Generate fvSchemes, fvSolution
        self._write_fv_schemes(work_dir, job)
        self._write_fv_solution(work_dir, job)
        # Generate turbulenceProperties
        self._write_turbulence_props(work_dir, job)
        # Generate initial/boundary conditions
        self._write_initial_conditions(work_dir, job)
        
        return work_dir
        
    def _write_control_dict(self, work_dir: Path, job: SimulationJob):
        content = f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      controlDict;
}}
application     {self.executable};
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         1000;
deltaT          1;
writeControl    timeStep;
writeInterval   100;
purgeWrite      0;
writeFormat     ascii;
writePrecision  6;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable true;
"""
        (work_dir / "system" / "controlDict").write_text(content)
        
    def _write_fv_schemes(self, work_dir: Path, job: SimulationJob):
        content = """FoamFile { version 2.0; format ascii; class dictionary; location "system"; object fvSchemes; }
ddtSchemes { default steadyState; }
gradSchemes { default cellLimited Gauss linear 1; }
divSchemes { default none; div(phi,U) bounded Gauss linearUpwind grad(U); div(phi,k) bounded Gauss upwind; div(phi,epsilon) bounded Gauss upwind; div(phi,omega) bounded Gauss upwind; div((nuEff*dev2(T(grad(U))))) Gauss linear; }
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes { default corrected; }
"""
        (work_dir / "system" / "fvSchemes").write_text(content)
        
    def _write_fv_solution(self, work_dir: Path, job: SimulationJob):
        content = """FoamFile { version 2.0; format ascii; class dictionary; location "system"; object fvSolution; }
solvers { p { solver GAMG; tolerance 1e-06; relTol 0.1; smoother DICGaussSeidel; } "(U|k|epsilon|omega)" { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-08; relTol 0.1; }; }
PISO { nCorrectors 2; nNonOrthogonalCorrectors 0; pRefCell 0; pRefValue 0; }
relaxationFactors { equations { U 0.7; k 0.7; epsilon 0.7; omega 0.7; } }
"""
        (work_dir / "system" / "fvSolution").write_text(content)
        
    def _write_turbulence_props(self, work_dir: Path, job: SimulationJob):
        # Determine turbulence model from boundary conditions or default
        turb_model = "kOmegaSST"  # Default robust model
        for bc in job.boundary_conditions:
            if bc.bc_type == "TURBULENCE_MODEL":
                turb_model = bc.values.get("model", "kOmegaSST")
                
        content = f"""FoamFile {{ version 2.0; format ascii; class dictionary; location "constant"; object turbulenceProperties; }}
simulationType RANS;
RAS
{{
    RASModel        {turb_model};
    turbulence      on;
    printCoeffs     on;
}}
"""
        (work_dir / "constant" / "turbulenceProperties").write_text(content)
        
    def _write_initial_conditions(self, work_dir: Path, job: SimulationJob):
        # Placeholder U, p, k, epsilon fields
        for field in ["U", "p", "k", "epsilon"]:
            (work_dir / "0" / field).write_text(f"// {field} initial conditions placeholder\n")
            
    def execute(self, work_dir: Path, config: Dict) -> Dict:
        # Run blockMesh, then solver
        cmds = [
            ["blockMesh"],
            [self.executable, "-parallel"] if config.get("cores", 1) > 1 else [self.executable]
        ]
        meta = {"returncode": 0, "stdout": "", "stderr": "", "peak_memory_mb": 0}
        for cmd in cmds:
            result = self._run_subprocess(cmd, work_dir, config.get("timeout_seconds", 3600))
            meta["stdout"] += result["stdout"]
            meta["stderr"] += result["stderr"]
        return meta
        
    def parse_results(self, work_dir: Path) -> SimulationResult:
        log_file = work_dir / "log.simpleFoam"
        convergence = []
        if log_file.exists():
            content = log_file.read_text()
            # Parse residual convergence
            for line in content.split("\n"):
                if "Solving for Ux" in line or "Solving for p" in line:
                    match = re.search(r"Initial residual = ([\d.E+-]+)", line)
                    if match:
                        convergence.append(float(match.group(1)))
                        
        return SimulationResult(
            job_id="",
            status=JobStatus.COMPLETED,
            convergence_data=convergence,
            result_files=[str(f) for f in work_dir.rglob("*") if f.is_file()]
        )
