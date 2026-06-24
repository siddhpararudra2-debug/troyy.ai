"""Situational Awareness - Real-time operational picture."""

from typing import Dict, List, Any, Optional
from datetime import datetime


class SituationalAwareness:
    """Maintains real-time situational awareness."""
    
    def __init__(self):
        """Initialize situational awareness."""
        self.entity_positions: Dict[str, Dict[str, float]] = {}
        self.entity_status: Dict[str, Dict[str, Any]] = {}
        self.threats: List[Dict[str, Any]] = []
        self.operational_picture: Dict[str, Any] = {}
    
    def update_entity_position(
        self,
        entity_id: str,
        position: Dict[str, float],
        velocity: Dict[str, float],
        timestamp: datetime = None
    ) -> None:
        """Update entity position in awareness."""
        self.entity_positions[entity_id] = {
            "position": position,
            "velocity": velocity,
            "timestamp": timestamp or datetime.utcnow(),
        }
    
    def update_entity_status(
        self,
        entity_id: str,
        status: Dict[str, Any]
    ) -> None:
        """Update entity status."""
        self.entity_status[entity_id] = {
            "status": status,
            "timestamp": datetime.utcnow(),
        }
    
    def add_threat(
        self,
        threat_type: str,
        location: Dict[str, float],
        severity: str = "medium"
    ) -> None:
        """Add threat to awareness."""
        threat = {
            "id": f"threat_{len(self.threats)}",
            "type": threat_type,
            "location": location,
            "severity": severity,
            "detected_at": datetime.utcnow(),
        }
        self.threats.append(threat)
    
    def clear_expired_threats(self, expiration_minutes: int = 30) -> None:
        """Remove expired threats."""
        now = datetime.utcnow()
        self.threats = [
            t for t in self.threats
            if (now - t["detected_at"]).total_seconds() < expiration_minutes * 60
        ]
    
    def get_operational_picture(self) -> Dict[str, Any]:
        """Get complete operational picture."""
        return {
            "entities": len(self.entity_positions),
            "threats": len(self.threats),
            "entity_positions": self.entity_positions,
            "entity_status": self.entity_status,
            "threats": self.threats,
            "timestamp": datetime.utcnow(),
        }
    
    def get_entity_picture(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity-specific picture."""
        if entity_id not in self.entity_positions:
            return None
        
        return {
            "entity_id": entity_id,
            "position": self.entity_positions[entity_id],
            "status": self.entity_status.get(entity_id, {}),
            "nearby_threats": self._get_nearby_threats(entity_id),
        }
    
    def _get_nearby_threats(self, entity_id: str, radius_km: float = 10.0) -> List[Dict[str, Any]]:
        """Get threats near entity."""
        if entity_id not in self.entity_positions:
            return []
        
        entity_pos = self.entity_positions[entity_id]["position"]
        nearby = []
        
        for threat in self.threats:
            # Simplified distance calculation
            dx = threat["location"].get("x", 0) - entity_pos.get("x", 0)
            dy = threat["location"].get("y", 0) - entity_pos.get("y", 0)
            distance = (dx**2 + dy**2) ** 0.5
            
            if distance < radius_km * 1000:
                nearby.append(threat)
        
        return nearby
