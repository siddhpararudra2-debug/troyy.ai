from sqlalchemy import Column, String, DateTime, JSON, Uuid
from sqlalchemy.orm import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class SchematicProject(Base):
    __tablename__ = "schematic_projects"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class GeneratedSchematic(Base):
    __tablename__ = "generated_schematics"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(Uuid(as_uuid=True), nullable=False)
    schematic_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ErcResult(Base):
    __tablename__ = "erc_results"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schematic_id = Column(Uuid(as_uuid=True), nullable=False)
    erc_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
