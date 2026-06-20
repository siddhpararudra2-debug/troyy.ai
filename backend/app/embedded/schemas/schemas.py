"""
Embedded Systems & Firmware Generation Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


# Base Request
class BaseEmbeddedRequest(BaseModel):
    project_id: str
    hardware_config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    requirements: Optional[Dict[str, Any]] = Field(default_factory=dict)


# 1. Firmware Architecture
class FirmwareArchitectureRequest(BaseEmbeddedRequest):
    system_type: str = "rtos"


class FirmwareArchitectureResponse(BaseModel):
    id: str
    project_id: str
    folder_structure: List[str] = Field(default_factory=list)
    module_architecture: Dict[str, Any] = Field(default_factory=dict)
    subsystem_design: Dict[str, Any] = Field(default_factory=dict)
    dependency_map: Dict[str, Any] = Field(default_factory=dict)
    boot_process: List[str] = Field(default_factory=list)
    initialization_flow: List[str] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# 2. RTOS
class RTOSRequest(BaseEmbeddedRequest):
    rtos_type: str = "FreeRTOS"


class TaskDefinition(BaseModel):
    id: str
    name: str
    priority: int
    stack_size: int
    period_ms: Optional[int] = None


class RTOSResponse(BaseModel):
    id: str
    project_id: str
    rtos_type: str
    tasks: List[TaskDefinition] = Field(default_factory=list)
    queues: List[Dict[str, Any]] = Field(default_factory=list)
    semaphores: List[Dict[str, Any]] = Field(default_factory=list)
    mutexes: List[Dict[str, Any]] = Field(default_factory=list)
    timers: List[Dict[str, Any]] = Field(default_factory=list)
    watchdogs: List[Dict[str, Any]] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# 3. Task Scheduler
class TaskSchedulingRequest(BaseEmbeddedRequest):
    pass


class TaskSchedulingResponse(BaseModel):
    id: str
    project_id: str
    execution_plan: List[Dict[str, Any]] = Field(default_factory=list)
    cpu_utilization: Dict[str, Any] = Field(default_factory=dict)
    priorities: Dict[str, int] = Field(default_factory=dict)
    timing_analysis: Dict[str, Any] = Field(default_factory=dict)
    wcet_analysis: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# 4. Driver Generation
class DriverGenerationRequest(BaseEmbeddedRequest):
    driver_types: List[str] = Field(default_factory=list)


class DriverDefinition(BaseModel):
    type: str
    hal_layer: Optional[str] = None
    driver_layer: Optional[str] = None
    abstraction_layer: Optional[str] = None


class DriverGenerationResponse(BaseModel):
    id: str
    project_id: str
    drivers: List[DriverDefinition] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# 5. Communication Stack
class CommunicationStackRequest(BaseEmbeddedRequest):
    protocols: List[str] = Field(default_factory=list)


class CommunicationStackResponse(BaseModel):
    id: str
    project_id: str
    protocol_layers: Dict[str, Any] = Field(default_factory=dict)
    packet_definitions: Dict[str, Any] = Field(default_factory=dict)
    communication_frameworks: List[Dict[str, Any]] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# 6. State Machine
class StateMachineRequest(BaseEmbeddedRequest):
    state_machine_type: str = "finite"


class StateMachineResponse(BaseModel):
    id: str
    project_id: str
    states: List[Dict[str, Any]] = Field(default_factory=list)
    transitions: List[Dict[str, Any]] = Field(default_factory=list)
    conditions: List[Dict[str, Any]] = Field(default_factory=list)
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    recovery_logic: List[Dict[str, Any]] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# 7. Sensor Integration
class SensorIntegrationRequest(BaseEmbeddedRequest):
    sensor_types: List[str] = Field(default_factory=list)


class SensorIntegrationResponse(BaseModel):
    id: str
    project_id: str
    sensors: List[Dict[str, Any]] = Field(default_factory=list)
    calibration_logic: List[str] = Field(default_factory=list)
    filtering_logic: List[str] = Field(default_factory=list)
    health_monitoring: List[str] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# 8. Motor Control
class MotorControlRequest(BaseEmbeddedRequest):
    motor_types: List[str] = Field(default_factory=list)


class MotorControlResponse(BaseModel):
    id: str
    project_id: str
    motors: List[Dict[str, Any]] = Field(default_factory=list)
    control_loops: List[Dict[str, Any]] = Field(default_factory=list)
    pwm_structures: List[Dict[str, Any]] = Field(default_factory=list)
    safety_systems: List[str] = Field(default_factory=list)
    control_architectures: List[str] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# 9. Flight Controller
class FlightControllerRequest(BaseEmbeddedRequest):
    vehicle_type: str = "multirotor"


class FlightControllerResponse(BaseModel):
    id: str
    project_id: str
    flight_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    navigation_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    mission_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    control_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    sensor_fusion_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    failsafe_systems: List[str] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# 10. Robotics Controller
class RoboticsControllerRequest(BaseEmbeddedRequest):
    pass


class RoboticsControllerResponse(BaseModel):
    id: str
    project_id: str
    kinematics_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    motion_planning_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    actuator_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    safety_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    trajectory_controllers: List[Dict[str, Any]] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# 11. Code Generation
class CodeGenerationRequest(BaseEmbeddedRequest):
    language: str = "C"


class GeneratedCodeProject(BaseModel):
    project_structure: List[str] = Field(default_factory=list)
    modules: List[str] = Field(default_factory=list)
    interfaces: List[str] = Field(default_factory=list)
    configuration_files: List[str] = Field(default_factory=list)
    build_files: List[str] = Field(default_factory=list)


class CodeGenerationResponse(BaseModel):
    id: str
    project_id: str
    language: str
    code_project: GeneratedCodeProject
    execution_time_ms: Optional[float] = None
    created_at: datetime
