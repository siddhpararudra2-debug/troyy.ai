"""State Machine - State Management for Sprint 17."""
from typing import Dict, Any, List, Optional


class StateMachine:
    """Generic state machine implementation."""

    def __init__(self, states: List[str], transitions: List[Dict[str, str]], initial_state: str):
        self.states = states
        self.transitions = transitions
        self.current_state = initial_state

    def can_transition_to(self, target_state: str) -> bool:
        """Check if transition to target_state is allowed."""
        for t in self.transitions:
            if t["from"] == self.current_state and t["to"] == target_state:
                return True
        return False

    def transition_to(self, target_state: str) -> bool:
        """Perform transition if allowed."""
        if self.can_transition_to(target_state):
            self.current_state = target_state
            return True
        return False
