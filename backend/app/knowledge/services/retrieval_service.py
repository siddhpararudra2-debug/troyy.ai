"""
Retrieval Service for RAG.
"""
from typing import List, Dict, Any
from app.knowledge.services.vector_store import vector_store_service


class RetrievalService:
    """Service for retrieving relevant knowledge from vector store."""

    def __init__(self) -> None:
        self.vector_store = vector_store_service

    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Dict[str, Any] | None = None
    ) -> List[Dict[str, Any]]:
        """Search for relevant documents."""
        # Base search from Qdrant
        results = await self.vector_store.search(query, limit)
        # Apply filters if provided
        if filters:
            filtered_results = []
            for result in results:
                match = True
                for key, value in filters.items():
                    if result["payload"].get(key) != value:
                        match = False
                        break
                if match:
                    filtered_results.append(result)
            results = filtered_results
        return results

    async def get_context_pack(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get a formatted context pack for LLM."""
        results = await self.search(query, limit)
        return [
            {
                "type": "knowledge",
                "content": r["payload"].get("chunk_text", ""),
                "metadata": r["payload"]
            }
            for r in results
        ]


# Singleton instance
retrieval_service = RetrievalService()
