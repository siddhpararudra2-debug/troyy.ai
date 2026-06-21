from typing import List, Dict
from engineering_swarm.schemas.swarm_models import DebatePosition

class DebateEngine:
    def __init__(self, max_rounds: int = 5):
        self.max_rounds = max_rounds
        
    def conduct_debate(self, positions: List[DebatePosition], topic: str) -> Dict:
        debate_log = []
        current_positions = positions.copy()
        
        for round_num in range(self.max_rounds):
            round_log = {"round": round_num + 1, "positions": []}
            
            for pos in current_positions:
                round_log["positions"].append({
                    "agent": pos.agent_id,
                    "role": pos.role.value,
                    "claim": pos.claim,
                    "confidence": pos.confidence
                })
                
            confidences = [p.confidence for p in current_positions]
            if max(confidences) - min(confidences) < 0.1:
                debate_log.append({"event": "CONVERGENCE", "round": round_num + 1})
                break
                
            n_current = len(current_positions)
            for i in range(n_current):
                pos = current_positions[i]
                if i < n_current - 1:
                    counter = DebatePosition(
                        agent_id=pos.agent_id,
                        role=pos.role,
                        claim=f"Counter to {current_positions[i+1].claim[:30]}...",
                        evidence=["Alternative analysis"],
                        confidence=pos.confidence * 0.95
                    )
                    current_positions.append(counter)
                    
            debate_log.append(round_log)
            
        return {"topic": topic, "rounds": len(debate_log), "log": debate_log, "final_positions": [p.dict() for p in current_positions[:len(positions)]]}
