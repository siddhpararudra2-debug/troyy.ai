"""
Model Orchestrator - Central coordination for local AI model inference.
Integrates Ollama, routing, health monitoring, and session management.
"""
import asyncio
import logging
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import AsyncGenerator, Optional

from models.ollama_service import OllamaService
from models.routing_service import RoutingService, TaskType
from models.health_service import HealthService

logger = logging.getLogger(__name__)


@dataclass
class SessionContext:
    """Session context for conversation tracking."""
    session_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    messages: list[dict] = field(default_factory=list)
    context: Optional[list[int]] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class InferenceResult:
    """Result of a model inference."""
    content: str
    model_used: str
    task_type: TaskType
    response_time: float
    session_id: str
    finished: bool = True


class ModelOrchestrator:
    """
    Central orchestrator for local AI model inference.
    Manages model selection, routing, sessions, and health monitoring.
    """

    def __init__(self):
        self.ollama = OllamaService()
        self.routing = RoutingService()
        self.health = HealthService()
        self._sessions: dict[str, SessionContext] = {}
        self._lock = asyncio.Lock()

    async def initialize(self):
        """Initialize the orchestrator and check available models."""
        available = await self.ollama.is_available()
        self.health.update_infrastructure_health(ollama=available)
        
        if available:
            models = await self.ollama.list_models()
            for model_info in models:
                model_name = model_info.get("name", model_info.get("model", ""))
                self.routing.update_model_health(model_name, True)
                self.health.set_availability(model_name, True)
                logger.info(f"Model available: {model_name}")
        else:
            logger.warning("Ollama not available. Models will not function.")

    async def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        task_type: Optional[TaskType] = None,
        stream: bool = False,
        temperature: float = 0.7,
    ) -> InferenceResult | AsyncGenerator[str, None]:
        """
        Process a chat message through the appropriate model.
        Returns either a complete result or a stream of tokens.
        """
        # Get or create session
        session = await self._get_or_create_session(session_id)
        
        # Classify task if not specified
        if task_type is None:
            task_type = self.routing.classify_task(message)
        
        # Select model
        model_name, system_prompt = self.routing.select_model(task_type)
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add recent context (last 10 messages)
        context_messages = session.messages[-10:] if session.messages else []
        messages.extend(context_messages)
        messages.append({"role": "user", "content": message})
        
        # Track session
        session.messages.append({"role": "user", "content": message})
        
        if stream:
            return self._stream_response(
                model_name, messages, task_type, session, temperature
            )
        
        # Non-streaming inference
        start_time = time.time()
        try:
            response = await self.ollama.chat(
                model=model_name,
                messages=messages,
                stream=False,
                temperature=temperature,
            )
            
            elapsed = time.time() - start_time
            content = response.get("message", {}).get("content", "")
            
            # Record success
            self.health.record_success(model_name, elapsed)
            
            # Store response in session
            session.messages.append({"role": "assistant", "content": content})
            
            return InferenceResult(
                content=content,
                model_used=model_name,
                task_type=task_type,
                response_time=elapsed,
                session_id=session.session_id,
            )
        except Exception as e:
            elapsed = time.time() - start_time
            self.health.record_error(model_name)
            logger.error(f"Inference error on {model_name}: {e}")
            raise

    async def _stream_response(
        self,
        model_name: str,
        messages: list[dict],
        task_type: TaskType,
        session: SessionContext,
        temperature: float,
    ) -> AsyncGenerator[str, None]:
        """Stream a response token by token."""
        start_time = time.time()
        full_content = ""
        
        try:
            stream = await self.ollama.chat(
                model=model_name,
                messages=messages,
                stream=True,
                temperature=temperature,
            )
            
            async for token in stream:
                full_content += token
                yield token
            
            elapsed = time.time() - start_time
            self.health.record_success(model_name, elapsed)
            
            # Store response in session
            session.messages.append({"role": "assistant", "content": full_content})
        except Exception as e:
            elapsed = time.time() - start_time
            self.health.record_error(model_name)
            logger.error(f"Streaming error on {model_name}: {e}")
            raise

    async def create_session(self) -> SessionContext:
        """Create a new conversation session."""
        session = SessionContext(session_id=str(uuid.uuid4()))
        async with self._lock:
            self._sessions[session.session_id] = session
        return session

    async def get_session(self, session_id: str) -> Optional[SessionContext]:
        """Get an existing session."""
        async with self._lock:
            return self._sessions.get(session_id)

    async def _get_or_create_session(self, session_id: Optional[str]) -> SessionContext:
        """Get existing session or create new one."""
        if session_id:
            session = await self.get_session(session_id)
            if session:
                return session
        return await self.create_session()

    async def get_system_status(self) -> dict:
        """Get overall system status."""
        health = self.health.get_system_health()
        available_models = self.routing.get_available_models()
        active_sessions = len(self._sessions)
        
        return {
            "status": "healthy" if health.ollama_available else "degraded",
            "ollama_connected": health.ollama_available,
            "available_models": available_models,
            "active_sessions": active_sessions,
            "model_health": {
                name: {
                    "available": h.available,
                    "avg_response_time": round(h.avg_response_time, 2),
                    "total_requests": h.total_requests,
                    "error_count": h.error_count,
                }
                for name, h in health.models.items()
            },
            "last_updated": health.last_updated.isoformat() if health.last_updated else None,
        }

    async def shutdown(self):
        """Clean up resources."""
        await self.ollama.close()