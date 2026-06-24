"""
Dependency Graph - Dependency analysis and impact propagation through the knowledge graph.

Capabilities:
- Dependency Mapping
- Impact Propagation
- Dependency Analysis
"""

from typing import Optional, List, Dict, Any, Set
from knowledge_graph.graph_builder import KnowledgeGraph


class DependencyGraph:
    """Analyzes dependencies in the engineering knowledge graph."""

    def __init__(self, knowledge_graph: KnowledgeGraph):
        self._graph = knowledge_graph
        self._dependency_cache: Dict[str, List[str]] = {}

    def find_dependents(self, node_id: str) -> List[str]:
        """Find all nodes that depend on the given node."""
        dependents = []
        visited: Set[str] = set()

        def _traverse(current: str):
            if current in visited:
                return
            visited.add(current)
            for node in self._graph.get_connected_nodes(current):
                if node.id != current and node.id not in visited:
                    dependents.append(node.id)
                    _traverse(node.id)

        _traverse(node_id)
        return dependents

    def impact_analysis(self, node_id: str) -> Dict[str, Any]:
        """Analyze the impact of changing a node."""
        dependents = self.find_dependents(node_id)
        node = self._graph._nodes.get(node_id)
        return {
            "target_node": node.to_dict() if node else node_id,
            "impacted_nodes_count": len(dependents),
            "impacted_nodes": [
                self._graph._nodes.get(nid).to_dict()
                for nid in dependents if nid in self._graph._nodes
            ],
        }

    def find_cycles(self) -> List[List[str]]:
        """Detect cyclic dependencies in the graph."""
        cycles = []
        visited: Set[str] = set()
        path: List[str] = []

        def _dfs(current: str):
            if current in path:
                cycle_start = path.index(current)
                cycles.append(path[cycle_start:])
                return
            if current in visited:
                return
            visited.add(current)
            path.append(current)
            for node in self._graph.get_connected_nodes(current):
                _dfs(node.id)
            path.pop()

        for node_id in self._graph._nodes:
            _dfs(node_id)

        return cycles