"""
CAD Generation & Engineering Geometry SQLAlchemy Models
"""
from datetime import datetime
from sqlalchemy import Column, Text, Float, Integer, DateTime, ForeignKey
from app.core.database import Base


class CADProject(Base):
    __tablename__ = "cad_projects"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CADPart(Base):
    __tablename__ = "cad_parts"
    id = Column(Text, primary_key=True)
    cad_project_id = Column(Text, ForeignKey("cad_projects.id"))
    name = Column(Text, nullable=False)
    part_type = Column(Text, nullable=False)
    features_json = Column(Text, nullable=False, default="[]")
    constraints_json = Column(Text, nullable=False, default="[]")
    parametric_dimensions_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)


class CADAssembly(Base):
    __tablename__ = "cad_assemblies"
    id = Column(Text, primary_key=True)
    cad_project_id = Column(Text, ForeignKey("cad_projects.id"))
    name = Column(Text, nullable=False)
    parts_json = Column(Text, nullable=False, default="[]")
    mates_json = Column(Text, nullable=False, default="[]")
    joints_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class CADDrawing(Base):
    __tablename__ = "cad_drawings"
    id = Column(Text, primary_key=True)
    cad_project_id = Column(Text, ForeignKey("cad_projects.id"))
    name = Column(Text, nullable=False)
    part_id = Column(Text)
    assembly_id = Column(Text)
    views_json = Column(Text, nullable=False, default="[]")
    dimensions_json = Column(Text, nullable=False, default="[]")
    notes_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class MassProperty(Base):
    __tablename__ = "mass_properties"
    id = Column(Text, primary_key=True)
    part_id = Column(Text)
    assembly_id = Column(Text)
    mass_kg = Column(Float)
    cog_x = Column(Float)
    cog_y = Column(Float)
    cog_z = Column(Float)
    volume_m3 = Column(Float)
    surface_area_m2 = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class ToleranceAnalysis(Base):
    __tablename__ = "tolerance_analyses"
    id = Column(Text, primary_key=True)
    part_id = Column(Text)
    tolerances_json = Column(Text, nullable=False, default="[]")
    gdt_json = Column(Text, nullable=False, default="[]")
    stackups_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class ManufacturingReview(Base):
    __tablename__ = "manufacturing_reviews"
    id = Column(Text, primary_key=True)
    part_id = Column(Text)
    constraints_json = Column(Text, nullable=False, default="[]")
    dfm_json = Column(Text, nullable=False, default="[]")
    recommendations_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class CADRevision(Base):
    __tablename__ = "cad_revisions"
    id = Column(Text, primary_key=True)
    cad_project_id = Column(Text, ForeignKey("cad_projects.id"))
    version = Column(Text, nullable=False)
    changes_json = Column(Text, nullable=False, default="[]")
    approvals_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)
