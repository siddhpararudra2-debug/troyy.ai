"""
Agent runtime for the Engineering OS multi-agent framework.
Manages agent lifecycle, execution, and resource allocation.
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from agents.agent_registry import AgentRegistry
from agents.task_manager import TaskManager
from agents.communication_bus import CommunicationBus

logger = logging.getLogger(__name__)


class AgentRuntime:
    """
    Runtime environment for engineering agents.
    Manages agent lifecycle, coordinates task execution, and monitors health.
    """

    def __init__(
        self,
        agent_registry: AgentRegistry,
        task_manager: TaskManager,
        communication_bus: CommunicationBus,
    ):
        self.registry = agent_registry
        self.task_manager = task_manager
        self.bus = communication_bus
        self._running = False
        self._tasks: dict[str, asyncio.Task] = {}

    async def start(self):
        """Start the agent runtime."""
        self._running = True
        logger.info(f"Agent runtime started with {self.registry.count()} agents")

    async def stop(self):
        """Stop the agent runtime."""
        self._running = False
        for task_id, task in self._tasks.items():
            task.cancel()
        self._tasks.clear()
        logger.info("Agent runtime stopped")

    async def submit_task(
        self,
        project_id: str,
        agent_type: str,
        title: str,
        description: str,
        input_data: dict,
        priority: int = 0,
    ) -> str:
        """Submit a task for asynchronous execution."""
        task = await self.task_manager.create_task(
            project_id=project_id,
            agent_type=agent_type,
            title=title,
            description=description,
            input_data=input_data,
            priority=priority,
        )
        
        # Start execution in background
        exec_task = asyncio.create_task(
            self.task_manager.execute_task(task.task_id)
        )
        self._tasks[task.task_id] = exec_task
        
        return task.task_id

    async def get_status(self) -> dict:
        """Get runtime status."""
        stats = await self.task_manager.get_statistics()
        return {
            "running": self._running,
            "agents": self.registry.count(),
            "agent_types": self.registry.get_agent_types(),
            "capabilities": self.registry.list_capabilities(),
            "tasks": stats,
        }