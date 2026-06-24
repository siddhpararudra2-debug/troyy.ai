"""
Retrieval service for Engineering OS RAG pipeline.
Coordinates embedding, vector search, and result ranking.
"""
import logging
from typing import Optional

from rag.embedding_service import EmbeddingProvider, EmbeddingService
from rag.vector_store import VectorStore, COLLECTION_KNOWLEDGE, COLLECTION_DOCUMENTS
from rag.document_ingestor import DocumentChunk

logger = logging.getLogger(__name__)


class RetrievalService:
    """
    Coordinates document retrieval using embeddings and vector search.
    Provides unified interface for semantic search across knowledge sources.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_provider: EmbeddingProvider,
    ):
        self.vector_store = vector_store
        self.embedding = embedding_provider

    async def search_knowledge(
        self,
        query: str,
        collection: str = COLLECTION_KNOWLEDGE,
        filter_dict: Optional[dict] = None,
        limit: int = 10,
        score_threshold: float = 0.3,
    ) -> list[dict]:
        """
        Search knowledge base using semantic search.
        
        Args:
            query: Natural language query
            collection: Qdrant collection to search
            filter_dict: Optional metadata filters
            limit: Max results
            score_threshold: Minimum similarity score
        """
        # Generate query embedding
        query_vector = await self.embedding.embed(query)
        
        # Search vector store
        results = await self.vector_store.search(
            collection_name=collection,
            query_vector=query_vector,
            filter_dict=filter_dict,
            limit=limit,
            score_threshold=score_threshold,
        )
        
        return results

    async def search_documents(
        self,
        query: str,
        filter_dict: Optional[dict] = None,
        limit: int = 10,
    ) -> list[dict]:
        """Search indexed documents."""
        return await self.search_knowledge(
            query=query,
            collection=COLLECTION_DOCUMENTS,
            filter_dict=filter_dict,
            limit=limit,
        )

    async def index_chunks(
        self,
        chunks: list[DocumentChunk],
        collection: str = COLLECTION_KNOWLEDGE,
    ):
        """Index document chunks with embeddings."""
        # Generate embeddings for all chunks
        texts = [chunk.content for chunk in chunks]
        embeddings = await self.embedding.embed_batch(texts)
        
        # Index in vector store
        chunk_dicts = [chunk.to_dict() for chunk in chunks]
        await self.vector_store.index_document_chunks(
            collection_name=collection,
            chunks=chunk_dicts,
            embeddings=embeddings,
        )

    async def hybrid_search(
        self,
        query: str,
        text_filter: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict]:
        """
        Hybrid search combining semantic and keyword matching.
        """
        query_vector = await self.embedding.embed(query)
        
        return await self.vector_store.hybrid_search(
            collection_name=COLLECTION_KNOWLEDGE,
            query_vector=query_vector,
            text_filter=text_filter,
            limit=limit,
        )

    async def get_knowledge_context(
        self,
        query: str,
        max_results: int = 5,
        max_tokens: int = 2048,
    ) -> str:
        """
        Assemble a context string from knowledge base for AI prompts.
        """
        results = await self.search_knowledge(query=query, limit=max_results)
        
        if not results:
            return ""
        
        parts = ["### Knowledge Base Context\n"]
        token_estimate = 0
        
        for r in results:
            entry = f"\n**[Score: {r['score']:.2f}]** {r.get('title', 'Untitled')}"
            entry += f"\nSource: {r.get('source', 'Unknown')}\n"
            entry += f"{r['content'][:400]}...\n"
            
            entry_tokens = len(entry) // 4
            if token_estimate + entry_tokens > max_tokens:
                break
            
            parts.append(entry)
            token_estimate += entry_tokens
        
        return "\n".join(parts)