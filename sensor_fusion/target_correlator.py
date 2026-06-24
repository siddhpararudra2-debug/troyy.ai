"""Target Correlator - Module 6 for Sprint 13."""
from typing import Dict, Any, List, Tuple


class TargetCorrelator:
    def __init__(self):
        self.correlations: List[Dict[str, Any]] = []

    def correlate_measurements(
        self,
        measurements: List[Dict[str, Any]],
        tracks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        correlations = []
        for m in measurements:
            for t in tracks:
                distance = self._calculate_distance(
                    m.get("position", {}),
                    t["state"]["position"]
                )
                if distance < 10.0:
                    correlations.append({
                        "measurement": m,
                        "track_id": t["id"],
                        "confidence": 1.0 - (distance / 10.0),
                    })
        self.correlations.extend(correlations)
        return correlations

    def _calculate_distance(self, p1: Dict[str, float], p2: Dict[str, float]) -> float:
        dx = p1.get("x", 0.0) - p2.get("x", 0.0)
        dy = p1.get("y", 0.0) - p2.get("y", 0.0)
        dz = p1.get("z", 0.0) - p2.get("z", 0.0)
        return (dx**2 + dy**2 + dz**2)**0.5
