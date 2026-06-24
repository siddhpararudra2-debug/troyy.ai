"""
Agent Registry for Engineering OS.
Manages agent registration, discovery, and capability lookup.
"""
import logging
from typing import Optional

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Registry for all available engineering agents.
    Provides agent discovery, capability lookup, and lifecycle management.
    """

    def __init__(self):
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent):
        """Register an agent in the registry."""
        self._agents[agent.agent_type] = agent
        logger.info(f"Registered agent: {agent.name} ({agent.agent_type})")

    def unregister(self, agent_type: str):
        """Unregister an agent."""
        if agent_type in self._agents:
            del self._agents[agent_type]
            logger.info(f"Unregistered agent: {agent_type}")

    def get_agent(self, agent_type: str) -> Optional[BaseAgent]:
        """Get an agent by type."""
        return self._agents.get(agent_type)

    def get_all_agents(self) -> dict[str, BaseAgent]:
        """Get all registered agents."""
        return self._agents.copy()

    def find_agent_for_task(self, task_type: str) -> Optional[BaseAgent]:
        """Find an agent that can handle a specific task type."""
        for agent in self._agents.values():
            if task_type in agent.capabilities:
                return agent
        return None

    def list_capabilities(self) -> dict[str, list[str]]:
        """List all capabilities grouped by agent."""
        return {
            agent_type: agent.get_capabilities()
            for agent_type, agent in self._agents.items()
        }

    def get_agent_types(self) -> list[str]:
        """Get list of all registered agent types."""
        return list(self._agents.keys())

    def count(self) -> int:
        """Get the number of registered agents."""
        return len(self._agents)