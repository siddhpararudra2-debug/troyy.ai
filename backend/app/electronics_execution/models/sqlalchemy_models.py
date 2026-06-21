"""
SQLAlchemy Models for Electronics Execution
"""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class ElectronicsArchitecture(Base):
    __tablename__ = "electronics_architectures"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    power_tree_json = Column(Text, default="{}")
    signal_chain_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=func.now())


class PowerSystemDesign(Base):
    __tablename__ = "power_system_designs"

    id = Column(String, primary_key=True)
    electronics_architecture_id = Column(String, ForeignKey("electronics_architectures.id"), nullable=False)
    voltages_json = Column(Text, default="[]")
    regulators_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=func.now())


class SignalChainDesign(Base):
    __tablename__ = "signal_chain_designs"

    id = Column(String, primary_key=True)
    electronics_architecture_id = Column(String, ForeignKey("electronics_architectures.id"), nullable=False)
    sensors_json = Column(Text, default="[]")
    interfaces_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=func.now())
