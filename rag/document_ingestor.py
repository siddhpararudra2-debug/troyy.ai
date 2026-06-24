"""
Document ingestion service for Engineering OS.
Handles PDF ingestion, chunking, and processing for RAG pipeline.
"""
import io
import logging
import uuid
from typing import Optional

import pypdf

logger = logging.getLogger(__name__)


class DocumentChunk:
    """A chunk of a document with metadata."""

    def __init__(
        self,
        content: str,
        chunk_index: int,
        title: str = "",
        source: str = "",
        document_id: str = "",
        asset_type: str = "text",
        tags: Optional[list[str]] = None,
    ):
        self.id = str(uuid.uuid4())
        self.content = content
        self.chunk_index = chunk_index
        self.title = title
        self.source = source
        self.document_id = document_id
        self.asset_type = asset_type
        self.tags = tags or []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "chunk_index": self.chunk_index,
            "title": self.title,
            "source": self.source,
            "document_id": self.document_id,
            "asset_type": self.asset_type,
            "tags": self.tags,
        }


class DocumentIngestor:
    """
    Ingests documents from various formats (PDF, text, markdown)
    and splits them into chunks for embedding and indexing.
    """

    CHUNK_SIZE = 500  # words per chunk
    CHUNK_OVERLAP = 50  # overlapping words between chunks

    async def ingest_pdf(self, file_content: bytes, filename: str) -> list[DocumentChunk]:
        """Ingest a PDF file and return document chunks."""
        chunks = []
        try:
            pdf_reader = pypdf.PdfReader(io.BytesIO(file_content))
            full_text = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text.strip():
                    full_text += f"\n\n[Page {page_num + 1}]\n{text}"
            
            chunks = self._chunk_text(
                full_text,
                title=filename,
                source=filename,
                document_id=str(uuid.uuid4()),
                asset_type="pdf",
            )
            logger.info(f"Ingested PDF '{filename}': {len(chunks)} chunks")
        except Exception as e:
            logger.error(f"Failed to ingest PDF '{filename}': {e}")
            raise
        return chunks

    async def ingest_text(
        self, text: str, title: str = "", source: str = ""
    ) -> list[DocumentChunk]:
        """Ingest plain text and return document chunks."""
        chunks = self._chunk_text(
            text,
            title=title,
            source=source,
            document_id=str(uuid.uuid4()),
            asset_type="text",
        )
        logger.info(f"Ingested text '{title}': {len(chunks)} chunks")
        return chunks

    async def ingest_markdown(
        self, markdown_content: str, title: str = "", source: str = ""
    ) -> list[DocumentChunk]:
        """Ingest markdown content and return document chunks."""
        chunks = self._chunk_text(
            markdown_content,
            title=title,
            source=source,
            document_id=str(uuid.uuid4()),
            asset_type="markdown",
            tags=["markdown"],
        )
        logger.info(f"Ingested markdown '{title}': {len(chunks)} chunks")
        return chunks

    def _chunk_text(
        self,
        text: str,
        title: str = "",
        source: str = "",
        document_id: str = "",
        asset_type: str = "text",
        tags: Optional[list[str]] = None,
    ) -> list[DocumentChunk]:
        """
        Split text into overlapping chunks for embedding.
        Uses word-level chunking with configurable size and overlap.
        """
        words = text.split()
        chunks = []
        
        if not words:
            return chunks
        
        # For short texts, return as single chunk
        if len(words) <= self.CHUNK_SIZE:
            chunks.append(DocumentChunk(
                content=text,
                chunk_index=0,
                title=title,
                source=source,
                document_id=document_id,
                asset_type=asset_type,
                tags=tags,
            ))
            return chunks
        
        start = 0
        chunk_index = 0
        
        while start < len(words):
            end = min(start + self.CHUNK_SIZE, len(words))
            chunk_text = " ".join(words[start:end])
            
            chunks.append(DocumentChunk(
                content=chunk_text,
                chunk_index=chunk_index,
                title=f"{title} (part {chunk_index + 1})",
                source=source,
                document_id=document_id,
                asset_type=asset_type,
                tags=tags,
            ))
            
            chunk_index += 1
            start = end - self.CHUNK_OVERLAP
        
        return chunks