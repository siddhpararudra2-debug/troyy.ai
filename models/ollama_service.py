"""
Ollama service for local model inference.
Handles communication with locally running Ollama instances.
"""
import json
import logging
from typing import AsyncGenerator, Optional
import httpx

logger = logging.getLogger(__name__)


class OllamaService:
    """Service for interacting with local Ollama instance."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=120.0)
        return self._client

    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        context: Optional[list[int]] = None,
    ) -> dict | AsyncGenerator[str, None]:
        """Generate a response from the model."""
        client = await self._get_client()
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if system:
            payload["system"] = system
        if context:
            payload["context"] = context

        if stream:
            return self._stream_response(client, payload)
        
        response = await client.post("/api/generate", json=payload)
        response.raise_for_status()
        return response.json()

    async def _stream_response(
        self, client: httpx.AsyncClient, payload: dict
    ) -> AsyncGenerator[str, None]:
        """Stream response from Ollama."""
        async with client.stream("POST", "/api/generate", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    try:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            yield chunk["response"]
                        if chunk.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue

    async def chat(
        self,
        model: str,
        messages: list[dict],
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> dict | AsyncGenerator[str, None]:
        """Chat completion using Ollama."""
        client = await self._get_client()
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        if stream:
            return self._stream_chat(client, payload)
        
        response = await client.post("/api/chat", json=payload)
        response.raise_for_status()
        return response.json()

    async def _stream_chat(
        self, client: httpx.AsyncClient, payload: dict
    ) -> AsyncGenerator[str, None]:
        """Stream chat response from Ollama."""
        async with client.stream("POST", "/api/chat", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    try:
                        chunk = json.loads(line)
                        if "message" in chunk and "content" in chunk["message"]:
                            yield chunk["message"]["content"]
                        if chunk.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue

    async def list_models(self) -> list[dict]:
        """List available models in Ollama."""
        client = await self._get_client()
        response = await client.get("/api/tags")
        response.raise_for_status()
        data = response.json()
        return data.get("models", [])

    async def is_available(self) -> bool:
        """Check if Ollama service is running."""
        try:
            client = await self._get_client()
            response = await client.get("/api/tags", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False

    async def get_model_info(self, model: str) -> Optional[dict]:
        """Get information about a specific model."""
        models = await self.list_models()
        for m in models:
            if m.get("name") == model or m.get("model") == model:
                return m
        return None

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None