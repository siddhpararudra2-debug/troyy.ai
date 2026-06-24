"""Mission Allocator - Allocate missions to robots in Sprint 14."""
from typing import Dict, Any, List, Tuple


class MissionAllocator:
    """Allocates missions to robots in a fleet."""

    def __init__(self):
        self.allocations: Dict[str, str] = {}

    def allocate(
        self,
        mission: Dict[str, Any],
        robots: List[Dict[str, Any]],
    ) -> Tuple[str, List[str]]:
        """Allocate a mission to robots."""
        if not robots:
            return mission["id"], []
        assigned = [robots[0]["id"]]
        self.allocations[mission["id"]] = assigned[0]
        return mission["id"], assigned
