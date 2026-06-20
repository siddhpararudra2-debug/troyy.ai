"""
Task Scheduler Service
"""
import uuid
import time
from datetime import datetime
from app.embedded.schemas.schemas import (
    TaskSchedulingRequest,
    TaskSchedulingResponse
)


class TaskSchedulerService:
    @staticmethod
    def generate(request: TaskSchedulingRequest) -> TaskSchedulingResponse:
        start_time = time.time()
        execution_plan = [
            {"task": "1ms Task", "start_time": 0, "duration": 0.1},
            {"task": "10ms Task", "start_time": 1, "duration": 0.5},
            {"task": "100ms Task", "start_time": 10, "duration": 2},
        ]
        cpu_utilization = {"max": 70, "average": 50}
        priorities = {"Idle": 0, "1ms": 1, "10ms": 2, "100ms":3}
        timing_analysis = {"1ms": {"jitter": 0.01}}
        wcet_analysis = {"1ms": 0.1, "10ms": 0.5}
        return TaskSchedulingResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            execution_plan=execution_plan,
            cpu_utilization=cpu_utilization,
            priorities=priorities,
            timing_analysis=timing_analysis,
            wcet_analysis=wcet_analysis,
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
