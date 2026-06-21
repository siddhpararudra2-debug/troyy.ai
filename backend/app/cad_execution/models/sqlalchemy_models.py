"""
SQLAlchemy Models for CAD Execution
"""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class CADExecutionProject(Base):
    __tablename__ = "cad_execution_projects"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    engine = Column(String, nullable=False, default="cadquery")  # cadquery, freecad
    config_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class CADPartExecution(Base):
    __tablename__ = "cad_part_executions"

    id = Column(String, primary_key=True)
    cad_execution_project_id = Column(String, ForeignKey("cad_execution_projects.id"), nullable=False)
    part_name = Column(String, nullable=False)
    part_type = Column(String, nullable=False)
    geometry_json = Column(Text, default="{}")
    parametric_dimensions_json = Column(Text, default="{}")
    material = Column(String, default="aluminum")
    status = Column(String, nullable=False, default="pending")
    file_path = Column(String)
    created_at = Column(DateTime, default=func.now())


class CADAssemblyExecution(Base):
    __tablename__ = "cad_assembly_executions"

    id = Column(String, primary_key=True)
    cad_execution_project_id = Column(String, ForeignKey("cad_execution_projects.id"), nullable=False)
    assembly_name = Column(String, nullable=False)
    parts_json = Column(Text, default="[]")
    mates_json = Column(Text, default="[]")
    status = Column(String, nullable=False, default="pending")
    file_path = Column(String)
    created_at = Column(DateTime, default=func.now())


class CADExport(Base):
    __tablename__ = "cad_exports"

    id = Column(String, primary_key=True)
    cad_execution_project_id = Column(String, ForeignKey("cad_execution_projects.id"), nullable=False)
    part_or_assembly_id = Column(String, nullable=False)
    export_format = Column(String, nullable=False)  # step, stl, iges, obj, gltf, fcstd
    file_path = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=func.now())


class CADValidationResult(Base):
    __tablename__ = "cad_validation_results"

    id = Column(String, primary_key=True)
    cad_execution_project_id = Column(String, ForeignKey("cad_execution_projects.id"), nullable=False)
    part_or_assembly_id = Column(String, nullable=False)
    validation_type = Column(String, nullable=False)  # geometry, mass_properties, gdnt, manufacturability
    is_valid = Column(Integer, default=1)
    issues_json = Column(Text, default="[]")
    mass_properties_json = Column(Text, default="{}")
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=func.now())
