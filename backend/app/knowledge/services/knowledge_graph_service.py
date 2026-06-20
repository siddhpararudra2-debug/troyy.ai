"""
Knowledge Graph Service
"""
import uuid
import time
import json
from datetime import datetime
from app.knowledge.schemas.schemas import (
    KnowledgeNodeRequest,
    KnowledgeNodeResponse,
    KnowledgeRelationshipRequest,
    KnowledgeRelationshipResponse,
    KnowledgeGraphResponse
)


class KnowledgeGraphService:
    @staticmethod
    def create_node(request: KnowledgeNodeRequest) -> KnowledgeNodeResponse:
        return KnowledgeNodeResponse(
            id=str(uuid.uuid4()),
            node_type=request.node_type,
            name=request.name,
            properties=request.properties,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    @staticmethod
    def create_relationship(request: KnowledgeRelationshipRequest) -> KnowledgeRelationshipResponse:
        return KnowledgeRelationshipResponse(
            id=str(uuid.uuid4()),
            source_node_id=request.source_node_id,
            target_node_id=request.target_node_id,
            relationship_type=request.relationship_type,
            properties=request.properties,
            created_at=datetime.utcnow()
        )

    @staticmethod
    def get_graph(project_id: str) -> KnowledgeGraphResponse:
        start_time = time.time()
        motor_node = KnowledgeGraphService.create_node(KnowledgeNodeRequest(
            project_id=project_id,
            node_type="component",
            name="Drone Motor",
            properties={"part_number": "MTR-2212"}
        ))
        battery_node = KnowledgeGraphService.create_node(KnowledgeNodeRequest(
            project_id=project_id,
            node_type="component",
            name="Drone Battery",
            properties={"capacity": "5000mAh"}
        ))
        drone_node = KnowledgeGraphService.create_node(KnowledgeNodeRequest(
            project_id=project_id,
            node_type="system",
            name="Quadcopter Drone",
            properties={"weight": "1.2kg"}
        ))
        rel1 = KnowledgeGraphService.create_relationship(KnowledgeRelationshipRequest(
            project_id=project_id,
            source_node_id=motor_node.id,
            target_node_id=drone_node.id,
            relationship_type="powers",
            properties={}
        ))
        rel2 = KnowledgeGraphService.create_relationship(KnowledgeRelationshipRequest(
            project_id=project_id,
            source_node_id=battery_node.id,
            target_node_id=motor_node.id,
            relationship_type="supplies",
            properties={}
        ))
        return KnowledgeGraphResponse(
            id=str(uuid.uuid4()),
            project_id=project_id,
            nodes=[motor_node, battery_node, drone_node],
            relationships=[rel1, rel2],
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow()
        )
