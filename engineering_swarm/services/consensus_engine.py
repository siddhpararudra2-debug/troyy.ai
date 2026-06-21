from typing import List, Dict
from engineering_swarm.schemas.swarm_models import DebatePosition, ConsensusResult

class ConsensusEngine:
    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
        
    def reach_consensus(self, positions: List[DebatePosition], topic: str, agent_weights: Dict[str, float]) -> ConsensusResult:
        votes = {}
        total_weight = 0
        
        for pos in positions:
            weight = agent_weights.get(pos.agent_id, 1.0)
            votes[pos.claim] = votes.get(pos.claim, 0) + pos.confidence * weight
            total_weight += weight
            
        if total_weight > 0:
            for claim in votes:
                votes[claim] /= total_weight
                
        winning_claim = max(votes, key=votes.get)
        confidence = votes[winning_claim]
        
        dissenters = [p.agent_id for p in positions if p.claim != winning_claim and p.confidence > 0.5]
        
        return ConsensusResult(
            topic=topic,
            decision=winning_claim,
            votes=votes,
            confidence=confidence,
            dissenting_agents=dissenters
        )
