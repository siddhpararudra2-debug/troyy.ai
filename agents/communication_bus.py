"""
Communication bus for inter-agent messaging in Engineering OS.
Provides publish/subscribe pattern for agent-to-agent communication.
"""
import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class AgentMessage:
    """Message sent between agents."""
    sender: str
    recipient: str
    message_type: str
    payload: dict
    message_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None


class CommunicationBus:
    """
    Publish/subscribe communication bus for inter-agent messaging.
    Agents can publish messages and subscribe to specific message types.
    """

    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = {}
        self._message_history: list[AgentMessage] = []
        self._lock = asyncio.Lock()
        self._max_history = 1000

    async def publish(self, message: AgentMessage):
        """Publish a message to all subscribers of its type."""
        async with self._lock:
            self._message_history.append(message)
            if len(self._message_history) > self._max_history:
                self._message_history = self._message_history[-self._max_history:]
        
        # Notify subscribers
        subscribers = self._subscribers.get(message.message_type, []) + \
                     self._subscribers.get("*", [])
        
        for callback in subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(message)
                else:
                    callback(message)
            except Exception as e:
                logger.error(f"Error in subscriber callback: {e}")

    def subscribe(self, message_type: str, callback: Callable):
        """Subscribe to a message type."""
        if message_type not in self._subscribers:
            self._subscribers[message_type] = []
        self._subscribers[message_type].append(callback)
        logger.debug(f"Subscribed to {message_type}")

    def unsubscribe(self, message_type: str, callback: Callable):
        """Unsubscribe from a message type."""
        if message_type in self._subscribers:
            self._subscribers[message_type].remove(callback)

    async def send_task_request(
        self, sender: str, recipient: str, task_data: dict, correlation_id: Optional[str] = None
    ):
        """Send a task request to a specific agent."""
        message = AgentMessage(
            sender=sender,
            recipient=recipient,
            message_type="task_request",
            payload=task_data,
            correlation_id=correlation_id,
        )
        await self.publish(message)

    async def send_task_result(
        self, sender: str, recipient: str, result_data: dict, correlation_id: str
    ):
        """Send task result back to requesting agent."""
        message = AgentMessage(
            sender=sender,
            recipient=recipient,
            message_type="task_result",
            payload=result_data,
            correlation_id=correlation_id,
        )
        await self.publish(message)

    async def send_query(
        self, sender: str, recipient: str, query: str, correlation_id: Optional[str] = None
    ):
        """Send a query to a specific agent."""
        message = AgentMessage(
            sender=sender,
            recipient=recipient,
            message_type="query",
            payload={"query": query},
            correlation_id=correlation_id,
        )
        await self.publish(message)

    async def get_history(
        self, message_type: Optional[str] = None, limit: int = 50
    ) -> list[AgentMessage]:
        """Get message history, optionally filtered by type."""
        if message_type:
            return [m for m in self._message_history[-limit:] if m.message_type == message_type]
        return self._message_history[-limit:]