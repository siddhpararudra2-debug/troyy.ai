"""
Embedding service for Engineering OS.
Generates and manages embeddings using local Ollama models.
"""
import json
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating embeddings using local models.
    Uses Ollama's embedding API for local inference.
    """

    def __init__(self, ollama_base_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.ollama_url, timeout=30.0)
        return self._client

    async def generate_embedding(
        self, text: str, model: str = "qwen"
    ) -> list[float]:
        """Generate embedding vector for text using local model."""
        client = await self._get_client()
        payload = {"model": model, "prompt": text}
        response = await client.post("/api/embeddings", json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("embedding", [])

    async def generate_embeddings_batch(
        self, texts: list[str], model: str = "qwen"
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = []
        for text in texts:
            embedding = await self.generate_embedding(text, model)
            embeddings.append(embedding)
        return embeddings

    async def is_available(self) -> bool:
        """Check if embedding service is available."""
        try:
            client = await self._get_client()
            response = await client.get("/api/tags", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


class EmbeddingProvider:
    """
    Abstract embedding provider for different models.
    Allows switching between different embedding models.
    """

    def __init__(self, embedding_service: EmbeddingService, model: str = "qwen"):
        self.service = embedding_service
        self.model = model
        self.dimension = 4096  # qwen embedding dimension

    async def embed(self, text: str) -> list[float]:
        """Embed a single text."""
        return await self.service.generate_embedding(text, self.model)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts."""
        return await self.service.generate_embeddings_batch(texts, self.model)