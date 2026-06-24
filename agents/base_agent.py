"""
Base agent class for the Engineering OS multi-agent framework.
Defines the interface and common functionality for all engineering agents.
"""
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class AgentContext:
    """Context passed to agents during task execution."""
    task_id: str
    project_id: str
    input_data: dict
    memory_context: str = ""
    knowledge_context: str = ""
    session_id: Optional[str] = None


@dataclass
class AgentResult:
    """Result from an agent's task execution."""
    task_id: str
    agent_type: str
    status: str  # success, failed, partial
    output: dict
    summary: str
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    model_used: Optional[str] = None


class BaseAgent(ABC):
    """
    Abstract base class for all engineering agents.
    Each agent specializes in a specific engineering domain.
    """

    def __init__(
        self,
        agent_type: str,
        name: str,
        description: str,
        model_orchestrator=None,
    ):
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.model = model_orchestrator
        self.capabilities: list[str] = []
        self._task_history: list[dict] = []

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute a task with the given context."""
        pass

    async def can_handle(self, task_type: str) -> bool:
        """Check if this agent can handle a task type."""
        return task_type in self.capabilities

    def get_capabilities(self) -> list[str]:
        """Get the list of agent capabilities."""
        return self.capabilities

    async def generate_response(
        self, prompt: str, system_prompt: str, temperature: float = 0.7
    ) -> str:
        """Generate a response using the model orchestrator."""
        if not self.model:
            return "Model orchestrator not available"
        
        try:
            result = await self.model.chat(
                message=prompt,
                temperature=temperature,
            )
            if hasattr(result, "content"):
                return result.content
            return str(result)
        except Exception as e:
            logger.error(f"Agent {self.name} generation error: {e}")
            return f"Error generating response: {str(e)}"