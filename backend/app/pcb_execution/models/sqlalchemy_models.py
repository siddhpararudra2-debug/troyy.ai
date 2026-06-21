"""
SQLAlchemy Models for PCB Execution
"""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class PCBExecutionProject(Base):
    __tablename__ = "pcb_execution_projects"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    config_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class SchematicExecution(Base):
    __tablename__ = "schematic_executions"

    id = Column(String, primary_key=True)
    pcb_execution_project_id = Column(String, ForeignKey("pcb_execution_projects.id"), nullable=False)
    components_json = Column(Text, default="[]")
    nets_json = Column(Text, default="[]")
    file_path = Column(String)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=func.now())


class PCBLayoutExecution(Base):
    __tablename__ = "pcb_layout_executions"

    id = Column(String, primary_key=True)
    pcb_execution_project_id = Column(String, ForeignKey("pcb_execution_projects.id"), nullable=False)
    schematic_id = Column(String, ForeignKey("schematic_executions.id"), nullable=False)
    board_width_mm = Column(Float, default=100)
    board_height_mm = Column(Float, default=80)
    placement_json = Column(Text, default="{}")
    routing_json = Column(Text, default="{}")
    file_path = Column(String)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=func.now())


class GerberExport(Base):
    __tablename__ = "gerber_exports"

    id = Column(String, primary_key=True)
    pcb_execution_project_id = Column(String, ForeignKey("pcb_execution_projects.id"), nullable=False)
    layout_id = Column(String, ForeignKey("pcb_layout_executions.id"), nullable=False)
    files_json = Column(Text, default="[]")
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=func.now())
