"""
RAG (Retrieval Augmented Generation) Service
"""
import time
from datetime import datetime
from app.knowledge.schemas.schemas import RAGRequest, RAGResponse
from app.knowledge.services.retrieval_service import retrieval_service
from app.knowledge.services.citation_service import citation_service


class RAGService:
    @staticmethod
    async def retrieve(request: RAGRequest) -> RAGResponse:
        start_time = time.time()
        # Get search results
        results = await retrieval_service.search(request.query, request.limit)
        # Format context pack
        context_pack = []
        for result in results:
            context_pack.append({
                "type": "knowledge",
                "content": result["payload"].get("chunk_text", ""),
                "metadata": result["payload"]
            })
        # Generate references
        references = citation_service.generate_references(results)

        return RAGResponse(
            query=request.query,
            context_pack=context_pack,
            references=references,
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
