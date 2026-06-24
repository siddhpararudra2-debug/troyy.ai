"""Mission Replayer - Module 5 for Sprint 13."""
import uuid
from typing import Dict, Any


class MissionReplayer:
    def __init__(self):
        self.replays: Dict[str, Any] = {}

    def start_replay(self, original_mission_id: str, playback_speed: float = 1.0) -> str:
        replay_id = str(uuid.uuid4())
        replay = {
            "id": replay_id,
            "original_mission_id": original_mission_id,
            "playback_speed": playback_speed,
            "status": "playing",
            "current_position": 0.0,
        }
        self.replays[replay_id] = replay
        return replay_id

    def pause_replay(self, replay_id: str) -> bool:
        if replay_id in self.replays:
            self.replays[replay_id]["status"] = "paused"
            return True
        return False

    def resume_replay(self, replay_id: str) -> bool:
        if replay_id in self.replays:
            self.replays[replay_id]["status"] = "playing"
            return True
        return False

    def get_replay(self, replay_id: str) -> Any:
        return self.replays.get(replay_id)
