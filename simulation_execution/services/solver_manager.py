from typing import Dict
from simulation_execution.solvers.base_solver import BaseSolverAdapter
from simulation_execution.solvers.calculix_adapter import CalculiXAdapter
from simulation_execution.solvers.openfoam_adapter import OpenFOAMAdapter
from simulation_execution.solvers.ngspice_adapter import NGSpiceAdapter
from simulation_execution.schemas.enums import SolverType

class SolverManager:
    """Registry and factory for solver adapters."""
    
    def __init__(self):
        self._adapters: Dict[SolverType, BaseSolverAdapter] = {
            SolverType.CALCULIX: CalculiXAdapter(),
            SolverType.OPENFOAM: OpenFOAMAdapter(),
            SolverType.NGSPICE: NGSpiceAdapter(),
        }
        
    def register(self, solver_type: SolverType, adapter: BaseSolverAdapter):
        self._adapters[solver_type] = adapter
        
    def get(self, solver_type: SolverType) -> BaseSolverAdapter:
        if solver_type not in self._adapters:
            raise ValueError(f"No adapter registered for solver {solver_type}")
        return self._adapters[solver_type]
        
    def list_solvers(self) -> list:
        return [{"type": t.value, "name": a.solver_name, "executable": a.executable}
                for t, a in self._adapters.items()]
