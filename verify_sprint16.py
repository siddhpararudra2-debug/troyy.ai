#!/usr/bin/env python3
"""Verify Sprint 16 (Engineering Deep Research) modules are all available and working."""

import sys

print("=== Verifying Sprint 16 Modules ===\n")

all_passed = True

# Test Module 1: Research Core
try:
    print("1. Testing Research Core (research_core)...")
    from research_core import (
        ResearchOrchestrator,
        ResearchPlanner,
        SourceManager,
        EvidenceManager,
        ResearchValidator,
    )
    print("   OK: Imported all research_core classes")
    orchestrator = ResearchOrchestrator()
    project = orchestrator.start_research(
        question="How to design a lightweight drone frame?",
        domain="Aerospace",
        name="Drone Frame Research"
    )
    print(f"   OK: Started research project: {project['name']}")
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
    import traceback
    traceback.print_exc()
print()

# Test Module 2: Mechanical Research
try:
    print("2. Testing Mechanical Research (mechanical_research)...")
    from mechanical_research import (
        MaterialResearch,
        StructuralResearch,
        ManufacturingResearch,
        ThermalResearch,
        FatigueResearch,
        BenchmarkEngine,
        FailureAnalysis,
    )
    print("   OK: Imported all mechanical_research classes")
    mat_research = MaterialResearch()
    result = mat_research.research("Aluminum 6061", "Drone frame")
    print(f"   OK: Material research result: suitability score {result['suitability_score']}")
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
print()

# Test Module 3: Electrical Research
try:
    print("3. Testing Electrical & Electronics Research (electrical_research)...")
    from electrical_research import (
        ComponentResearch,
        ArchitectureResearch,
        PCBResearch,
        PowerElectronicsResearch,
        SemiconductorResearch,
        EMCResearch,
        ThermalElectronicsResearch,
    )
    print("   OK: Imported all electrical_research classes")
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
print()

# Test Module 4: Materials Intelligence
try:
    print("4. Testing Materials Intelligence (materials)...")
    from materials import (
        MaterialDatabase,
        MaterialComparator,
        LifecycleAnalyzer,
        SustainabilityEngine,
    )
    print("   OK: Imported all materials classes")
    db = MaterialDatabase()
    mat = db.add_material(
        "Aluminum 6061",
        "Metal",
        {"tensile_strength": 310, "density": 2.7},
        cost_per_unit=5.0,
        supplier="Supplier X"
    )
    print(f"   OK: Added material: {mat['name']}")
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
print()

# Test Module 5: Manufacturing Intelligence
try:
    print("5. Testing Manufacturing Intelligence (manufacturing_research)...")
    from manufacturing_research import (
        ProcessResearch,
        CapabilityMapper,
        CostAnalyzer,
        SupplyChainResearch,
    )
    print("   OK: Imported all manufacturing_research classes")
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
print()

# Test Module 6: Standards Intelligence
try:
    print("6. Testing Standards Intelligence (standards)...")
    from standards import (
        StandardsEngine,
        ComplianceMapper,
        RegulationAnalyzer,
        CertificationPlanner,
    )
    print("   OK: Imported all standards classes")
    engine = StandardsEngine()
    std = engine.add_standard(
        "AS9100",
        "AS9100",
        "SAE International",
        "Aerospace quality management system"
    )
    print(f"   OK: Added standard: {std['name']}")
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
print()

# Test Module 7: Patent Intelligence
try:
    print("7. Testing Patent Intelligence (patents)...")
    from patents import (
        PatentSearch,
        PriorArtAnalyzer,
        NoveltyEngine,
        PatentLandscape,
    )
    print("   OK: Imported all patents classes")
    searcher = PatentSearch()
    patent = searcher.add_patent(
        "Lightweight Drone Frame",
        "US1234567",
        ["Inventor A", "Inventor B"],
        "Company X"
    )
    print(f"   OK: Added patent: {patent['title']}")
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
print()

# Test Module 8: Academic Research
try:
    print("8. Testing Academic Research (academic)...")
    from academic import (
        LiteratureSearch,
        CitationGraph,
        TrendDetector,
        SotaAnalyzer,
        ResearchGapDetector,
    )
    print("   OK: Imported all academic classes")
    lit_search = LiteratureSearch()
    paper = lit_search.add_paper(
        "Lightweight Composite Materials for Aerospace",
        ["Author A", "Author B"],
        "AIAA Journal"
    )
    print(f"   OK: Added paper: {paper['title']}")
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
print()

