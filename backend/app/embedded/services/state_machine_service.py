"""
State Machine Service
"""
import uuid
import time
from datetime import datetime
from app.embedded.schemas.schemas import (
    StateMachineRequest,
    StateMachineResponse
)


class StateMachineService:
    @staticmethod
    def generate(request: StateMachineRequest) -> StateMachineResponse:
        start_time = time.time()
        states = [
            {"id": "idle", "description": "Idle State"},
            {"id": "active", "description": "Active State"},
            {"id": "error", "description": "Error State"},
            {"id": "recovery", "description": "Recovery State"},
        ]
        transitions = [
            {"from": "idle", "to": "active", "trigger": "start_cmd"},
            {"from": "active", "to": "idle", "trigger": "stop_cmd"},
            {"from": "active", "to": "error", "trigger": "fault_detected"},
            {"from": "error", "to": "recovery", "trigger": "reset"},
        ]
        return StateMachineResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            states=states,
            transitions=transitions,
            conditions=[],
            actions=[],
            recovery_logic=[],
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
