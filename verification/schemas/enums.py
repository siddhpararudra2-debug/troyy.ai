from enum import Enum

class TestType(str, Enum):
    UNIT = "UNIT"
    INTEGRATION = "INTEGRATION"
    SYSTEM = "SYSTEM"
    ACCEPTANCE = "ACCEPTANCE"
    REGRESSION = "REGRESSION"

class CoverageType(str, Enum):
    STATEMENT = "STATEMENT"
    BRANCH = "BRANCH"
    CONDITION = "CONDITION"
    MCDC = "MCDC"

class ExecutionEnvironment(str, Enum):
    SIL = "SIL"
    HIL = "HIL"
    PIL = "PIL"
    PHYSICAL = "PHYSICAL"

class TestStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"

class VerificationMethod(str, Enum):
    ANALYSIS = "ANALYSIS"
    TEST = "TEST"
    SIMULATION = "SIMULATION"
    INSPECTION = "INSPECTION"
    REVIEW = "REVIEW"