# Test Module 9: Engineering Benchmarking
try:
    print("9. Testing Engineering Benchmarking (benchmarking)...")
    from benchmarking import (
        ProductAnalyzer,
        CompetitorAnalyzer,
        ArchitectureBenchmark,
        TechnologyComparator,
    )
    print("   OK: Imported all benchmarking classes")
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
print()

# Test Module 10: Autonomous Research Agent Team
try:
    print("10. Testing Research Agents (research_agents)...")
    from research_agents import (
        MechanicalAgent,
        ElectricalAgent,
        AerospaceAgent,
        ManufacturingAgent,
        MaterialsAgent,
        StandardsAgent,
        PatentAgent,
        AcademicAgent,
    )
    print("   OK: Imported all research_agents classes")
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
print()

# Test Module 11: Trade Study Engine
try:
    print("11. Testing Trade Study Engine (trade_studies)...")
    from trade_studies import (
        DecisionMatrix,
        WeightingEngine,
        SensitivityAnalyzer,
        RecommendationEngine,
    )
    print("   OK: Imported all trade_studies classes")
    dm = DecisionMatrix()
    matrix = dm.create_matrix(
        "Material Selection",
        [{"name": "Aluminum"}, {"name": "Carbon Fiber"}],
        [{"name": "Cost", "weight": 0.4}, {"name": "Strength", "weight": 0.6}]
    )
    weights = WeightingEngine().equal_weights(2)
    result = dm.calculate_scores(matrix["id"], weights)
    print(f"   OK: Trade study result: {result['results']}")
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
print()

# Test Module 12: Technology Scouting
try:
    print("12. Testing Technology Scouting (technology_scouting)...")
    from technology_scouting import (
        EmergingTechDetector,
        TrendForecaster,
        InnovationMapper,
    )
    print("   OK: Imported all technology_scouting classes")
    detector = EmergingTechDetector()
    trends = detector.detect()
    print(f"   OK: Found {len(trends)} emerging tech trends")
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
print()

# Test Module 13: Knowledge Extraction
try:
    print("13. Testing Knowledge Extraction (knowledge_extraction)...")
    from knowledge_extraction import (
        EntityExtractor,
        RelationshipBuilder,
        EvidenceLinker,
    )
    print("   OK: Imported all knowledge_extraction classes")
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
print()

# Test Module 14: Research Report Generation
try:
    print("14. Testing Research Report Generation (research_reports)...")
    from research_reports import (
        ReportGenerator,
        ExecutiveSummary,
        TechnicalWriter,
    )
    print("   OK: Imported all research_reports classes")
    generator = ReportGenerator()
    report = generator.generate({"name": "Test Project", "question": "Test Question"})
    print("   OK: Generated research report")
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
print()

# Test Module 15: Engineering Research Brain
try:
    print("15. Testing Research Brain (research_brain)...")
    from research_brain import (
        EngineeringScientist,
        RecommendationEngine,
        StrategicAdvisor,
    )
    print("   OK: Imported all research_brain classes")
    scientist = EngineeringScientist()
    result = scientist.research("How to optimize drone battery life?")
    print(f"   OK: Scientist started research: {result['status']}")
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
print()

# Test Database Models
try:
    print("16. Testing Database Models (database.sprint16_models)...")
    from database.sprint16_models import (
        ResearchProject,
        ResearchQuestion,
        ResearchSource,
        Paper,
        Patent,
        Standard,
        TradeStudy,
        TechnologyTrend,
        MaterialRecord,
        ComponentRecord,
        ResearchFinding,
        Recommendation,
        Evidence,
        Citation,
        KnowledgeNode,
        KnowledgeEdge,
    )
    print("   OK: Imported all sprint16 database models")
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
print()

# Test API Routes
try:
    print("17. Testing API Routes (api.routes_sprint16)...")
    from api.routes_sprint16 import router
    print("   OK: Imported sprint16 router")
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
print()

print("=== Sprint 16 Verification Complete ===")
if all_passed:
    print("\n[PASSED] ALL TESTS PASSED!")
    sys.exit(0)
else:
    print("\n[FAILED] SOME TESTS FAILED!")
    sys.exit(1)
