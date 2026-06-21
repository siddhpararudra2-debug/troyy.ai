from pathlib import Path
from typing import Dict
from simulation_execution.solvers.base_solver import BaseSolverAdapter, SolverError
from simulation_execution.schemas.simulation_models import SimulationJob, SimulationResult
from simulation_execution.schemas.enums import JobStatus
import re

class NGSpiceAdapter(BaseSolverAdapter):
    """Adapter for NGSpice circuit simulator."""
    solver_name = "NGSpice"
    executable = "ngspice"
    
    def prepare_input(self, job: SimulationJob) -> Path:
        work_dir = self.working_base / f"spice_{job.id}"
        work_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate SPICE netlist
        netlist = self._generate_netlist(job)
        (work_dir / "circuit.spice").write_text(netlist)
        return work_dir
        
    def _generate_netlist(self, job: SimulationJob) -> str:
        """Generate SPICE netlist from job description.
        In production, this would come from schematic engine (Day 19)."""
        lines = ["* Auto-generated SPICE netlist", f"* Job: {job.id}"]
        
        # Parse boundary conditions as circuit elements
        for bc in job.boundary_conditions:
            if bc.bc_type == "VOLTAGE_SOURCE":
                lines.append(f"V{bc.name} {bc.values.get('pos_node', '1')} {bc.values.get('neg_node', '0')} DC {bc.values.get('voltage_v', 0)}")
            elif bc.bc_type == "RESISTOR":
                lines.append(f"R{bc.name} {bc.values.get('node_a', '1')} {bc.values.get('node_b', '2')} {bc.values.get('resistance_ohm', 1000)}")
            elif bc.bc_type == "CAPACITOR":
                lines.append(f"C{bc.name} {bc.values.get('node_a', '1')} {bc.values.get('node_b', '0')} {bc.values.get('capacitance_f', 1e-6)}")
                
        # Add analysis command
        lines.append(".tran 1u 10m")
        lines.append(".print tran v(1) v(2) i(V1)")
        lines.append(".end")
        
        return "\n".join(lines)
        
    def execute(self, work_dir: Path, config: Dict) -> Dict:
        cmd = [self.executable, "-b", "-o", "output.txt", "circuit.spice"]
        return self._run_subprocess(cmd, work_dir, config.get("timeout_seconds", 3600))
        
    def parse_results(self, work_dir: Path) -> SimulationResult:
        output_file = work_dir / "output.txt"
        waveforms = {}
        if output_file.exists():
            content = output_file.read_text()
            # Parse NGSpice output (simplified)
            headers = []
            for line in content.split("\n"):
                if line.startswith("Index"):
                    headers = line.split()
                elif line.strip() and not line.startswith("-") and headers:
                    values = line.split()
                    if len(values) == len(headers):
                        for i, h in enumerate(headers[1:], 1):
                            waveforms.setdefault(h, []).append(float(values[i]))
                            
        return SimulationResult(
            job_id="",
            status=JobStatus.COMPLETED,
            result_files=[str(output_file)],
            solver_output=str(waveforms)[:500]
        )
