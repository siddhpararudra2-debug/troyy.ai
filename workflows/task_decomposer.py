"""
Task Decomposer - Decomposes high-level engineering tasks into subtasks.

Capabilities:
- Task Decomposition
- Dependency Resolution
- Task Graph Generation
"""
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime


class TaskDecomposer:
    """Decomposes engineering tasks into structured subtask graphs."""

    STANDARD_DECOMPOSITIONS = {
        "drone_development": [
            {"name": "Define Mission Requirements", "type": "requirements", "depends_on": []},
            {"name": "Design Airframe", "type": "mechanical", "depends_on": ["Define Mission Requirements"]},
            {"name": "Select Propulsion System", "type": "mechanical", "depends_on": ["Design Airframe"]},
            {"name": "Design Avionics", "type": "electronics", "depends_on": ["Define Mission Requirements"]},
            {"name": "Develop Flight Software", "type": "software", "depends_on": ["Select Propulsion System", "Design Avionics"]},
            {"name": "Integration and Test", "type": "integration", "depends_on": ["Develop Flight Software"]},
        ],
        "satellite_development": [
            {"name": "Define Mission Orbit", "type": "requirements", "depends_on": []},
            {"name": "Design Satellite Bus", "type": "mechanical", "depends_on": ["Define Mission Orbit"]},
            {"name": "Design Power System", "type": "electronics", "depends_on": ["Design Satellite Bus"]},
            {"name": "Design Communication System", "type": "electronics", "depends_on": ["Design Satellite Bus"]},
            {"name": "Design Payload", "type": "payload", "depends_on": ["Define Mission Orbit"]},
            {"name": "Integration and Testing", "type": "integration", "depends_on": ["Design Power System", "Design Communication System", "Design Payload"]},
        ],
    }

    def decompose(self, task_name: str, task_type: str = "general",
                  description: Optional[str] = None) -> Dict[str, Any]:
        """Decompose a high-level task into subtasks."""
        subtasks = self.STANDARD_DECOMPOSITIONS.get(task_name, self._generic_decomposition(task_name))
        return {"task_name": task_name, "task_type": task_type, "subtasks": subtasks}

    def _generic_decomposition(self, task_name: str) -> List[Dict[str, Any]]:
        return [
            {"name": f"Analyze {task_name}", "type": "analysis", "depends_on": []},
            {"name": f"Design {task_name}", "type": "design", "depends_on": [f"Analyze {task_name}"]},
            {"name": f"Implement {task_name}", "type": "implementation", "depends_on": [f"Design {task_name}"]},
            {"name": f"Test {task_name}", "type": "testing", "depends_on": [f"Implement {task_name}"]},
        ]

    def generate_task_graph(self, subtasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a task dependency graph."""
        name_to_index = {st["name"]: i for i, st in enumerate(subtasks)}
        tasks = []
        for i, st in enumerate(subtasks):
            deps = []
            for d in st.get("depends_on", []):
                if d in name_to_index:
                    deps.append(f"T{name_to_index[d] + 1}")
            tasks.append({"id": f"T{i+1}", "name": st["name"], "type": st["type"],
                          "depends_on": deps})
        return {"tasks": tasks, "total_tasks": len(tasks)}
