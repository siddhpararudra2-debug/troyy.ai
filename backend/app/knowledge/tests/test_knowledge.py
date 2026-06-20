"""
Knowledge Platform Unit Tests
"""
from app.knowledge.services.knowledge_graph_service import KnowledgeGraphService
from app.knowledge.schemas.schemas import KnowledgeNodeRequest


def test_knowledge_graph_node_creation():
    request = KnowledgeNodeRequest(
        project_id="test-project-123",
        node_type="component",
        name="Test Motor",
        properties={"voltage": 12}
    )
    result = KnowledgeGraphService.create_node(request)
    assert result.name == "Test Motor"
    assert result.node_type == "component"
