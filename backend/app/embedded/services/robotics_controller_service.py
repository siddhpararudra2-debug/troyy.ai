"""
Robotics Controller Service
"""
import uuid
import time
from datetime import datetime
from app.embedded.schemas.schemas import (
    RoboticsControllerRequest,
    RoboticsControllerResponse
)


class RoboticsControllerService:
    @staticmethod
    def generate(request: RoboticsControllerRequest) -> RoboticsControllerResponse:
        start_time = time.time()
        kinematics_tasks = [{"name": "Forward Kinematics"}]
        motion_planning_tasks = [{"name": "Trajectory Generation"}]
        actuator_tasks = [{"name": "Joint Control"}]
        safety_tasks = [{"name": "Collision Detection"}]
        trajectory_controllers = [{"type": "PID"}]
        return RoboticsControllerResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            kinematics_tasks=kinematics_tasks,
            motion_planning_tasks=motion_planning_tasks,
            actuator_tasks=actuator_tasks,
            safety_tasks=safety_tasks,
            trajectory_controllers=trajectory_controllers,
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
