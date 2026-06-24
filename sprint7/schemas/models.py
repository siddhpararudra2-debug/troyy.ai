from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

class WorkOrder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    part_number: str
    quantity: int
    priority: int = Field(ge=1, le=5, default=3)
    state: str = "CREATED"
    assigned_machine: Optional[str] = None
    assigned_operator: Optional[str] = None
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    process_plan_id: Optional[str] = None
    quality_status: str = "PENDING"
    serial_numbers: List[str] = Field(default_factory=list)
    notes: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProductionRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    work_order_id: str
    serial_number: str
    operation_sequence: int
    operation_name: str
    machine_id: Optional[str] = None
    operator_id: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    quality_result: str = "PENDING"
    defects: List[str] = Field(default_factory=list)

class Machine(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    machine_type: str  # "CNC_MILL", "3D_PRINTER", "PICK_AND_PLACE", etc.
    state: str = "IDLE"
    capabilities: List[str] = Field(default_factory=list)
    current_job: Optional[str] = None
    utilization_pct: float = 0.0
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    mqtt_topic: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)

class HILTest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    hardware_id: str
    autopilot: str  # "PX4" or "ARDUPILOT"
    state: str = "IDLE"
    test_plan: List[Dict[str, Any]] = Field(default_factory=list)
    current_step: int = 0
    results: Dict[str, Any] = Field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    connection_params: Dict[str, Any] = Field(default_factory=dict)

class FlightMission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    vehicle_id: str
    autopilot: str
    waypoints: List[Dict[str, Any]] = Field(default_factory=list)
    state: str = "PLANNED"
    uploaded: bool = False
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    flight_log: List[Dict[str, Any]] = Field(default_factory=list)

class TelemetryRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    vehicle_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    altitude_m: float
    roll_deg: float = 0.0
    pitch_deg: float = 0.0
    yaw_deg: float = 0.0
    ground_speed_ms: float = 0.0
    battery_pct: float = 100.0
    flight_mode: str = "MANUAL"
    additional: Dict[str, Any] = Field(default_factory=dict)

class QualificationTest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    qualification_level: str
    test_procedure: str
    acceptance_criteria: List[str] = Field(default_factory=list)
    state: str = "PENDING"
    results: Dict[str, Any] = Field(default_factory=dict)
    evidence: List[str] = Field(default_factory=list)
    approved_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DeploymentPackage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    vehicle_id: str
    state: str = "PLANNED"
    design_version: str
    firmware_version: str
    manufacturing_batch: Optional[str] = None
    qualification_id: Optional[str] = None
    commissioning_checklist: List[Dict[str, Any]] = Field(default_factory=list)
    deployment_date: Optional[datetime] = None
    operational_hours: float = 0.0
    maintenance_due: Optional[datetime] = None

class ReliabilityRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    vehicle_id: str
    component: str
    operating_hours: float
    failures: int = 0
    mtbf_hours: Optional[float] = None
    weibull_shape: Optional[float] = None
    weibull_scale: Optional[float] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class FailureEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    vehicle_id: str
    component: str
    failure_mode: str
    severity: str  # "MINOR", "MAJOR", "CRITICAL"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    operating_hours_at_failure: float
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None

class MaintenanceTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    vehicle_id: str
    task_type: str  # "PREVENTIVE", "CORRECTIVE", "PREDICTIVE"
    description: str
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    performed_by: Optional[str] = None
    status: str = "SCHEDULED"
    notes: str = ""
