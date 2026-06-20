"""
RTOS Service
"""
import uuid
import time
from datetime import datetime
from app.embedded.schemas.schemas import (
    RTOSRequest,
    RTOSResponse,
    TaskDefinition
)


class RTOSService:
    @staticmethod
    def generate(request: RTOSRequest) -> RTOSResponse:
        start_time = time.time()
        tasks = [
            TaskDefinition(id="task-idle", name="Idle Task", priority=0, stack_size=512),
            TaskDefinition(id="task-1ms", name="1ms Task", priority=1, stack_size=1024, period_ms=1),
            TaskDefinition(id="task-10ms", name="10ms Task", priority=2, stack_size=1024, period_ms=10),
            TaskDefinition(id="task-100ms", name="100ms Task", priority=3, stack_size=1024, period_ms=100),
            TaskDefinition(id="task-1s", name="1s Task", priority=4, stack_size=1024, period_ms=1000),
        ]
        queues = [
            {"name": "sensor_queue", "size": 64, "item_size": 16}
        ]
        semaphores = [
            {"name": "sensor_sem", "count": 1}
        ]
        mutexes = [
            {"name": "data_mutex", "recursive": False}
        ]
        timers = [
            {"name": "led_timer", "period_ms": 500, "type": "repeated"}
        ]
        watchdogs = [
            {"name": "system_wdg", "timeout_ms": 1000}
        ]
        return RTOSResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            rtos_type=request.rtos_type,
            tasks=tasks,
            queues=queues,
            semaphores=semaphores,
            mutexes=mutexes,
            timers=timers,
            watchdogs=watchdogs,
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
