"""
Master Orchestrator for Engineering OS Multi-Agent System
Coordinates all engineering agents, manages workflows, and handles task distribution.
"""
import uuid
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from agents.agent_runtime import AgentRuntime
from app.agent_core.workflow_planner import WorkflowPlanner
from app.agent_core.task_allocator import TaskAllocator
from app.agent_core.execution_monitor import ExecutionMonitor
from app.knowledge_graph.graph_engine import GraphEngine

logger = logging.getLogger(__name__)


class MasterOrchestrator:
    """
    Central orchestrator for all engineering agents and workflows.
    Handles task decomposition, dependency resolution, and overall process coordination.
    """

    def __init__(
        self,
        agent_runtime: AgentRuntime,
        workflow_planner: Optional[WorkflowPlanner] = None,
        task_allocator: Optional[TaskAllocator] = None,
        execution_monitor: Optional[ExecutionMonitor] = None,
        knowledge_graph: Optional[GraphEngine] = None,
    ):
        self.agent_runtime = agent_runtime
        self.workflow_planner = workflow_planner or WorkflowPlanner()
        self.task_allocator = task_allocator or TaskAllocator(agent_runtime)
        self.execution_monitor = execution_monitor or ExecutionMonitor()
        self.knowledge_graph = knowledge_graph

        self._workflows: Dict[str, Dict] = {}
        self._task_queue: List[Dict] = []

    async def execute_mission(
        self,
        mission_id: Optional[str] = None,
        requirements: str = "",
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a complete engineering mission from requirements to final deliverables.

        :param mission_id: Unique identifier for this mission (auto-generated if not provided)
        :param requirements: High-level requirements/description of the mission
        :param project_id: Associated project ID
        :return: Complete mission results including all deliverables
        """
        mission_id = mission_id or str(uuid.uuid4())
        logger.info(f"Starting engineering mission {mission_id}: {requirements[:100]}...")

        # Step 1: Plan the overall workflow
        workflow_plan = await self.workflow_planner.plan_workflow(
            requirements=requirements,
            project_id=project_id,
            mission_id=mission_id,
        )

        # Step 2: Decompose into tasks
        tasks = await self.workflow_planner.decompose_tasks(workflow_plan)

        # Step 3: Execute tasks in correct order
        execution_result = await self.execute_tasks(tasks, mission_id, project_id)

        # Step 4: Compile final deliverables
        deliverables = await self.compile_deliverables(execution_result, project_id)

        logger.info(f"Mission {mission_id} completed successfully")
        return {
            "mission_id": mission_id,
            "project_id": project_id,
            "status": "completed",
            "started_at": workflow_plan["started_at"],
            "completed_at": datetime.utcnow().isoformat(),
            "deliverables": deliverables,
            "execution_results": execution_result,
        }

    async def execute_tasks(
        self,
        tasks: List[Dict],
        mission_id: str,
        project_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a list of tasks in dependency order.
        """
        results = []
        for task in tasks:
            task_id = task["task_id"]
            logger.info(f"Executing task {task_id} ({task['task_type']})")
            try:
                # Allocate and execute task
                task_result = await self.task_allocator.allocate_and_execute(
                    task=task,
                    project_id=project_id,
                    mission_id=mission_id,
                )
                results.append(task_result)
                self.execution_monitor.record_task_completion(
                    task_id=task_id,
                    task_type=task["task_type"],
                    status="success",
                    result=task_result,
                )
                logger.info(f"Task {task_id} completed successfully")
            except Exception as e:
                self.execution_monitor.record_task_completion(
                    task_id=task_id,
                    task_type=task["task_type"],
                    status="failed",
                    error=str(e),
                )
                logger.error(f"Task {task_id} failed: {e}")
                raise
        return results

    async def compile_deliverables(
        self,
        execution_results: List[Dict],
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Compile final deliverables from task execution results.
        """
        deliverables = {
            "cad_models": [],
            "reports": [],
            "documentation": [],
            "simulation_results": [],
            "bill_of_materials": [],
        }
        for result in execution_results:
            if "output" in result:
                for key in deliverables:
                    if key in result["output"]:
                        if isinstance(result["output"][key], list):
                            deliverables[key].extend(result["output"][key])
                        else:
                            deliverables[key].append(result["output"][key])
        return deliverables
