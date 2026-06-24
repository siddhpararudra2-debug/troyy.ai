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
    requirements_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CADPart(Base):
    __tablename__ = "cad_parts"
    id = Column(Text, primary_key=True)
    cad_project_id = Column(Text, ForeignKey("cad_projects.id"))
    name = Column(Text, nullable=False)
    part_type = Column(Text, nullable=False)
    material_id = Column(Text, ForeignKey("materials.id"))
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
    gdnt_json = Column(Text, nullable=False, default="[]")
    notes_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class Material(Base):
    __tablename__ = "materials"
    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    density_kgm3 = Column(Float, nullable=False)
    youngs_modulus_pa = Column(Float)
    yield_strength_pa = Column(Float)
    ultimate_strength_pa = Column(Float)
    cost_per_kg = Column(Float)
    categories_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class Fastener(Base):
    __tablename__ = "fasteners"
    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    size = Column(Text, nullable=False)
    material_id = Column(Text, ForeignKey("materials.id"))
    cost = Column(Float)
    supplier = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class BOM(Base):
    __tablename__ = "boms"
    id = Column(Text, primary_key=True)
    assembly_id = Column(Text, ForeignKey("cad_assemblies.id"))
    name = Column(Text, nullable=False)
    items_json = Column(Text, nullable=False, default="[]")
    total_cost = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class CostEstimate(Base):
    __tablename__ = "cost_estimates"
    id = Column(Text, primary_key=True)
    bom_id = Column(Text, ForeignKey("boms.id"))
    material_cost = Column(Float)
    labor_cost = Column(Float)
    overhead_cost = Column(Float)
    total_cost = Column(Float)
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
    gdnt_json = Column(Text, nullable=False, default="[]")
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


class StandardPart(Base):
    __tablename__ = "standard_parts"
    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    category = Column(Text, nullable=False)
    part_number = Column(Text)
    specifications_json = Column(Text, nullable=False, default="{}")
    cost = Column(Float)
    supplier = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class ManufacturingPackage(Base):
    __tablename__ = "manufacturing_packages"
    id = Column(Text, primary_key=True)
    cad_project_id = Column(Text, ForeignKey("cad_projects.id"))
    assembly_id = Column(Text, ForeignKey("cad_assemblies.id"))
    bom_id = Column(Text, ForeignKey("boms.id"))
    name = Column(Text, nullable=False)
    files_json = Column(Text, nullable=False, default="[]")  # Paths to step/stl/obj/pdf etc.
    drawings_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
