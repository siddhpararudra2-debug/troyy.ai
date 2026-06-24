"""
Vector Store integration with Qdrant.
"""
import uuid
from typing import List, Dict, Any
from qdrant_client import AsyncQdrantClient, models
from app.core.config import settings
from app.knowledge.services.embedding_service import embedding_service


class VectorStoreService:
    """Service to interact with Qdrant vector store."""

    def __init__(self) -> None:
        self.client = AsyncQdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.vector_size = settings.QDRANT_VECTOR_SIZE

    async def ensure_collection(self) -> None:
        """Create the collection if it doesn't exist."""
        collections = await self.client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if self.collection_name not in collection_names:
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE
                )
            )

    async def add_documents(
        self,
        texts: List[str],
        metadata: List[Dict[str, Any]]
    ) -> List[str]:
        """Add documents to Qdrant."""
        await self.ensure_collection()

        embeddings = await embedding_service.get_embeddings(texts)
        ids = [str(uuid.uuid4()) for _ in texts]

        points = [
            models.PointStruct(
                id=point_id,
                vector=embedding,
                payload=meta
            )
            for point_id, embedding, meta in zip(ids, embeddings, metadata)
        ]

        await self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        return ids

    async def search(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for relevant documents in Qdrant."""
        await self.ensure_collection()

        query_embedding = await embedding_service.get_embedding(query)
        search_result = await self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=limit,
            with_payload=True
        )

        return [
            {
                "id": point.id,
                "score": point.score,
                "payload": point.payload
            }
            for point in search_result.points
        ]


# Singleton instance
vector_store_service = VectorStoreService()
