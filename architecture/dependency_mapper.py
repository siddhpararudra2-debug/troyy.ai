"""
Dependency Mapper - Maps and analyzes dependencies within the system architecture.

Capabilities:
- Dependency Analysis
- Impact Propagation
- Dependency Graph Generation
"""

import uuid
from typing import Optional, List, Dict, Any, Set, Tuple
from datetime import datetime


class Dependency:
    """A dependency relationship between two system elements."""

    def __init__(
        self,
        dep_id: str,
        source: str,
        target: str,
        dep_type: str = "depends",
        weight: float = 1.0,
        description: Optional[str] = None,
    ):
        self.id = dep_id
        self.source = source
        self.target = target
        self.dep_type = dep_type
        self.weight = weight
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "type": self.dep_type,
            "weight": self.weight,
            "description": self.description,
        }


class DependencyMapper:
    """
    Maps dependencies between system components.
    Provides impact analysis and dependency graph generation.
    """

    def __init__(self):
        self._dependencies: Dict[str, Dependency] = {}
        self._nodes: Dict[str, Dict[str, Any]] = {}

    def add_node(self, node_id: str, name: str, node_type: str = "component"):
        self._nodes[node_id] = {"id": node_id, "name": name, "type": node_type}

    def add_dependency(
        self, source: str, target: str,
        dep_type: str = "depends", weight: float = 1.0,
        description: Optional[str] = None,
    ) -> Dependency:
        dep_id = str(uuid.uuid4())
        dep = Dependency(dep_id, source, target, dep_type, weight, description)
        self._dependencies[dep_id] = dep
        return dep

    def get_dependents(self, node_id: str) -> List[Dependency]:
        """Get all dependencies where this node is the target."""
        return [d for d in self._dependencies.values() if d.target == node_id]

    def get_dependencies(self, node_id: str) -> List[Dependency]:
        """Get all dependencies where this node is the source."""
        return [d for d in self._dependencies.values() if d.source == node_id]

    def find_impact_chain(self, node_id: str, max_depth: int = 10) -> List[Dict[str, Any]]:
        """Find the chain of impacts if this node changes."""
        chain = []
        visited: Set[str] = set()

        def _traverse(current_id: str, depth: int):
            if current_id in visited or depth > max_depth:
                return
            visited.add(current_id)

            deps = self.get_dependencies(current_id)
            for dep in deps:
                chain.append({
                    "from": dep.source,
                    "from_name": self._nodes.get(dep.source, {}).get("name", dep.source),
                    "to": dep.target,
                    "to_name": self._nodes.get(dep.target, {}).get("name", dep.target),
                    "type": dep.dep_type,
                    "depth": depth,
                })
                _traverse(dep.target, depth + 1)

        _traverse(node_id, 0)
        return chain

    def find_critical_path(self) -> List[Dict[str, Any]]:
        """Find the critical dependency path."""
        in_degree: Dict[str, int] = {}
        for dep in self._dependencies.values():
            if dep.source not in in_degree:
                in_degree[dep.source] = 0
            if dep.target not in in_degree:
                in_degree[dep.target] = 0
            in_degree[dep.target] = in_degree.get(dep.target, 0) + 1

        start_nodes = [nid for nid, deg in in_degree.items() if deg == 0]
        queue = [(nid, [nid]) for nid in start_nodes]
        longest_path = []

        while queue:
            current, path = queue.pop(0)
            if len(path) > len(longest_path):
                longest_path = path
            deps = self.get_dependencies(current)
            for dep in deps:
                queue.append((dep.target, path + [dep.target]))

        return [
            {"node_id": nid, "name": self._nodes.get(nid, {}).get("name", nid)}
            for nid in longest_path
        ]

    def generate_dependency_graph(self) -> Dict[str, Any]:
        """Generate a complete dependency graph."""
        return {
            "nodes": list(self._nodes.values()),
            "edges": [d.to_dict() for d in self._dependencies.values()],
            "stats": {
                "total_nodes": len(self._nodes),
                "total_dependencies": len(self._dependencies),
            },
        }