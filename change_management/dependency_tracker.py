"""Dependency Tracker - Change Management for Sprint 17."""
from typing import Dict, List, Optional, Any


class DependencyTracker:
    """Track dependencies between engineering artifacts."""

    def __init__(self):
        self.dependencies: Dict[str, List[str]] = {}

    def add_dependency(self, artifact_id: str, depends_on: str) -> None:
        """Add a dependency relationship."""
        if artifact_id not in self.dependencies:
            self.dependencies[artifact_id] = []
        if depends_on not in self.dependencies[artifact_id]:
            self.dependencies[artifact_id].append(depends_on)

    def get_dependencies(self, artifact_id: str) -> List[str]:
        """Get dependencies of an artifact."""
        return self.dependencies.get(artifact_id, [])

    def get_dependents(self, artifact_id: str) -> List[str]:
        """Get artifacts that depend on given artifact."""
        dependents = []
        for aid, deps in self.dependencies.items():
            if artifact_id in deps:
                dependents.append(aid)
        return dependents
