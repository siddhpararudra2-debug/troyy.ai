"""
Manufacturing Intelligence Platform SQLAlchemy Models
"""
from datetime import datetime
from sqlalchemy import Column, Text, Float, Integer, DateTime, ForeignKey
from app.core.database import Base


class BillOfMaterial(Base):
    __tablename__ = "bill_of_materials"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    items_json = Column(Text, nullable=False, default="[]")
    total_items = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    part_number = Column(Text, nullable=False)
    lead_time_days = Column(Integer, default=7)
    price = Column(Float, default=0.0)
    availability = Column(Text, default="in_stock")
    created_at = Column(DateTime, default=datetime.utcnow)


class ProcurementPlan(Base):
    __tablename__ = "procurement_plans"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    purchase_orders_json = Column(Text, nullable=False, default="[]")
    supplier_list_json = Column(Text, nullable=False, default="[]")
    lead_times_json = Column(Text, nullable=False, default="{}")
    critical_components_json = Column(Text, nullable=False, default="[]")
    procurement_risks_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class CostEstimate(Base):
    __tablename__ = "cost_estimates"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    materials = Column(Float, default=0.0)
    machining = Column(Float, default=0.0)
    printing = Column(Float, default=0.0)
    electronics = Column(Float, default=0.0)
    pcb = Column(Float, default=0.0)
    labor = Column(Float, default=0.0)
    testing = Column(Float, default=0.0)
    logistics = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    unit_cost = Column(Float, default=0.0)
    batch_size = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


class ManufacturingPlan(Base):
    __tablename__ = "manufacturing_plans"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    production_level = Column(Text, default="prototype")
    fabrication_steps_json = Column(Text, nullable=False, default="[]")
    assembly_steps_json = Column(Text, nullable=False, default="[]")
    testing_steps_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class CNCRoute(Base):
    __tablename__ = "cnc_routes"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    operations_json = Column(Text, nullable=False, default="[]")
    tool_selection_json = Column(Text, nullable=False, default="[]")
    cycle_time_min = Column(Float, default=0.0)
    dfm_recommendations_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class PrintPlan(Base):
    __tablename__ = "print_plans"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    technology = Column(Text, default="FDM")
    orientation = Column(Text, nullable=False)
    support_strategy = Column(Text, nullable=False)
    material = Column(Text, nullable=False)
    print_time_hours = Column(Float, default=0.0)
    recommendations_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    risks_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class BuildPackage(Base):
    __tablename__ = "build_packages"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    cad_files_json = Column(Text, nullable=False, default="[]")
    drawings_json = Column(Text, nullable=False, default="[]")
    bom_id = Column(Text, nullable=True)
    assembly_instructions = Column(Text, nullable=True)
    manufacturing_plans_json = Column(Text, nullable=False, default="[]")
    testing_plans_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)
