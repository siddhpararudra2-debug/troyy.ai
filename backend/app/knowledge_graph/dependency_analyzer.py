"""
Dependency Analyzer for Engineering Knowledge Graph
Analyzes dependencies between entities.
"""
import logging
from typing import Dict, Any, List, Set
from app.knowledge_graph.graph_engine import GraphEngine

logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    """
    Analyzes dependencies in the engineering knowledge graph:
    - Which parts depend on other parts
    - Which requirements depend on other requirements
    - Impact of changes
    """

    def __init__(self, graph_engine: GraphEngine):
        self.graph = graph_engine

    def find_dependencies(self, node_id: str) -> List[str]:
        """
        Find all dependencies (things that this node depends on).
        """
        dependencies = []
        # Find all edges FROM this node
        for edge_id in self.graph._adjacency.get(node_id, []):
            edge = self.graph._edges.get(edge_id)
            if edge and edge["source"] == node_id:
                dependencies.append(edge["target"])
        return dependencies

    def find_dependents(self, node_id: str) -> List[str]:
        """
        Find all dependents (things that depend on this node).
        """
        dependents = []
        for edge_id in self.graph._adjacency.get(node_id, []):
            edge = self.graph._edges.get(edge_id)
            if edge and edge["target"] == node_id:
                dependents.append(edge["source"])
        return dependents

    def find_all_dependencies_recursive(self, node_id: str) -> Set[str]:
        """
        Recursively find all dependencies of a node (transitive closure).
        """
        visited = set()
        stack = [node_id]
        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                for dep in self.find_dependencies(current):
                    if dep not in visited:
                        stack.append(dep)
        return visited - {node_id}
