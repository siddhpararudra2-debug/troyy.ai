"""Voice Interface - Voice commands for robots in Sprint 14."""
from typing import Dict, Any


class VoiceInterface:
    """Voice command interface for robots."""

    def process_command(self, audio: Any) -> Dict[str, Any]:
        """Process voice command."""
        return {"intent": "unknown", "confidence": 0.5}

    def speak(self, text: str) -> None:
        """Synthesize speech."""
        pass
