"""
CAD Orchestrator - Main entry point for CAD execution
"""
import uuid
import time
from datetime import datetime
from typing import Dict, Any, Optional
from app.core.config import settings
from .cadquery_service import CadQueryService
from .freecad_service import FreeCADService
from .geometry_builder import GeometryBuilder
from .assembly_builder import AssemblyBuilder
from .drawing_generator import DrawingGenerator
from .export_service import ExportService
from .cad_validation_service import CADValidationService


class CADOrchestrator:
    """
    Orchestrates the entire CAD generation pipeline
    """

    def __init__(self):
        self.cadquery_service = CadQueryService()
        self.freecad_service = FreeCADService()
        self.geometry_builder = GeometryBuilder()
        self.assembly_builder = AssemblyBuilder()
        self.drawing_generator = DrawingGenerator()
        self.export_service = ExportService()
        self.validation_service = CADValidationService()

    def create_project(
        self,
        project_id: str,
        name: str,
        engine: str = "cadquery",
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new CAD execution project
        """
        config = config or {}
        cad_project_id = str(uuid.uuid4())
        
        return {
            "id": cad_project_id,
            "project_id": project_id,
            "name": name,
            "status": "pending",
            "engine": engine,
            "config": config,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

    def generate_part(
        self,
        cad_execution_project_id: str,
        part_name: str,
        part_type: str = "bracket",
        parametric_dimensions: Optional[Dict[str, float]] = None,
        material: str = "aluminum",
        engine: str = "cadquery"
    ) -> Dict[str, Any]:
        """
        Generate a CAD part using the specified engine
        """
        parametric_dimensions = parametric_dimensions or {}
        
        if engine == "cadquery":
            result = self.cadquery_service.generate_part(
                part_name=part_name,
                part_type=part_type,
                parametric_dimensions=parametric_dimensions,
                material=material
            )
        elif engine == "freecad":
            result = self.freecad_service.generate_part(
                part_name=part_name,
                part_type=part_type,
                parametric_dimensions=parametric_dimensions,
                material=material
            )
        else:
            raise ValueError(f"Unsupported CAD engine: {engine}")
        
        return {
            "id": result["id"],
            "cad_execution_project_id": cad_execution_project_id,
            "part_name": result["part_name"],
            "part_type": result["part_type"],
            "geometry": result["geometry"],
            "parametric_dimensions": result["parametric_dimensions"],
            "material": result["material"],
            "status": result["status"],
            "file_path": result.get("file_path"),
            "created_at": datetime.utcnow()
        }

    def generate_assembly(
        self,
        cad_execution_project_id: str,
        assembly_name: str,
        parts: Optional[list] = None,
        mates: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Generate a CAD assembly
        """
        assembly = self.assembly_builder.build_assembly(
            assembly_name=assembly_name,
            parts=parts or [],
            mates=mates
        )
        
        return {
            "id": assembly["id"],
            "cad_execution_project_id": cad_execution_project_id,
            "assembly_name": assembly["name"],
            "parts": assembly["parts"],
            "mates": assembly["mates"],
            "status": assembly["status"],
            "file_path": assembly.get("file_path"),
            "created_at": datetime.utcnow()
        }

    def export(
        self,
        cad_execution_project_id: str,
        part_or_assembly_id: str,
        export_format: str = "step"
    ) -> Dict[str, Any]:
        """
        Export a CAD model
        """
        export = self.export_service.export(
            part_or_assembly_id=part_or_assembly_id,
            export_format=export_format
        )
        
        return {
            "id": export["id"],
            "cad_execution_project_id": cad_execution_project_id,
            "part_or_assembly_id": export["part_or_assembly_id"],
            "export_format": export["export_format"],
            "file_path": export["file_path"],
            "status": export["status"],
            "created_at": datetime.utcnow()
        }

    def validate(
        self,
        cad_execution_project_id: str,
        part_or_assembly_id: str,
        validation_type: str = "geometry",
        geometry: Optional[Dict[str, Any]] = None,
        material: str = "aluminum"
    ) -> Dict[str, Any]:
        """
        Validate a CAD model
        """
        if validation_type == "geometry":
            result = self.validation_service.validate_geometry(
                part_or_assembly_id=part_or_assembly_id,
                geometry=geometry or {}
            )
        elif validation_type == "mass_properties":
            result = self.validation_service.calculate_mass_properties(
                part_or_assembly_id=part_or_assembly_id,
                geometry=geometry or {},
                material=material
            )
        elif validation_type == "manufacturability":
            result = self.validation_service.validate_manufacturability(
                part_or_assembly_id=part_or_assembly_id,
                geometry=geometry or {}
            )
        else:
            raise ValueError(f"Unsupported validation type: {validation_type}")
        
        return {
            "id": result["id"],
            "cad_execution_project_id": cad_execution_project_id,
            "part_or_assembly_id": result["part_or_assembly_id"],
            "validation_type": result["validation_type"],
            "is_valid": result["is_valid"],
            "issues": result["issues"],
            "mass_properties": result.get("mass_properties"),
            "execution_time_ms": result["execution_time_ms"],
            "created_at": datetime.utcnow()
        }
