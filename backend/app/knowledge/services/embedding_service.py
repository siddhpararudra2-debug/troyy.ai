"""
Embedding Service for generating embeddings via Ollama.
"""
import httpx
from typing import List
from app.core.config import settings


class EmbeddingService:
    """Service to generate embeddings using Ollama."""

    def __init__(self) -> None:
        self.base_url = settings.OLLAMA_BASE_URL
        self.client = httpx.AsyncClient(timeout=settings.OLLAMA_REQUEST_TIMEOUT)
        self.embedding_model = settings.OLLAMA_MODEL_REASONING  # Use reasoning model for embeddings

    async def get_embedding(self, text: str) -> List[float]:
        """Generate a single embedding for given text."""
        response = await self.client.post(
            f"{self.base_url}/api/embeddings",
            json={
                "model": self.embedding_model,
                "prompt": text
            }
        )
        response.raise_for_status()
        data = response.json()
        return data["embedding"]

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        embeddings = []
        for text in texts:
            emb = await self.get_embedding(text)
            embeddings.append(emb)
        return embeddings


# Singleton instance
embedding_service = EmbeddingService()
