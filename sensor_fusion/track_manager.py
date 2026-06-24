"""Track Manager - Module 6 for Sprint 13."""
import uuid
from typing import Dict, Any, Optional, List


class TrackManager:
    def __init__(self):
        self.tracks: Dict[str, Any] = {}

    def create_track(
        self,
        initial_position: Dict[str, float],
        classification: str = "unknown"
    ) -> str:
        track_id = str(uuid.uuid4())
        self.tracks[track_id] = {
            "id": track_id,
            "state": {
                "position": initial_position,
                "velocity": {"vx": 0.0, "vy": 0.0, "vz": 0.0},
                "classification": classification,
                "confidence": 0.5,
            },
            "history": [initial_position],
            "status": "active",
        }
        return track_id

    def update_track(
        self,
        track_id: str,
        position: Dict[str, float],
        velocity: Optional[Dict[str, float]] = None
    ) -> bool:
        if track_id not in self.tracks:
            return False
        track = self.tracks[track_id]
        track["state"]["position"] = position
        if velocity:
            track["state"]["velocity"] = velocity
        track["history"].append(position)
        return True

    def get_track(self, track_id: str) -> Optional[Any]:
        return self.tracks.get(track_id)

    def list_tracks(self, status: Optional[str] = None) -> List[Any]:
        tracks = list(self.tracks.values())
        if status:
            tracks = [t for t in tracks if t["status"] == status]
        return tracks
