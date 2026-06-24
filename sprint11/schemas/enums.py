from enum import Enum

class ExperimentState(str, Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class HypothesisStatus(str, Enum):
    PROPOSED = "PROPOSED"
    TESTED = "TESTED"
    SUPPORTED = "SUPPORTED"
    REFUTED = "REFUTED"
    INCONCLUSIVE = "INCONCLUSIVE"

class AgentCapabilityLevel(str, Enum):
    NOVICE = "NOVICE"
    COMPETENT = "COMPETENT"
    PROFICIENT = "PROFICIENT"
    EXPERT = "EXPERT"
    MASTER = "MASTER"

class GovernanceDecision(str, Enum):
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"

class SafetyLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class BenchmarkDomain(str, Enum):
    REASONING = "REASONING"
    CODING = "CODING"
    ENGINEERING_ANALYSIS = "ENGINEERING_ANALYSIS"
    DESIGN = "DESIGN"
    PLANNING = "PLANNING"
    SAFETY = "SAFETY"
