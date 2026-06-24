"""
CAD Generation & Geometry Tests - Sprint 3
"""
from app.cad.services.cad_orchestrator import CADOrchestrator
from app.cad.services.geometry_engine import GeometryEngine
from app.cad.services.parametric_generator import ParametricGenerator
from app.cad.services.feature_generator import FeatureGenerator
from app.cad.services.export_manager import ExportManager
from app.cad.services.cadquery_engine import CadQueryEngine
from app.cad.services.freecad_engine import FreeCADEngine
from app.cad.services.mechanical_reasoner import MechanicalReasoner, MaterialSelector
from app.cad.services.component_library import ComponentLibrary
from app.cad.services.assembly_generator import AssemblyGenerator
from app.cad.services.drawing_generator import DrawingGenerator
from app.cad.services.bom_generator import BOMGenerator
from app.cad.schemas.schemas import (
    CADGenerateRequest, CADPartRequest, CADAssemblyRequest, 
    CADDrawingRequest, BOMGenerateRequest, MechanicalAnalysisRequest
)


def test_cad_orchestrator():
    """Test the main CAD orchestrator"""
    orchestrator = CADOrchestrator()
    requirements = {
        "name": "Test Project",
        "dimensions": {"length": 10, "width": 10, "height": 10}
    }
    # For async functions, we'd use pytest-asyncio, but placeholder test
    assert orchestrator is not None
    assert hasattr(orchestrator, 'geometry_engine')
    assert hasattr(orchestrator, 'parametric_generator')


def test_geometry_engine():
    """Test geometry engine operations"""
    engine = GeometryEngine()
    
    # Test sketch creation
    sketch = engine.create_sketch(plane="XY", origin=(0, 0, 0))
    assert sketch is not None
    assert "id" in sketch
    
    # Test adding rectangle
    sketch_with_rect = engine.add_rectangle(sketch, (0, 0), 20, 10)
    assert len(sketch_with_rect["entities"]) == 1
    
    # Test extrude
    solid = engine.extrude(sketch_with_rect, 5)
    assert solid is not None
    assert "id" in solid


def test_parametric_generator():
    """Test parametric generator"""
    generator = ParametricGenerator()
    
    # Test parameter definition
    param = generator.define_parameter("width", 50.0, 10.0, 100.0)
    assert param["name"] == "width"
    assert param["value"] == 50.0
    
    # Test apply parameters
    geometry = {"type": "solid"}
    parametric_model = generator.apply_parameters(geometry, {"width": 50, "height": 30})
    assert parametric_model["parametric"] is True
    assert "parameters" in parametric_model


def test_feature_generator():
    """Test feature generator"""
    generator = FeatureGenerator()
    
    # Test creating hole
    hole = generator.create_hole([10, 10, 0], 5.0)
    assert hole["type"] == "hole"
    assert hole["diameter"] == 5.0
    
    # Test creating fillet
    fillet = generator.create_fillet([1, 2, 3], 2.0)
    assert fillet["type"] == "fillet"


def test_export_manager():
    """Test export manager"""
    manager = ExportManager()
    
    # Test supported formats
    supported = manager.get_supported_formats()
    assert "step" in supported
    assert "stl" in supported
    
    # Test model export (placeholder)
    model = {"name": "TestModel"}
    exports = manager.export_model(model, ["step", "stl"])
    assert "step" in exports
    assert "stl" in exports


def test_cadquery_engine():
    """Test CadQuery engine"""
    engine = CadQueryEngine()
    
    # Test script generation for drone arm
    requirements = {"part_type": "drone_arm", "dimensions": {"length": 150}}
    result = engine.generate_from_requirements(requirements)
    assert "script" in result
    assert "model" in result


def test_freecad_engine():
    """Test FreeCAD engine"""
    engine = FreeCADEngine()
    
    # Test part creation
    part = engine.create_part({"name": "TestPart", "part_type": "box"})
    assert part["status"] == "created"
    
    # Test export
    exports = engine.export({"name": "TestModel"}, ["step", "fcstd"])
    assert len(exports) == 2


def test_mechanical_reasoner():
    """Test mechanical reasoning engine"""
    reasoner = MechanicalReasoner()
    requirements = {
        "load_kg": 50,
        "weight_priority": "high",
        "strength_priority": "medium"
    }
    
    analysis = reasoner.analyze_requirements(requirements)
    assert "material_recommendations" in analysis
    assert len(analysis["material_recommendations"]) > 0


def test_material_selector():
    """Test material selector"""
    selector = MaterialSelector()
    materials = selector.recommend_materials({
        "weight_priority": "high",
        "strength_priority": "medium"
    })
    assert len(materials) > 0
    # Check that aluminum is a top recommendation
    aluminum_found = any(m["name"] == "Aluminum 6061" for m in materials)
    assert aluminum_found


def test_component_library():
    """Test component library"""
    library = ComponentLibrary()
    
    # Test searching bearings
    bearings = library.search_components(category="bearings")
    assert len(bearings) > 0
    assert bearings[0]["category"] == "bearings"
    
    # Test searching fasteners
    fasteners = library.search_components(category="fasteners")
    assert len(fasteners) > 0


def test_assembly_generator():
    """Test assembly generator"""
    generator = AssemblyGenerator()
    
    # Create assembly
    assembly = generator.create_assembly(
        name="TestAssembly",
        project_id="test-project-1"
    )
    assert assembly["name"] == "TestAssembly"
    
    # Add a part
    part = {"id": "part-1", "name": "TestPart"}
    assembly = generator.add_part(assembly, part, [0, 0, 0])
    assert len(assembly["parts"]) == 1


def test_drawing_generator():
    """Test drawing generator"""
    generator = DrawingGenerator()
    
    part = {"id": "part-1", "name": "TestPart"}
    drawing = generator.create_drawing(
        part,
        views=["front", "top", "right"],
        title="Test Drawing"
    )
    assert len(drawing["views"]) == 3
    assert len(drawing["dimensions"]) > 0


def test_bom_generator():
    """Test BOM generator"""
    generator = BOMGenerator()
    
    # Create test assembly with parts
    assembly = {
        "id": "asm-1",
        "name": "Test Assembly",
        "parts": [
            {"part": {"id": "p1", "name": "Bracket", "material": "Aluminum", "cost": 10.0}},
            {"part": {"id": "p2", "name": "Screw", "material": "Steel", "cost": 0.50}},
            {"part": {"id": "p2", "name": "Screw", "material": "Steel", "cost": 0.50}},
        ]
    }
    
    # Generate BOM
    bom = generator.generate_bom(assembly)
    assert len(bom["items"]) == 2  # Should group identical parts
    assert bom["total_cost"] > 0


def test_material_properties_calculation():
    """Test mass property calculation"""
    engine = GeometryEngine()
    sketch = engine.create_sketch()
    sketch = engine.add_rectangle(sketch, (0,0), 10, 10)
    solid = engine.extrude(sketch, 5)
    
    props = engine.calculate_mass_properties(solid)
    assert "mass_kg" in props
    assert "volume_m3" in props


def test_cad_part_request_validation():
    """Test CAD part request schema"""
    request = CADPartRequest(
        project_id="test-123",
        part_type="bracket",
        name="Test Bracket",
        parameters={"width": 50, "height": 30}
    )
    assert request.project_id == "test-123"
    assert request.part_type == "bracket"

