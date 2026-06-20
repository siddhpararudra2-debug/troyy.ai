"""
Electronics Intelligence SQLAlchemy Models
"""

from datetime import datetime
from sqlalchemy import Column, Text, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ComponentLibrary(Base):
    """Component library model for storing all electronic components."""

    __tablename__ = "component_library"

    id = Column(Text, primary_key=True)
    component_type = Column(Text, nullable=False)  # mcu, sensor, regulator, mosfet, communication
    manufacturer = Column(Text, nullable=False)
    part_number = Column(Text, nullable=False, unique=True)
    description = Column(Text)
    specifications_json = Column(Text, nullable=False, default='{}')  # JSON of specs
    package = Column(Text)
    operating_voltage_min = Column(Float)
    operating_voltage_max = Column(Float)
    operating_current_max = Column(Float)
    operating_temp_min = Column(Float)
    operating_temp_max = Column(Float)
    interfaces_json = Column(Text, default='[]')
    cost_usd = Column(Float)
    availability_score = Column(Float, default=1.0)
    datasheet_url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class ComponentRecommendation(Base):
    """Component recommendation result model."""

    __tablename__ = "component_recommendations"

    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    component_type = Column(Text, nullable=False)
    requirements_json = Column(Text, nullable=False, default='{}')
    constraints_json = Column(Text, nullable=False, default='{}')
    selected_component_id = Column(Text, ForeignKey("component_library.id"))
    alternatives_json = Column(Text, nullable=False, default='[]')
    engineering_justification_json = Column(Text, nullable=False, default='{}')
    tradeoffs_json = Column(Text, nullable=False, default='[]')
    performance_analysis_json = Column(Text, nullable=False, default='{}')
    cost_analysis_json = Column(Text, nullable=False, default='{}')
    availability_analysis_json = Column(Text, nullable=False, default='{}')
    validation_results_json = Column(Text, nullable=False, default='{}')
    documentation_json = Column(Text, nullable=False, default='{}')
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    selected_component = relationship("ComponentLibrary")


class MicrocontrollerRecommendation(Base):
    """Microcontroller recommendation result model."""

    __tablename__ = "microcontroller_recommendations"

    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    requirements_json = Column(Text, nullable=False, default='{}')
    selected_mcu_id = Column(Text, ForeignKey("component_library.id"))
    alternatives_json = Column(Text, nullable=False, default='[]')
    gpio_analysis_json = Column(Text, nullable=False, default='{}')
    adc_analysis_json = Column(Text, nullable=False, default='{}')
    pwm_analysis_json = Column(Text, nullable=False, default='{}')
    memory_analysis_json = Column(Text, nullable=False, default='{}')
    communication_analysis_json = Column(Text, nullable=False, default='{}')
    justification_json = Column(Text, nullable=False, default='{}')
    tradeoffs_json = Column(Text, nullable=False, default='[]')
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    selected_mcu = relationship("ComponentLibrary")


class SensorRecommendation(Base):
    """Sensor recommendation result model."""

    __tablename__ = "sensor_recommendations"

    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    sensor_type = Column(Text, nullable=False)
    requirements_json = Column(Text, nullable=False, default='{}')
    selected_sensor_id = Column(Text, ForeignKey("component_library.id"))
    alternatives_json = Column(Text, nullable=False, default='[]')
    justification_json = Column(Text, nullable=False, default='{}')
    tradeoffs_json = Column(Text, nullable=False, default='[]')
    performance_analysis_json = Column(Text, nullable=False, default='{}')
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    selected_sensor = relationship("ComponentLibrary")


class RegulatorRecommendation(Base):
    """Regulator recommendation result model."""

    __tablename__ = "regulator_recommendations"

    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    regulator_type = Column(Text, nullable=False)
    requirements_json = Column(Text, nullable=False, default='{}')
    selected_regulator_id = Column(Text, ForeignKey("component_library.id"))
    alternatives_json = Column(Text, nullable=False, default='[]')
    power_dissipation_analysis_json = Column(Text, nullable=False, default='{}')
    efficiency_analysis_json = Column(Text, nullable=False, default='{}')
    thermal_analysis_json = Column(Text, nullable=False, default='{}')
    justification_json = Column(Text, nullable=False, default='{}')
    tradeoffs_json = Column(Text, nullable=False, default='[]')
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    selected_regulator = relationship("ComponentLibrary")


class MosfetRecommendation(Base):
    """MOSFET recommendation result model."""

    __tablename__ = "mosfet_recommendations"

    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    requirements_json = Column(Text, nullable=False, default='{}')
    selected_mosfet_id = Column(Text, ForeignKey("component_library.id"))
    alternatives_json = Column(Text, nullable=False, default='[]')
    voltage_analysis_json = Column(Text, nullable=False, default='{}')
    current_analysis_json = Column(Text, nullable=False, default='{}')
    switching_analysis_json = Column(Text, nullable=False, default='{}')
    thermal_analysis_json = Column(Text, nullable=False, default='{}')
    justification_json = Column(Text, nullable=False, default='{}')
    tradeoffs_json = Column(Text, nullable=False, default='[]')
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    selected_mosfet = relationship("ComponentLibrary")


class CommunicationRecommendation(Base):
    """Communication protocol recommendation result model."""

    __tablename__ = "communication_recommendations"

    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    requirements_json = Column(Text, nullable=False, default='{}')
    selected_protocol = Column(Text, nullable=False)
    alternatives_json = Column(Text, nullable=False, default='[]')
    justification_json = Column(Text, nullable=False, default='{}')
    tradeoffs_json = Column(Text, nullable=False, default='[]')
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class CompatibilityAnalysis(Base):
    """Compatibility analysis result model."""

    __tablename__ = "compatibility_analyses"

    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    components_json = Column(Text, nullable=False, default='[]')
    voltage_compatibility_json = Column(Text, nullable=False, default='{}')
    current_compatibility_json = Column(Text, nullable=False, default='{}')
    logic_level_compatibility_json = Column(Text, nullable=False, default='{}')
    communication_compatibility_json = Column(Text, nullable=False, default='{}')
    thermal_compatibility_json = Column(Text, nullable=False, default='{}')
    overall_compatibility_score = Column(Float, nullable=False)
    issues_json = Column(Text, nullable=False, default='[]')
    recommendations_json = Column(Text, nullable=False, default='[]')
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class ElectronicsArchitecture(Base):
    """Electronics architecture generation result model."""

    __tablename__ = "electronics_architectures"

    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    requirements_json = Column(Text, nullable=False, default='{}')
    power_tree_json = Column(Text, nullable=False, default='{}')
    signal_architecture_json = Column(Text, nullable=False, default='{}')
    communication_architecture_json = Column(Text, nullable=False, default='{}')
    subsystem_architecture_json = Column(Text, nullable=False, default='{}')
    components_json = Column(Text, nullable=False, default='[]')
    documentation_json = Column(Text, nullable=False, default='{}')
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
