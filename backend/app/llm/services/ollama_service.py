"""
Ollama Service for local model interactions.
"""
import httpx
import time
from typing import Any, AsyncGenerator, List, Dict
from datetime import datetime
from app.core.config import settings
from app.llm.schemas.schemas import ChatMessage


class OllamaService:
    """Service to interact with local Ollama server."""

    def __init__(self) -> None:
        self.base_url = settings.OLLAMA_BASE_URL
        self.client = httpx.AsyncClient(timeout=settings.OLLAMA_REQUEST_TIMEOUT)

    async def is_model_available(self, model_name: str) -> tuple[bool, float]:
        """Check if a specific model is available and healthy."""
        start_time = time.time()
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            available_models = [m["name"] for m in data.get("models", [])]
            return model_name in available_models, (time.time() - start_time) * 1000
        except Exception:
            return False, (time.time() - start_time) * 1000

    async def generate(
        self,
        model_name: str,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        stream: bool = False
    ) -> Dict[str, Any] | AsyncGenerator[str, None]:
        """Generate chat completion with optional streaming."""
        request_data: Dict[str, Any] = {
            "model": model_name,
            "messages": [
                {"role": m.role, "content": m.content}
                for m in messages
            ],
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }
        if max_tokens:
            request_data["options"]["num_predict"] = max_tokens

        if stream:
            return self._generate_stream(model_name, request_data)
        else:
            return await self._generate_sync(model_name, request_data)

    async def _generate_sync(self, model_name: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate completion in sync (non-streaming) mode."""
        start_time = time.time()
        response = await self.client.post(
            f"{self.base_url}/api/chat",
            json=request_data
        )
        response.raise_for_status()
        data = response.json()
        return {
            "response": data["message"]["content"],
            "model_used": model_name,
            "response_time_ms": (time.time() - start_time) * 1000,
            "status": "completed"
        }

    async def _generate_stream(self, model_name: str, request_data: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Generate completion in streaming mode."""
        async with self.client.stream(
            "POST",
            f"{self.base_url}/api/chat",
            json=request_data
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    import json
                    try:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
                    except json.JSONDecodeError:
                        continue
