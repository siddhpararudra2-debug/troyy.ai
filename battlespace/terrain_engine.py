"""Terrain Engine - Terrain modeling and analysis."""

from typing import Dict, Any, Optional, List
import math


class TerrainEngine:
    """Terrain modeling and analysis."""
    
    def __init__(self):
        """Initialize terrain engine."""
        self.terrain_models: Dict[str, Dict[str, Any]] = {}
    
    def build_terrain_model(
        self,
        name: str,
        elevation_data: List[List[float]]
    ) -> str:
        """Build terrain model from elevation data."""
        import uuid
        model_id = str(uuid.uuid4())
        
        self.terrain_models[model_id] = {
            "id": model_id,
            "name": name,
            "elevation_data": elevation_data,
            "statistics": self._calculate_terrain_stats(elevation_data),
        }
        
        return model_id
    
    def get_elevation(
        self,
        model_id: str,
        lat: float,
        lon: float
    ) -> Optional[float]:
        """Get elevation at location."""
        if model_id not in self.terrain_models:
            return None
        
        # Simplified - return average elevation
        elevations = self.terrain_models[model_id]["elevation_data"]
        if not elevations or not elevations[0]:
            return 0.0
        
        return sum(sum(row) for row in elevations) / sum(len(row) for row in elevations)
    
    def analyze_terrain(self, model_id: str) -> Dict[str, Any]:
        """Analyze terrain characteristics."""
        if model_id not in self.terrain_models:
            return {}
        
        model = self.terrain_models[model_id]
        return model["statistics"]
    
    def _calculate_terrain_stats(self, elevation_data: List[List[float]]) -> Dict[str, Any]:
        """Calculate terrain statistics."""
        if not elevation_data or not elevation_data[0]:
            return {}
        
        flat_data = [e for row in elevation_data for e in row]
        
        return {
            "min_elevation": min(flat_data),
            "max_elevation": max(flat_data),
            "avg_elevation": sum(flat_data) / len(flat_data),
            "slope": self._calculate_slope(elevation_data),
        }
    
    def _calculate_slope(self, elevation_data: List[List[float]]) -> float:
        """Calculate average slope."""
        if len(elevation_data) < 2 or len(elevation_data[0]) < 2:
            return 0.0
        
        slopes = []
        for i in range(len(elevation_data) - 1):
            for j in range(len(elevation_data[i]) - 1):
                dz = abs(elevation_data[i + 1][j + 1] - elevation_data[i][j])
                slope = math.degrees(math.atan(dz / 10.0))  # Assuming 10m cell
                slopes.append(slope)
        
        return sum(slopes) / len(slopes) if slopes else 0.0
