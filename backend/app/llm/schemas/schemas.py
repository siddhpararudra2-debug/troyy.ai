"""
LLM Schemas for chat, routing, health, etc.
"""
from typing import Any, List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    name: Optional[str] = None
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model_type: Literal["coding", "engineering", "reasoning"] = "reasoning"
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = None
    stream: bool = True


class ChatResponse(BaseModel):
    response: str
    model_used: str
    response_time_ms: float
    status: str


class ModelHealth(BaseModel):
    name: str
    status: Literal["available", "unavailable"]
    response_time_ms: Optional[float] = None
    last_checked: datetime


class HealthCheckResponse(BaseModel):
    overall_status: Literal["healthy", "degraded", "unhealthy"]
    models: List[ModelHealth]
    timestamp: datetime


class RoutingDecision(BaseModel):
    requested_model_type: str
    selected_model: str
    fallback_available: bool
    reasoning: Optional[str] = None
