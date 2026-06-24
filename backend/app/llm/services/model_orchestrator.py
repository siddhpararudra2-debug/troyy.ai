"""
Model Orchestrator - main entrypoint for all LLM interactions.
"""
from typing import AsyncGenerator, Dict, Any, Literal
from app.llm.services.ollama_service import OllamaService
from app.llm.services.routing_service import RoutingService
from app.llm.schemas.schemas import ChatMessage, ChatResponse


class ModelOrchestrator:
    """Orchestrates all LLM interactions, handling routing, fallbacks, etc."""

    def __init__(self) -> None:
        self.ollama_service = OllamaService()
        self.routing_service = RoutingService(self.ollama_service)

    async def chat(
        self,
        messages: list[ChatMessage],
        model_type: Literal["coding", "engineering", "reasoning"] = "reasoning",
        temperature: float = 0.7,
        max_tokens: int | None = None,
        stream: bool = True
    ) -> ChatResponse | AsyncGenerator[str, None]:
        """Main chat completion method."""
        routing_decision = await self.routing_service.get_model(model_type)

        if not routing_decision.fallback_available:
            raise Exception("No LLM models available")

        return await self.ollama_service.generate(
            routing_decision.selected_model,
            messages,
            temperature,
            max_tokens,
            stream
        )

    async def chat_sync(
        self,
        messages: list[ChatMessage],
        model_type: Literal["coding", "engineering", "reasoning"] = "reasoning",
        temperature: float = 0.7,
        max_tokens: int | None = None
    ) -> ChatResponse:
        """Synchronous chat completion (non-streaming)."""
        result = await self.chat(
            messages,
            model_type,
            temperature,
            max_tokens,
            stream=False
        )
        return ChatResponse(**result)  # type: ignore


# Singleton instance
model_orchestrator = ModelOrchestrator()
