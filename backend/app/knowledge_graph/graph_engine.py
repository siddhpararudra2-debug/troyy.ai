"""
Graph Engine for Engineering Knowledge Graph
Manages the knowledge graph nodes and edges.
"""
import uuid
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class GraphEngine:
    """
    Core engine for engineering knowledge graph operations:
    - Add nodes and edges
    - Query graph
    - Traverse relationships
    """

    def __init__(self):
        self._nodes: Dict[str, Dict[str, Any]] = {}  # node_id -> node data
        self._edges: Dict[str, Dict[str, Any]] = {}  # edge_id -> edge data
        self._adjacency: Dict[str, List[str]] = {}    # node_id -> list of connected node ids

    async def add_node(
        self,
        node_type: str,
        data: Dict[str, Any],
        node_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Add a node to the knowledge graph.
        """
        node_id = node_id or str(uuid.uuid4())
        node = {
            "node_id": node_id,
            "type": node_type,
            "data": data,
        }
        self._nodes[node_id] = node
        self._adjacency[node_id] = []
        logger.info(f"Added node: {node_type} ({node_id})")
        return node

    async def add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Add an edge between two nodes.
        """
        edge_id = str(uuid.uuid4())
        edge = {
            "edge_id": edge_id,
            "source": source_id,
            "target": target_id,
            "type": relationship_type,
            "data": data or {},
        }
        self._edges[edge_id] = edge
        self._adjacency[source_id].append(edge_id)
        self._adjacency[target_id].append(edge_id)
        logger.info(f"Added edge: {relationship_type} ({source_id} → {target_id})")
        return edge

    def get_node(self, node_id: str) -> Optional[Dict]:
        return self._nodes.get(node_id)

    def query_nodes(self, node_type: Optional[str] = None) -> List[Dict]:
        if node_type:
            return [node for node in self._nodes.values() if node["type"] == node_type]
        return list(self._nodes.values())
