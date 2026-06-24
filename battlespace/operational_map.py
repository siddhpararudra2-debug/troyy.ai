"""Operational Map - 2D/3D operational visualization."""

from typing import Dict, List, Any, Optional
import uuid


class OperationalMap:
    """Manages operational maps and overlays."""
    
    def __init__(self):
        """Initialize operational map."""
        self.maps: Dict[str, Dict[str, Any]] = {}
        self.layers: Dict[str, List[Dict[str, Any]]] = {}
    
    def create_map(
        self,
        name: str,
        center: Dict[str, float],
        zoom: int = 10,
        map_type: str = "satellite"
    ) -> str:
        """Create operational map."""
        map_id = str(uuid.uuid4())
        
        self.maps[map_id] = {
            "id": map_id,
            "name": name,
            "center": center,
            "zoom": zoom,
            "type": map_type,
            "layers": [],
        }
        
        self.layers[map_id] = []
        return map_id
    
    def add_layer(
        self,
        map_id: str,
        layer_name: str,
        layer_data: Dict[str, Any]
    ) -> bool:
        """Add layer to map."""
        if map_id not in self.maps:
            return False
        
        layer = {
            "name": layer_name,
            "data": layer_data,
            "visible": True,
        }
        
        self.layers[map_id].append(layer)
        self.maps[map_id]["layers"].append(layer_name)
        
        return True
    
    def add_marker(
        self,
        map_id: str,
        position: Dict[str, float],
        marker_type: str,
        label: str = ""
    ) -> bool:
        """Add marker to map."""
        if map_id not in self.maps:
            return False
        
        # Add to a markers layer
        marker = {
            "position": position,
            "type": marker_type,
            "label": label,
        }
        
        if not any(l["name"] == "markers" for l in self.layers[map_id]):
            self.add_layer(map_id, "markers", {"features": []})
        
        for layer in self.layers[map_id]:
            if layer["name"] == "markers":
                layer["data"]["features"].append(marker)
        
        return True
    
    def get_map(self, map_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve map."""
        return self.maps.get(map_id)
    
    def render_map(self, map_id: str) -> Dict[str, Any]:
        """Render map for display."""
        if map_id not in self.maps:
            return {}
        
        map_data = self.maps[map_id]
        
        return {
            "id": map_id,
            "name": map_data["name"],
            "center": map_data["center"],
            "zoom": map_data["zoom"],
            "type": map_data["type"],
            "layers": self.layers.get(map_id, []),
        }
