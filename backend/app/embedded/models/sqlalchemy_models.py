"""
Embedded Systems & Firmware SQLAlchemy Models
"""
from datetime import datetime
from sqlalchemy import Column, Text, Integer, Float, DateTime, ForeignKey
from app.core.database import Base


class FirmwareProject(Base):
    __tablename__ = "firmware_projects"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FirmwareArchitecture(Base):
    __tablename__ = "firmware_architectures"
    id = Column(Text, primary_key=True)
    firmware_project_id = Column(Text, ForeignKey("firmware_projects.id"))
    folder_structure_json = Column(Text, nullable=False, default="[]")
    module_architecture_json = Column(Text, nullable=False, default="{}")
    subsystem_design_json = Column(Text, nullable=False, default="{}")
    dependency_map_json = Column(Text, nullable=False, default="{}")
    boot_process_json = Column(Text, nullable=False, default="[]")
    initialization_flow_json = Column(Text, nullable=False, default="[]")
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class RTOSConfiguration(Base):
    __tablename__ = "rtos_configurations"
    id = Column(Text, primary_key=True)
    firmware_project_id = Column(Text, ForeignKey("firmware_projects.id"))
    rtos_type = Column(Text, nullable=False)
    tasks_json = Column(Text, nullable=False, default="[]")
    queues_json = Column(Text, nullable=False, default="[]")
    semaphores_json = Column(Text, nullable=False, default="[]")
    mutexes_json = Column(Text, nullable=False, default="[]")
    timers_json = Column(Text, nullable=False, default="[]")
    watchdogs_json = Column(Text, nullable=False, default="[]")
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class TaskDefinition(Base):
    __tablename__ = "task_definitions"
    id = Column(Text, primary_key=True)
    rtos_config_id = Column(Text, ForeignKey("rtos_configurations.id"))
    name = Column(Text, nullable=False)
    priority = Column(Integer, nullable=False)
    stack_size = Column(Integer, nullable=False)
    period_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class DriverDefinition(Base):
    __tablename__ = "driver_definitions"
    id = Column(Text, primary_key=True)
    firmware_project_id = Column(Text, ForeignKey("firmware_projects.id"))
    driver_type = Column(Text, nullable=False)
    hal_layer_json = Column(Text, nullable=False, default="{}")
    driver_layer_json = Column(Text, nullable=False, default="{}")
    abstraction_layer_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)


class CommunicationStack(Base):
    __tablename__ = "communication_stacks"
    id = Column(Text, primary_key=True)
    firmware_project_id = Column(Text, ForeignKey("firmware_projects.id"))
    protocol_layers_json = Column(Text, nullable=False, default="{}")
    packet_definitions_json = Column(Text, nullable=False, default="{}")
    communication_frameworks_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class StateMachine(Base):
    __tablename__ = "state_machines"
    id = Column(Text, primary_key=True)
    firmware_project_id = Column(Text, ForeignKey("firmware_projects.id"))
    type = Column(Text, nullable=False)
    states_json = Column(Text, nullable=False, default="[]")
    transitions_json = Column(Text, nullable=False, default="[]")
    conditions_json = Column(Text, nullable=False, default="[]")
    actions_json = Column(Text, nullable=False, default="[]")
    recovery_logic_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class FlightControllerArchitecture(Base):
    __tablename__ = "flight_controller_architectures"
    id = Column(Text, primary_key=True)
    firmware_project_id = Column(Text, ForeignKey("firmware_projects.id"))
    vehicle_type = Column(Text, nullable=False)
    flight_tasks_json = Column(Text, nullable=False, default="[]")
    navigation_tasks_json = Column(Text, nullable=False, default="[]")
    mission_tasks_json = Column(Text, nullable=False, default="[]")
    control_tasks_json = Column(Text, nullable=False, default="[]")
    sensor_fusion_tasks_json = Column(Text, nullable=False, default="[]")
    failsafe_systems_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class RoboticsControllerArchitecture(Base):
    __tablename__ = "robotics_controller_architectures"
    id = Column(Text, primary_key=True)
    firmware_project_id = Column(Text, ForeignKey("firmware_projects.id"))
    kinematics_tasks_json = Column(Text, nullable=False, default="[]")
    motion_planning_tasks_json = Column(Text, nullable=False, default="[]")
    actuator_tasks_json = Column(Text, nullable=False, default="[]")
    safety_tasks_json = Column(Text, nullable=False, default="[]")
    trajectory_controllers_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class GeneratedCodeProject(Base):
    __tablename__ = "generated_code_projects"
    id = Column(Text, primary_key=True)
    firmware_project_id = Column(Text, ForeignKey("firmware_projects.id"))
    language = Column(Text, nullable=False)
    project_structure_json = Column(Text, nullable=False, default="[]")
    modules_json = Column(Text, nullable=False, default="[]")
    interfaces_json = Column(Text, nullable=False, default="[]")
    configuration_files_json = Column(Text, nullable=False, default="[]")
    build_files_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)
