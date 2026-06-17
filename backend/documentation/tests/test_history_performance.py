import pytest
import time
from documentation.services.project_history_service import ProjectHistoryService

class MockHistoryDB:
    def query(self, model):
        class MockQuery:
            def filter(self, *args): return self
            def order_by(self, *args): return self
            def limit(self, *args): return self
            def all(self): 
                # Simulate 50 history entries
                return [type('obj', (object,), {
                    'id': i, 'project_id': 'P-001', 'timestamp': '2026-06-16T10:00:00',
                    'event_type': 'UPDATE', 'details': {}, 'actor': 'SYSTEM'
                }) for i in range(50)]
        return MockQuery()

@pytest.mark.asyncio
async def test_history_retrieval_under_100ms():
    db = MockHistoryDB()
    service = ProjectHistoryService(db)
    
    start = time.perf_counter()
    history = service.get_timeline("P-001", limit=50)
    elapsed_ms = (time.perf_counter() - start) * 1000
    
    assert elapsed_ms < 100, f"History retrieval took {elapsed_ms}ms, exceeding 100ms target"
    assert len(history) == 50
