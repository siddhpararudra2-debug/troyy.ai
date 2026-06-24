"""
Tests for the Project Memory System.
"""
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from memory.memory_storage import MemoryStorage
from memory.memory_retrieval import MemoryRetrieval, RetrievalResult
from memory.memory_service import MemoryService


class TestMemoryService:
    @pytest.mark.asyncio
    async def test_store_memory(self):
        mock_session = AsyncMock()
        service = MemoryService(mock_session)
        
        result = await service.store(
            project_id=uuid.uuid4(),
            memory_type="conversation",
            content="Test memory content",
            title="Test Memory",
            importance=0.8,
        )
        assert result["memory_type"] == "conversation"
        assert result["title"] == "Test Memory"

    @pytest.mark.asyncio
    async def test_search_memory(self):
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        service = MemoryService(mock_session)
        
        results = await service.search(
            query="test query",
            limit=10,
        )
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_store_conversation_memory(self):
        mock_session = AsyncMock()
        service = MemoryService(mock_session)
        
        result = await service.store_conversation_memory(
            project_id=uuid.uuid4(),
            user_message="Hello",
            assistant_response="Hi there!",
            model_used="qwen",
        )
        assert result["memory_type"] == "conversation"

    @pytest.mark.asyncio
    async def test_store_requirement(self):
        mock_session = AsyncMock()
        service = MemoryService(mock_session)
        
        result = await service.store_requirement(
            project_id=uuid.uuid4(),
            title="System shall be fast",
            description="The system must respond within 100ms",
        )
        assert result["memory_type"] == "requirement"

    @pytest.mark.asyncio
    async def test_get_project_summary(self):
        mock_session = AsyncMock()
        service = MemoryService(mock_session)
        
        summary = await service.get_project_summary(uuid.uuid4())
        assert isinstance(summary, dict)


class TestMemoryRetrieval:
    def test_calculate_relevance_title_match(self):
        from database.models import MemoryEntry
        mem = MagicMock(spec=MemoryEntry)
        mem.title = "Structural Analysis Report"
        mem.content = "This contains structural analysis results"
        mem.summary = None
        mem.tags = ["structural", "analysis"]
        mem.importance = 1.0
        
        retrieval = MemoryRetrieval.__new__(MemoryRetrieval)
        score = retrieval._calculate_relevance("structural", mem)
        assert score > 0.0
        assert score <= 1.0

    def test_calculate_relevance_no_match(self):
        from database.models import MemoryEntry
        mem = MagicMock(spec=MemoryEntry)
        mem.title = "Electronics Design"
        mem.content = "Circuit components and PCB layout"
        mem.summary = None
        mem.tags = ["electronics"]
        mem.importance = 0.5
        
        retrieval = MemoryRetrieval.__new__(MemoryRetrieval)
        score = retrieval._calculate_relevance("aerodynamics", mem)
        assert score == 0.0