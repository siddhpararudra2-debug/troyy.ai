"""
LLM Routes.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.llm.schemas.schemas import (
    ChatRequest,
    ChatResponse,
    HealthCheckResponse
)
from app.llm.services.model_orchestrator import model_orchestrator
from app.llm.services.health_service import HealthService
from app.llm.services.ollama_service import OllamaService

router = APIRouter(prefix="/llm", tags=["LLM / Local AI"])
health_service = HealthService(OllamaService())


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Non-streaming chat completion."""
    try:
        return await model_orchestrator.chat_sync(
            request.messages,
            request.model_type,
            request.temperature,
            request.max_tokens
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat completion."""
    try:
        response_generator = await model_orchestrator.chat(
            request.messages,
            request.model_type,
            request.temperature,
            request.max_tokens,
            stream=True
        )
        return StreamingResponse(
            response_generator,
            media_type="text/plain"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check for all local AI models."""
    try:
        return await health_service.check_health()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
