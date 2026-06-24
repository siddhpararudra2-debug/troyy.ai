"""
Document Ingestion Service for RAG.
"""
from typing import List, Dict, Any
from pathlib import Path
import PyPDF2
from datetime import datetime
from app.knowledge.services.vector_store import vector_store_service


class DocumentIngestor:
    """Service for ingesting and chunking documents."""

    def __init__(self) -> None:
        self.chunk_size = 1000
        self.chunk_overlap = 200

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks of specified size with overlap."""
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size
            if end > text_length:
                end = text_length
            chunk = text[start:end]
            chunks.append(chunk.strip())
            start += (self.chunk_size - self.chunk_overlap)

        return chunks

    async def ingest_text(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[str]:
        """Ingest raw text content, chunk and store in Qdrant."""
        chunks = self._chunk_text(text)
        metadatas = [
            {
                **metadata,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "chunk_text": chunk
            }
            for i, chunk in enumerate(chunks)
        ]

        return await vector_store_service.add_documents(chunks, metadatas)

    async def ingest_pdf(
        self,
        pdf_path: Path,
        metadata: Dict[str, Any]
    ) -> List[str]:
        """Ingest a PDF file, extract text, chunk and store in Qdrant."""
        text = ""
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""

        full_metadata = {
            **metadata,
            "file_name": pdf_path.name,
            "file_path": str(pdf_path),
            "file_type": "pdf",
            "ingested_at": datetime.utcnow().isoformat()
        }

        return await self.ingest_text(text, full_metadata)


# Singleton instance
document_ingestor = DocumentIngestor()
