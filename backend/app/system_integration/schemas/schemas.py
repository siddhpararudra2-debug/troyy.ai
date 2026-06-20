"""
System Integration & Hardware-Software Co-Design Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


# Base Request
class BaseSystemRequest(BaseModel):
    project_id: str
    project_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


# 1 - System Architecture
class SystemArchitectureRequest(BaseSystemRequest):
    pass


class SubsystemInfo(BaseModel):
    name: str
    type: str
    subcomponents: List[str]


class SystemArchitectureResponse(BaseModel):
    id: str
    project_id: str
    subsystem_hierarchy: List[SubsystemInfo]
    dependency_map: Dict[str, List[str]]
    signal_flow: List[Dict[str, Any]]
    power_flow: List[Dict[str, Any]]
    control_flow: List[Dict[str, Any]]
    mechanical_interfaces: List[Dict[str, Any]]
    software_interfaces: List[Dict[str, Any]]
    execution_time_ms: Optional[float] = None
    created_at: datetime


# 2 - Requirement Traceability
class TraceabilityRequest(BaseSystemRequest):
    pass


class RequirementInfo(BaseModel):
    id: str
    description: str
    status: str
    parent_id: Optional[str] = None


class TraceabilityResponse(BaseModel):
    id: str
    project_id: str
    requirements: List[RequirementInfo]
    traceability_matrix: Dict[str, List[str]]
    coverage_report: Dict[str, Any]
    gap_analysis: List[Dict[str, Any]]
    execution_time_ms: Optional[float] = None
    created_at: datetime


# 3 - Subsystem Integration
class IntegrationRequest(BaseSystemRequest):
    integration_pairs: Optional[List[Dict[str, str]]] = None


class IntegrationResponse(BaseModel):
    id: str
    project_id: str
    integration_map: Dict[str, Any]
    subsystem_dependencies: Dict[str, List[str]]
    execution_time_ms: Optional[float] = None
    created_at: datetime


# 4 - Hardware Software Mapping
class HardwareSoftwareMappingRequest(BaseSystemRequest):
    pass


class HardwareSoftwareMappingResponse(BaseModel):
    id: str
    project_id: str
    hw_sw_dependency_graph: Dict[str, List[str]]
    mappings: List[Dict[str, str]]
    execution_time_ms: Optional[float] = None
    created_at: datetime


# 5 - Interface Management
class InterfaceManagementRequest(BaseSystemRequest):
    pass


class InterfaceDefinition(BaseModel):
    id: str
    type: str
    source: str
    target: str
    properties: Dict[str, Any]


class InterfaceManagementResponse(BaseModel):
    id: str
    project_id: str
    interfaces: List[InterfaceDefinition]
    compatibility_reports: List[Dict[str, Any]]
    execution_time_ms: Optional[float] = None
    created_at: datetime


# 6 - Dependency Management
class DependencyManagementRequest(BaseSystemRequest):
    pass


class DependencyInfo(BaseModel):
    source: str
    target: str
    type: str
    description: str


class DependencyManagementResponse(BaseModel):
    id: str
    project_id: str
    dependency_graph: List[DependencyInfo]
    impact_analysis: List[Dict[str, Any]]
    execution_time_ms: Optional[float] = None
    created_at: datetime


# 7 - Digital Thread
class DigitalThreadRequest(BaseSystemRequest):
    pass


class DigitalThreadRecord(BaseModel):
    id: str
    artifact_type: str
    artifact_id: str
    parent_ids: List[str]
    timestamp: datetime


class DigitalThreadResponse(BaseModel):
    id: str
    project_id: str
    digital_thread: List[DigitalThreadRecord]
    design_evolution_map: Dict[str, List[str]]
    execution_time_ms: Optional[float] = None
    created_at: datetime


# 8 - Configuration Management
class ConfigurationManagementRequest(BaseSystemRequest):
    pass


class ConfigurationBaseline(BaseModel):
    id: str
    name: str
    version: str
    artifacts: List[str]
    approvals: List[Dict[str, Any]]


class ConfigurationManagementResponse(BaseModel):
    id: str
    project_id: str
    configuration_baselines: List[ConfigurationBaseline]
    revision_reports: List[Dict[str, Any]]
    execution_time_ms: Optional[float] = None
    created_at: datetime


# 9 - System Validation
class SystemValidationRequest(BaseSystemRequest):
    pass


class SystemValidationResponse(BaseModel):
    id: str
    project_id: str
    validation_results: List[Dict[str, Any]]
    engineering_findings: List[str]
    execution_time_ms: Optional[float] = None
    created_at: datetime


# 10 - System Review Board
class SystemReviewRequest(BaseSystemRequest):
    pass


class SystemReviewResponse(BaseModel):
    id: str
    project_id: str
    critical_findings: List[str]
    risks: List[Dict[str, Any]]
    recommendations: List[str]
    approval_status: str
    execution_time_ms: Optional[float] = None
    created_at: datetime
