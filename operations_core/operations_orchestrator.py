"""Operations Orchestrator - Module 10 for Sprint 13."""
from enum import Enum
import uuid
from typing import Dict, Any, Optional, List


class OperationPhase(Enum):
    PLANNING = "planning"
    SIMULATION = "simulation"
    REHEARSAL = "rehearsal"
    EXECUTION = "execution"
    MONITORING = "monitoring"
    ANALYTICS = "analytics"
    LESSONS_LEARNED = "lessons_learned"


class OperationsOrchestrator:
    def __init__(self):
        self.operations: Dict[str, Any] = {}

    def initiate_operation(
        self,
        operation_name: str,
        mission_id: str,
        participants: List[str]
    ) -> str:
        operation_id = str(uuid.uuid4())
        operation = {
            "id": operation_id,
            "name": operation_name,
            "mission_id": mission_id,
            "participants": participants,
            "phase": OperationPhase.PLANNING.value,
            "timeline": [],
        }
        self.operations[operation_id] = operation
        return operation_id

    def advance_phase(
        self,
        operation_id: str,
        next_phase: OperationPhase
    ) -> bool:
        if operation_id not in self.operations:
            return False
        self.operations[operation_id]["phase"] = next_phase.value
        return True

    def get_operation(self, operation_id: str) -> Optional[Any]:
        return self.operations.get(operation_id)

    def list_operations(self, phase: Optional[OperationPhase] = None) -> List[Any]:
        operations = list(self.operations.values())
        if phase:
            operations = [o for o in operations if o["phase"] == phase.value]
        return operations
