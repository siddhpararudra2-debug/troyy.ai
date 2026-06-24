"""
Vector store service using Qdrant for semantic search.
Handles document indexing, search, and collection management.
"""
import logging
import uuid
from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import (
    CollectionStatus, Distance, VectorParams,
    PointStruct, Filter, FieldCondition, MatchValue,
    SearchParams, ScoredPoint,
)

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Vector store using Qdrant for embedding storage and semantic search.
    Manages collections, points, and search operations.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        grpc_port: int = 6334,
        prefer_grpc: bool = False,
    ):
        self.client = QdrantClient(
            host=host,
            port=port,
            grpc_port=grpc_port,
            prefer_grpc=prefer_grpc,
        )
        self._collections: dict[str, bool] = {}

    async def initialize(self):
        """Initialize vector store and ensure default collections exist."""
        collections = self.client.get_collections().collections
        existing = {c.name for c in collections}
        logger.info(f"Qdrant collections available: {existing}")

    async def ensure_collection(
        self,
        collection_name: str,
        vector_size: int = 4096,
        distance: Distance = Distance.COSINE,
    ):
        """Ensure a collection exists, creating it if necessary."""
        try:
            self.client.get_collection(collection_name)
            logger.debug(f"Collection {collection_name} already exists")
        except Exception:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance,
                ),
            )
            logger.info(f"Created collection: {collection_name}")

    async def index_document_chunks(
        self,
        collection_name: str,
        chunks: list[dict],
        embeddings: list[list[float]],
    ):
        """
        Index document chunks with their embeddings.
        
        Args:
            collection_name: Qdrant collection name
            chunks: List of chunk dicts with id, content, metadata
            embeddings: List of embedding vectors
        """
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = chunk.get("id", str(uuid.uuid4()))
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "content": chunk["content"],
                        "title": chunk.get("title", ""),
                        "source": chunk.get("source", ""),
                        "chunk_index": chunk.get("chunk_index", i),
                        "document_id": chunk.get("document_id", ""),
                        "asset_type": chunk.get("asset_type", "general"),
                        "tags": chunk.get("tags", []),
                    },
                )
            )

        self.client.upsert(
            collection_name=collection_name,
            points=points,
        )
        logger.info(f"Indexed {len(points)} chunks in {collection_name}")

    async def search(
        self,
        collection_name: str,
        query_vector: list[float],
        filter_dict: Optional[dict] = None,
        limit: int = 10,
        score_threshold: float = 0.5,
    ) -> list[dict]:
        """
        Search for similar vectors in the collection.
        
        Args:
            collection_name: Qdrant collection name
            query_vector: Query embedding vector
            filter_dict: Optional filter criteria
            limit: Max results
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results with content and metadata
        """
        query_filter = None
        if filter_dict:
            conditions = []
            for key, value in filter_dict.items():
                if isinstance(value, list):
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value),
                        )
                    )
                else:
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value),
                        )
                    )
            if conditions:
                query_filter = Filter(must=conditions)

        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=limit,
            score_threshold=score_threshold,
            search_params=SearchParams(
                hnsw_ef=128,
                exact=False,
            ),
        )

        return [
            {
                "id": str(r.id),
                "score": r.score,
                "content": r.payload.get("content", ""),
                "title": r.payload.get("title", ""),
                "source": r.payload.get("source", ""),
                "chunk_index": r.payload.get("chunk_index"),
                "document_id": r.payload.get("document_id"),
                "asset_type": r.payload.get("asset_type"),
                "tags": r.payload.get("tags", []),
            }
            for r in results
        ]

    async def hybrid_search(
        self,
        collection_name: str,
        query_vector: list[float],
        text_filter: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict]:
        """
        Perform hybrid search combining vector similarity with text filtering.
        
        Args:
            collection_name: Qdrant collection name
            query_vector: Query embedding vector
            text_filter: Optional text to filter by
            limit: Max results
            
        Returns:
            List of search results
        """
        query_filter = None
        if text_filter:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="content",
                        match=MatchValue(value=text_filter),
                    )
                ]
            )

        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=limit,
            score_threshold=0.3,
        )

        return [
            {
                "id": str(r.id),
                "score": r.score,
                "content": r.payload.get("content", ""),
                "title": r.payload.get("title", ""),
                "source": r.payload.get("source", ""),
                "asset_type": r.payload.get("asset_type"),
            }
            for r in results
        ]

    async def delete_collection(self, collection_name: str):
        """Delete a collection."""
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"Deleted collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to delete collection {collection_name}: {e}")

    async def get_collection_info(self, collection_name: str) -> dict:
        """Get information about a collection."""
        try:
            info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "status": info.status,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "config": {
                    "vector_size": info.config.params.vectors.size,
                    "distance": str(info.config.params.vectors.distance),
                },
            }
        except Exception as e:
            return {"name": collection_name, "error": str(e)}

    async def close(self):
        """Close the Qdrant client."""
        self.client.close()


# Collection names
COLLECTION_KNOWLEDGE = "engineering_knowledge"
COLLECTION_DOCUMENTS = "engineering_documents"
COLLECTION_MEMORIES = "engineering_memories"