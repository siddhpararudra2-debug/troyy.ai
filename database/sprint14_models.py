"""Sprint 14 Database Models - Robotics & Autonomous Systems."""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from enum import Enum as PyEnum

Base = declarative_base()


class RobotType(PyEnum):
    MOBILE = "mobile"
    MANIPULATOR = "manipulator"
    UAV = "uav"
    UGV = "ugv"
    HUMANOID = "humanoid"
    HYBRID = "hybrid"


class RobotStatus(PyEnum):
    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class Robot(Base):
    """Robot database model."""
    __tablename__ = "sprint14_robots"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    robot_type = Column(String, nullable=False)  # Uses RobotType values
    status = Column(String, default=RobotStatus.IDLE.value)
    description = Column(String)
    serial_number = Column(String, unique=True)
    manufacturer = Column(String)
    model = Column(String)
    capabilities = Column(JSON, default=list)
    current_location = Column(JSON)
    health_score = Column(Float, default=1.0)
    battery_level = Column(Float, default=100.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)
    last_modified = Column(DateTime, default=datetime.utcnow)
    modified_by = Column(String)
    version = Column(Integer, default=1)


class RobotConfiguration(Base):
    """Robot configuration database model."""
    __tablename__ = "sprint14_robot_configurations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    robot_id = Column(String, ForeignKey("sprint14_robots.id"))
    name = Column(String, nullable=False)
    config_data = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    version = Column(Integer, default=1)


class SensorType(PyEnum):
    CAMERA = "camera"
    STEREO_CAMERA = "stereo_camera"
    RGB_D = "rgb_d"
    IMU = "imu"
    GPS = "gps"
    LIDAR = "lidar"
    RADAR = "radar"
    ENCODER = "encoder"
    ULTRASONIC = "ultrasonic"


class Sensor(Base):
    """Sensor database model."""
    __tablename__ = "sprint14_sensors"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    robot_id = Column(String, ForeignKey("sprint14_robots.id"))
    name = Column(String, nullable=False)
    sensor_type = Column(String, nullable=False)  # Uses SensorType values
    model = Column(String)
    manufacturer = Column(String)
    mount_location = Column(JSON)
    calibration_data = Column(JSON)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow)


class MapType(PyEnum):
    VISUAL = "visual"
    LIDAR = "lidar"
    OCCUPANCY_GRID = "occupancy_grid"
    TOPOLOGICAL = "topological"
    MULTI_SENSOR = "multi_sensor"


class Map(Base):
    """Map database model."""
    __tablename__ = "sprint14_maps"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    map_type = Column(String, nullable=False)  # Uses MapType values
    map_data = Column(JSON)
    resolution = Column(Float)
    origin = Column(JSON)
    bounds = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)
    last_modified = Column(DateTime, default=datetime.utcnow)
    version = Column(Integer, default=1)


class Mission(Base):
    """Mission database model for robotics."""
    __tablename__ = "sprint14_missions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String)
    mission_type = Column(String)
    status = Column(String, default="pending")
    assigned_robots = Column(JSON, default=list)
    objectives = Column(JSON, default=list)
    parameters = Column(JSON, default=dict)
    planned_start = Column(DateTime)
    planned_end = Column(DateTime)
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)
    last_modified = Column(DateTime, default=datetime.utcnow)
    version = Column(Integer, default=1)


class Trajectory(Base):
    """Trajectory database model."""
    __tablename__ = "sprint14_trajectories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mission_id = Column(String, ForeignKey("sprint14_missions.id"))
    robot_id = Column(String, ForeignKey("sprint14_robots.id"))
    name = Column(String)
    waypoints = Column(JSON, nullable=False)
    velocity_profile = Column(JSON)
    duration = Column(Float)
    safety_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    version = Column(Integer, default=1)


class LocalizationRecord(Base):
    """Localization record database model."""
    __tablename__ = "sprint14_localization_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    robot_id = Column(String, ForeignKey("sprint14_robots.id"))
    map_id = Column(String, ForeignKey("sprint14_maps.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    pose = Column(JSON, nullable=False)
    covariance = Column(JSON)
    confidence = Column(Float, default=1.0)


class Detection(Base):
    """Object detection database model."""
    __tablename__ = "sprint14_detections"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    robot_id = Column(String, ForeignKey("sprint14_robots.id"))
    sensor_id = Column(String, ForeignKey("sprint14_sensors.id"))
    mission_id = Column(String, ForeignKey("sprint14_missions.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    object_class = Column(String, nullable=False)
    bounding_box = Column(JSON)
    segmentation_mask = Column(JSON)
    confidence = Column(Float, default=0.5)
    pose = Column(JSON)


class Fleet(Base):
    """Fleet database model."""
    __tablename__ = "sprint14_fleets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String)
    robot_ids = Column(JSON, default=list)
    status = Column(String, default="idle")
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)
    last_modified = Column(DateTime, default=datetime.utcnow)
    version = Column(Integer, default=1)


class RobotTwin(Base):
    """Robot digital twin database model."""
    __tablename__ = "sprint14_robot_twins"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    robot_id = Column(String, ForeignKey("sprint14_robots.id"))
    twin_state = Column(JSON, nullable=False)
    last_sync = Column(DateTime, default=datetime.utcnow)
    predicted_state = Column(JSON)
    anomalies = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class OperatorSession(Base):
    """Operator session database model."""
    __tablename__ = "sprint14_operator_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    operator_id = Column(String, nullable=False)
    robot_ids = Column(JSON, default=list)
    mission_ids = Column(JSON, default=list)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    interaction_log = Column(JSON, default=list)


class BehaviorTree(Base):
    """Behavior tree database model."""
    __tablename__ = "sprint14_behavior_trees"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String)
    tree_data = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)
    version = Column(Integer, default=1)
