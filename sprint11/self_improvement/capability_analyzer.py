"""
Capability Analyzer — tracks agent capabilities as vectors.
"""
from typing import Dict, List, Optional
import numpy as np
import hashlib
from sprint11.schemas.models import AgentCapability
from sprint11.schemas.enums import AgentCapabilityLevel

class CapabilityAnalyzer:
    """Analyzes and tracks agent capabilities."""
    
    # Standard capability dimensions
    CAPABILITY_DIMENSIONS = [
        "reasoning", "planning", "coding", "math", "physics",
        "design", "analysis", "communication", "tool_usage", "safety"
    ]
    
    def __init__(self, embedding_dim: int = 64):
        self.embedding_dim = embedding_dim
        self.capabilities: Dict[str, List[AgentCapability]] = {}
        
    def record_capability(self, agent_id: str, capability_name: str,
                         score: float, evidence: Dict = None) -> AgentCapability:
        """Record a capability assessment."""
        # Determine level from score
        if score >= 0.9:
            level = AgentCapabilityLevel.MASTER
        elif score >= 0.75:
            level = AgentCapabilityLevel.EXPERT
        elif score >= 0.6:
            level = AgentCapabilityLevel.PROFICIENT
        elif score >= 0.4:
            level = AgentCapabilityLevel.COMPETENT
        else:
            level = AgentCapabilityLevel.NOVICE
            
        # Compute embedding (deterministic hash-based)
        embedding = self._compute_embedding(agent_id, capability_name, score)
        
        cap = AgentCapability(
            agent_id=agent_id,
            capability_name=capability_name,
            level=level.value,
            score=score,
            embedding=embedding,
            evidence=[evidence] if evidence else []
        )
        
        caps = self.capabilities.setdefault(agent_id, [])
        # Update existing or add new
        existing = next((c for c in caps if c.capability_name == capability_name), None)
        if existing:
            existing.level = level.value
            existing.score = score
            existing.embedding = embedding
            if evidence:
                existing.evidence.append(evidence)
            existing.last_evaluated = __import__("datetime").datetime.utcnow()
            return existing
        else:
            caps.append(cap)
            return cap
            
    def get_agent_profile(self, agent_id: str) -> Dict:
        """Get complete capability profile for an agent."""
        caps = self.capabilities.get(agent_id, [])
        if not caps:
            return {"agent_id": agent_id, "capabilities": [], "profile_vector": []}
            
        # Build profile vector (average of capability scores in standard dimensions)
        profile = np.zeros(len(self.CAPABILITY_DIMENSIONS))
        for i, dim in enumerate(self.CAPABILITY_DIMENSIONS):
            matching = [c for c in caps if c.capability_name == dim]
            if matching:
                profile[i] = matching[-1].score
                
        # Overall embedding (concatenation of all capability embeddings)
        all_embeddings = [np.array(c.embedding) for c in caps]
        if all_embeddings:
            overall_embedding = np.mean(all_embeddings, axis=0).tolist()
        else:
            overall_embedding = [0.0] * self.embedding_dim
            
        return {
            "agent_id": agent_id,
            "capabilities": [c.model_dump() for c in caps],
            "profile_vector": profile.tolist(),
            "overall_embedding": overall_embedding,
            "strongest": max(caps, key=lambda c: c.score).capability_name if caps else None,
            "weakest": min(caps, key=lambda c: c.score).capability_name if caps else None
        }
        
    def find_similar_agents(self, agent_id: str, top_k: int = 3) -> List[Dict]:
        """Find agents with similar capability profiles."""
        target_profile = self.get_agent_profile(agent_id)
        if not target_profile.get("overall_embedding"):
            return []
            
        target_vec = np.array(target_profile["overall_embedding"])
        target_norm = np.linalg.norm(target_vec)
        if target_norm == 0:
            return []
            
        similarities = []
        for other_id in self.capabilities.keys():
            if other_id == agent_id:
                continue
            other_profile = self.get_agent_profile(other_id)
            other_vec = np.array(other_profile.get("overall_embedding", []))
            if len(other_vec) != len(target_vec):
                continue
            other_norm = np.linalg.norm(other_vec)
            if other_norm == 0:
                continue
            sim = float(np.dot(target_vec, other_vec) / (target_norm * other_norm))
            similarities.append({
                "agent_id": other_id,
                "similarity": sim,
                "profile": other_profile
            })
            
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_k]
        
    def detect_skill_gaps(self, agent_id: str,
                         required_capabilities: Dict[str, float]) -> List[Dict]:
        """Detect skill gaps against requirements."""
        profile = self.get_agent_profile(agent_id)
        caps_by_name = {c["capability_name"]: c for c in profile["capabilities"]}
        
        gaps = []
        for cap_name, required_score in required_capabilities.items():
            current = caps_by_name.get(cap_name, {}).get("score", 0.0)
            if current < required_score:
                gaps.append({
                    "capability": cap_name,
                    "current_score": current,
                    "required_score": required_score,
                    "gap": required_score - current,
                    "priority": (required_score - current) / required_score
                })
                
        gaps.sort(key=lambda g: g["priority"], reverse=True)
        return gaps
        
    def _compute_embedding(self, agent_id: str, capability_name: str,
                          score: float) -> List[float]:
        """Compute deterministic embedding for capability."""
        # Hash-based pseudo-embedding
        text = f"{agent_id}:{capability_name}:{score:.4f}"
        h = hashlib.sha512(text.encode()).digest()
        vec = [(b / 127.5) - 1.0 for b in h[:self.embedding_dim]]
        # Modulate by score
        vec = [v * score for v in vec]
        return vec
