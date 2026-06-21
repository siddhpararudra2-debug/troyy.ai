from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

class ProjectPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class Department(str, Enum):
    MECHANICAL = "MECHANICAL"
    ELECTRONICS = "ELECTRONICS"
    FIRMWARE = "FIRMWARE"
    SIMULATION = "SIMULATION"
    MANUFACTURING = "MANUFACTURING"
    COMPLIANCE = "COMPLIANCE"
    VERIFICATION = "VERIFICATION"

class ResourceAllocation(BaseModel):
    department: Department
    project_id: str
    compute_hours: float
    engineer_hours: float
    budget_usd: float
    allocated_at: datetime = Field(default_factory=datetime.utcnow)

class PortfolioProject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    priority: ProjectPriority
    department_assignments: List[Department] = Field(default_factory=list)
    status: str = "INITIATED"
    resources: List[ResourceAllocation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class StrategicDirective(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    objectives: List[str] = Field(default_factory=list)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    issued_at: datetime = Field(default_factory=datetime.utcnow)

class EngineeringOrganization:
    def __init__(self):
        self.portfolio: Dict[str, PortfolioProject] = {}
        self.directives: List[StrategicDirective] = []
        self.resource_budget = {
            Department.MECHANICAL: 1000,
            Department.ELECTRONICS: 1000,
            Department.FIRMWARE: 800,
            Department.SIMULATION: 1500,
            Department.MANUFACTURING: 500,
            Department.COMPLIANCE: 400,
            Department.VERIFICATION: 600
        }
