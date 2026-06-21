from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import uuid
from datetime import datetime

class AgentRole(str, Enum):
    MECHANICAL = "MECHANICAL"
    ELECTRONICS = "ELECTRONICS"
    FIRMWARE = "FIRMWARE"
    SIMULATION = "SIMULATION"
    AEROSPACE = "AEROSPACE"
    ROBOTICS = "ROBOTICS"
    COMPLIANCE = "COMPLIANCE"
    VERIFICATION = "VERIFICATION"
    CHIEF_ENGINEER = "CHIEF_ENGINEER"

class DebatePosition(BaseModel):
    agent_id: str
    role: AgentRole
    claim: str
    evidence: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ConsensusResult(BaseModel):
    topic: str
    decision: str
    votes: Dict[str, float] = Field(default_factory=dict)
    confidence: float
    dissenting_agents: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AgentMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str
    recipient: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AgentMemory(BaseModel):
    agent_id: str
    role: AgentRole
    facts: Dict[str, Any] = Field(default_factory=dict)
    decisions: List[ConsensusResult] = Field(default_factory=list)
    messages: List[AgentMessage] = Field(default_factory=list)
    version: int = 0
