"""
Global Agent Manager
"""
import time
from typing import Dict, Any, List


class GlobalAgentManager:
    def get_agents(self) -> Dict[str, Any]:
        start_time = time.time()

        return {
            "agents": [
                {"id": "agent-1", "type": "cad", "status": "active"},
                {"id": "agent-2", "type": "electronics", "status": "active"},
                {"id": "agent-3", "type": "simulation", "status": "idle"},
                {"id": "agent-4", "type": "mission", "status": "active"},
                {"id": "agent-5", "type": "plm", "status": "idle"}
            ],
            "execution_time_ms": (time.time() - start_time) * 1000
        }
