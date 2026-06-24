"""Task Allocator - Module 2 for Sprint 13."""
from enum import Enum
import uuid
from typing import List, Dict, Any, Tuple


class AllocationStrategy(Enum):
    GREEDY = "greedy"
    ROUND_ROBIN = "round_robin"
    MINIMIZE_DISTANCE = "minimize_distance"
    MAXIMIZE_EFFICIENCY = "maximize_efficiency"


class TaskAllocator:
    def __init__(self):
        self.tasks: Dict[str, Any] = {}

    def create_task(
        self,
        swarm_id: str,
        task_type: str,
        priority: int = 5,
        required_capabilities: Optional[List[str]] = None
    ) -> Any:
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "swarm_id": swarm_id,
            "task_type": task_type,
            "priority": priority,
            "required_capabilities": required_capabilities or [],
            "status": "pending",
            "assigned_agent": None,
        }
        self.tasks[task_id] = task
        return task

    def allocate_tasks(
        self,
        swarm_id: str,
        agents: List[Dict[str, Any]],
        strategy: AllocationStrategy = AllocationStrategy.GREEDY
    ) -> Tuple[bool, Dict[str, Any]]:
        allocation = {}
        swarm_tasks = [t for t in self.tasks.values() if t["swarm_id"] == swarm_id and t["status"] == "pending"]
        
        if strategy == AllocationStrategy.GREEDY:
            for task in swarm_tasks:
                for agent in agents:
                    if all(cap in agent.get("capabilities", []) for cap in task["required_capabilities"]):
                        task["status"] = "assigned"
                        task["assigned_agent"] = agent["id"]
                        allocation[task["id"]] = agent["id"]
                        break
        
        return True, allocation
