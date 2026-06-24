"""
Behavior Model - System behavior and functional modeling for MBSE.

Capabilities:
- Behavior Modeling
- Functional Decomposition
- Activity Modeling
- State Machine Concepts
"""

import uuid
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime


class BehaviorType(str, Enum):
    """Types of system behaviors."""
    FUNCTION = "function"
    ACTIVITY = "activity"
    STATE = "state"
    TRANSITION = "transition"
    USE_CASE = "use_case"
    INTERACTION = "interaction"


class BehaviorElement:
    """A behavioral element in the system."""

    def __init__(
        self,
        behavior_id: str,
        name: str,
        behavior_type: BehaviorType,
        description: Optional[str] = None,
        parent_id: Optional[str] = None,
    ):
        self.id = behavior_id
        self.name = name
        self.behavior_type = behavior_type
        self.description = description
        self.parent_id = parent_id
        self.child_ids: List[str] = []
        self.inputs: List[Dict[str, Any]] = []
        self.outputs: List[Dict[str, Any]] = []
        self.constraints: List[str] = []
        self.allocated_to: List[str] = []  # Element IDs this behavior is allocated to
        self.metadata: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "behavior_type": self.behavior_type.value,
            "description": self.description,
            "parent_id": self.parent_id,
            "child_ids": self.child_ids,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "constraints": self.constraints,
            "allocated_to": self.allocated_to,
            "metadata": self.metadata,
        }


class BehaviorModel:
    """
    Models system behavior, functions, and activities.
    Supports functional decomposition and allocation to system elements.
    """

    def __init__(self):
        self._behaviors: Dict[str, BehaviorElement] = {}

    def create_behavior(
        self,
        name: str,
        behavior_type: BehaviorType,
        description: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> BehaviorElement:
        """Create a behavioral element."""
        behavior_id = str(uuid.uuid4())
        behavior = BehaviorElement(
            behavior_id=behavior_id,
            name=name,
            behavior_type=behavior_type,
            description=description,
            parent_id=parent_id,
        )
        self._behaviors[behavior_id] = behavior

        if parent_id and parent_id in self._behaviors:
            self._behaviors[parent_id].child_ids.append(behavior_id)

        return behavior

    def allocate_to_element(self, behavior_id: str, element_id: str) -> bool:
        """Allocate a behavior to a system element."""
        if behavior_id in self._behaviors:
            if element_id not in self._behaviors[behavior_id].allocated_to:
                self._behaviors[behavior_id].allocated_to.append(element_id)
            return True
        return False

    def get_functional_flow(self, root_behavior_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get the functional flow hierarchy."""
        if root_behavior_id:
            roots = [self._behaviors[root_behavior_id]] if root_behavior_id in self._behaviors else []
        else:
            roots = [b for b in self._behaviors.values() if b.parent_id is None]

        def _flatten(behavior: BehaviorElement) -> Dict[str, Any]:
            return {
                "id": behavior.id,
                "name": behavior.name,
                "type": behavior.behavior_type.value,
                "inputs": behavior.inputs,
                "outputs": behavior.outputs,
                "children": [
                    _flatten(self._behaviors[cid])
                    for cid in behavior.child_ids
                    if cid in self._behaviors
                ],
            }

        return [_flatten(r) for r in roots]

    def get_all_behaviors(self) -> List[BehaviorElement]:
        """Get all behaviors."""
        return list(self._behaviors.values())


class ActivityModel:
    """
    Models system activities and their sequences.
    Supports control flow and object flow between activities.
    """

    def __init__(self):
        self._activities: Dict[str, Dict[str, Any]] = {}

    def add_activity(self, name: str, description: Optional[str] = None) -> str:
        """Add an activity node."""
        activity_id = str(uuid.uuid4())
        self._activities[activity_id] = {
            "id": activity_id,
            "name": name,
            "description": description,
            "incoming": [],
            "outgoing": [],
        }
        return activity_id

    def add_control_flow(self, from_id: str, to_id: str, condition: Optional[str] = None) -> bool:
        """Add a control flow between activities."""
        if from_id in self._activities and to_id in self._activities:
            flow = {"target": to_id, "condition": condition}
            self._activities[from_id]["outgoing"].append(flow)
            self._activities[to_id]["incoming"].append({"source": from_id})
            return True
        return False

    def get_activity_diagram(self) -> Dict[str, Any]:
        """Get activity diagram representation."""
        return {
            "activities": list(self._activities.values()),
            "type": "ActivityDiagram",
        }