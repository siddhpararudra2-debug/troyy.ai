"""
Graph Builder - Builds system knowledge graphs connecting all engineering artifacts.

Capabilities:
- Knowledge Graph Construction
- Multi-domain Entity Connection
- Relationship Mapping
"""

import uuid
from typing import Optional, List, Dict, Any, Set
from datetime import datetime


class GraphNode:
    """A node in the knowledge graph."""

    def __init__(self, node_id: str, name: str, node_type: str,
                 domain: str = "general", description: Optional[str] = None):
        self.id = node_id
        self.name = name
        self.node_type = node_type
        self.domain = domain
        self.description = description
        self.properties: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "type": self.node_type,
                "domain": self.domain, "description": self.description,
                "properties": self.properties, "metadata": self.metadata}


class GraphEdge:
    """An edge connecting nodes in the knowledge graph."""

    def __init__(self, edge_id: str, source_id: str, target_id: str,
                 relation: str, weight: float = 1.0):
        self.id = edge_id
        self.source_id = source_id
        self.target_id = target_id
        self.relation = relation
        self.weight = weight
        self.properties: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "source": self.source_id, "target": self.target_id,
                "relation": self.relation, "weight": self.weight, "properties": self.properties}


class KnowledgeGraph:
    """A knowledge graph connecting engineering artifacts."""

    def __init__(self):
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: Dict[str, GraphEdge] = {}

    def add_node(self, name: str, node_type: str, domain: str = "general",
                 description: Optional[str] = None) -> GraphNode:
        node_id = str(uuid.uuid4())
        node = GraphNode(node_id, name, node_type, domain, description)
        self._nodes[node_id] = node
        return node

    def add_edge(self, source_id: str, target_id: str, relation: str,
                 weight: float = 1.0) -> Optional[GraphEdge]:
        if source_id not in self._nodes or target_id not in self._nodes:
            return None
        edge_id = str(uuid.uuid4())
        edge = GraphEdge(edge_id, source_id, target_id, relation, weight)
        self._edges[edge_id] = edge
        return edge

    def get_connected_nodes(self, node_id: str) -> List[GraphNode]:
        connected = set()
        for edge in self._edges.values():
            if edge.source_id == node_id:
                connected.add(edge.target_id)
            if edge.target_id == node_id:
                connected.add(edge.source_id)
        return [self._nodes[nid] for nid in connected if nid in self._nodes]

    def find_path(self, from_id: str, to_id: str) -> List[Dict[str, Any]]:
        visited: Set[str] = set()
        queue = [(from_id, [from_id])]
        while queue:
            current, path = queue.pop(0)
            if current == to_id:
                return [{"node": self._nodes[nid].to_dict() if nid in self._nodes else None} for nid in path]
            if current in visited:
                continue
            visited.add(current)
            for edge in self._edges.values():
                if edge.source_id == current and edge.target_id not in visited:
                    queue.append((edge.target_id, path + [edge.target_id]))
                if edge.target_id == current and edge.source_id not in visited:
                    queue.append((edge.source_id, path + [edge.source_id]))
        return []

    def export_graph(self) -> Dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self._nodes.values()],
            "edges": [e.to_dict() for e in self._edges.values()],
            "stats": {"nodes": len(self._nodes), "edges": len(self._edges)},
        }


class GraphBuilder:
    """Builds knowledge graphs connecting engineering artifacts."""

    def __init__(self):
        self.graph = KnowledgeGraph()

    def connect_domains(self, domains: Dict[str, List[Dict[str, Any]]]):
        """Connect entities from multiple domains into a unified graph."""
        for domain, entities in domains.items():
            for entity in entities:
                node = self.graph.add_node(
                    name=entity.get("name", "Unknown"),
                    node_type=entity.get("type", "artifact"),
                    domain=domain,
                    description=entity.get("description"),
                )
                node.properties = entity.get("properties", {})

        # Create cross-domain traceability edges
        req_nodes = [n for n in self.graph._nodes.values() if n.domain == "requirements"]
        arch_nodes = [n for n in self.graph._nodes.values() if n.domain == "architecture"]
        for rn in req_nodes:
            for an in arch_nodes:
                if rn.name.lower() in an.name.lower() or an.name.lower() in rn.name.lower():
                    self.graph.add_edge(rn.id, an.id, "traces_to")

    def get_graph(self) -> KnowledgeGraph:
        return self.graph