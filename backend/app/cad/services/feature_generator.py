"""
Feature Generator - Handles feature-based modeling
"""
from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class FeatureGenerator:
    """Generates and manages CAD features."""
    
    def __init__(self):
        self.features = []
        self.feature_library = self._init_feature_library()
    
    def _init_feature_library(self) -> Dict[str, Any]:
        """Initialize standard feature library."""
        return {
            "hole": self._create_hole_feature,
            "fillet": self._create_fillet_feature,
            "chamfer": self._create_chamfer_feature,
            "boss": self._create_boss_feature,
            "cut": self._create_cut_feature,
            "rib": self._create_rib_feature,
            "shell": self._create_shell_feature,
            "draft": self._create_draft_feature,
            "pattern_linear": self._create_linear_pattern,
            "pattern_circular": self._create_circular_pattern,
        }
    
    def add_features(
        self, 
        base_model: Dict[str, Any], 
        features: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Add multiple features to base model."""
        feature_model = {
            **base_model,
            "features": [],
        }
        
        for feature_data in features:
            feature = self.create_feature(feature_data)
            feature_model["features"].append(feature)
        
        return feature_model
    
    def create_feature(self, feature_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a single feature from data."""
        feature_type = feature_data.get("type")
        if feature_type in self.feature_library:
            return self.feature_library[feature_type](feature_data)
        else:
            logger.warning(f"Unknown feature type: {feature_type}")
            return feature_data
    
    def _create_hole_feature(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a hole feature."""
        return {
            "type": "hole",
            "position": data.get("position", [0, 0, 0]),
            "diameter": data.get("diameter", 5.0),
            "depth": data.get("depth"),
            "hole_type": data.get("hole_type", "simple"),  # simple, counterbore, countersink
            "counterbore_diameter": data.get("counterbore_diameter"),
            "counterbore_depth": data.get("counterbore_depth"),
            "countersink_angle": data.get("countersink_angle", 90.0),
        }
    
    def _create_fillet_feature(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a fillet feature."""
        return {
            "type": "fillet",
            "edges": data.get("edges", []),
            "radius": data.get("radius", 1.0),
        }
    
    def _create_chamfer_feature(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a chamfer feature."""
        return {
            "type": "chamfer",
            "edges": data.get("edges", []),
            "distance": data.get("distance", 1.0),
            "angle": data.get("angle", 45.0),
        }
    
    def _create_boss_feature(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a boss (extrude add) feature."""
        return {
            "type": "boss",
            "sketch": data.get("sketch"),
            "height": data.get("height", 10.0),
            "draft_angle": data.get("draft_angle", 0.0),
        }
    
    def _create_cut_feature(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a cut (extrude remove) feature."""
        return {
            "type": "cut",
            "sketch": data.get("sketch"),
            "depth": data.get("depth", 10.0),
            "draft_angle": data.get("draft_angle", 0.0),
        }
    
    def _create_rib_feature(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a rib feature."""
        return {
            "type": "rib",
            "sketch": data.get("sketch"),
            "thickness": data.get("thickness", 2.0),
        }
    
    def _create_shell_feature(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a shell feature."""
        return {
            "type": "shell",
            "thickness": data.get("thickness", 2.0),
            "faces_to_remove": data.get("faces_to_remove", []),
        }
    
    def _create_draft_feature(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a draft feature."""
        return {
            "type": "draft",
            "faces": data.get("faces", []),
            "neutral_plane": data.get("neutral_plane"),
            "angle": data.get("angle", 1.0),
        }
    
    def _create_linear_pattern(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a linear pattern feature."""
        return {
            "type": "linear_pattern",
            "feature": data.get("feature"),
            "direction1": data.get("direction1", [1, 0, 0]),
            "distance1": data.get("distance1", 10.0),
            "count1": data.get("count1", 2),
            "direction2": data.get("direction2"),
            "distance2": data.get("distance2"),
            "count2": data.get("count2"),
        }
    
    def _create_circular_pattern(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a circular pattern feature."""
        return {
            "type": "circular_pattern",
            "feature": data.get("feature"),
            "axis": data.get("axis", [0, 0, 1]),
            "angle": data.get("angle", 360.0),
            "count": data.get("count", 4),
        }
    
    def create_thread(
        self, 
        hole_feature: Dict[str, Any],
        thread_type: str = "metric",
        pitch: float = 1.0,
        major_diameter: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Add thread to a hole feature."""
        return {
            **hole_feature,
            "thread": {
                "type": thread_type,
                "pitch": pitch,
                "major_diameter": major_diameter or hole_feature.get("diameter"),
            },
        }
    
    def get_feature_tree(self, model: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get the feature tree from model."""
        return model.get("features", [])
