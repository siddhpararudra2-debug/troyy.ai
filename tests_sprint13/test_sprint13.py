"""Sprint 13 Comprehensive Tests."""

import pytest
from datetime import datetime
from mission_systems.mission_engine import MissionEngine, MissionStatus, MissionPriority, Mission, MissionObjective, MissionAsset
from mission_systems.objective_manager import ObjectiveManager, ObjectiveStatus
from mission_systems.mission_planner import MissionPlanner, PlanningConstraint
from mission_systems.mission_validator import MissionValidator
from swarm_ops.swarm_manager import SwarmManager, SwarmStatus, SwarmAgent
from swarm_ops.formation_controller import FormationController
from swarm_ops.task_allocator import TaskAllocator, AllocationStrategy
from command_control.c2_engine import C2Engine, CommandType, CommandStatus
from command_control.command_router import CommandRouter
from command_control.situational_awareness import SituationalAwareness
from sensor_fusion.fusion_engine import FusionEngine
from sensor_fusion.track_manager import TrackManager
from operational_twins.operational_twin import OperationalTwin
from logistics_readiness.readiness_engine import ReadinessEngine
from mission_analytics.analytics_engine import AnalyticsEngine
from operations_core.operations_orchestrator import OperationsOrchestrator, OperationPhase


# ==================== MISSION SYSTEMS TESTS ====================

class TestMissionEngine:
    """Test Mission Engine."""
    
    def test_create_mission(self):
        """Test mission creation."""
        engine = MissionEngine()
        mission = engine.create_mission(
            "Test Mission",
            "Test Description",
            "uav"
        )
        
        assert mission.name == "Test Mission"
        assert mission.mission_type == "uav"
        assert mission.status == MissionStatus.PLANNING
        assert mission.id in engine.missions
    
    def test_add_objective(self):
        """Test adding objective to mission."""
        engine = MissionEngine()
        mission = engine.create_mission("Test", "Test", "uav")
        
        obj = MissionObjective(
            name="Survey Area",
            objective_type="survey",
            location={"lat": 40.7128, "lon": -74.0060}
        )
        
        success = engine.add_objective(mission.id, obj)
        assert success
        assert len(mission.objectives) == 1
    
    def test_update_mission_status(self):
        """Test mission status update."""
        engine = MissionEngine()
        mission = engine.create_mission("Test", "Test", "uav")
        
        success = engine.update_mission_status(
            mission.id,
            MissionStatus.EXECUTING
        )
        
        assert success
        assert mission.status == MissionStatus.EXECUTING
        assert mission.actual_start is not None


class TestObjectiveManager:
    """Test Objective Manager."""
    
    def test_create_objective(self):
        """Test objective creation."""
        manager = ObjectiveManager()
        
        obj_id = manager.create_objective(
            mission_id="mission1",
            name="Survey",
            description="Survey area",
            objective_type="survey",
            target_location={"lat": 40.7128, "lon": -74.0060},
            success_criteria=["Coverage > 90%"],
            estimated_duration=120
        )
        
        assert obj_id in manager.objectives
        
        obj = manager.get_objective(obj_id)
        assert obj["name"] == "Survey"
    
    def test_update_objective_status(self):
        """Test objective status update."""
        manager = ObjectiveManager()
        
        obj_id = manager.create_objective(
            "m1", "Survey", "Survey area", "survey",
            {"lat": 40.7128, "lon": -74.0060},
            ["Coverage > 90%"]
        )
        
        success = manager.update_objective_status(
            obj_id,
            ObjectiveStatus.IN_PROGRESS
        )
        
        assert success
        assert manager.get_objective(obj_id)["status"] == "in_progress"


class TestMissionValidator:
    """Test Mission Validator."""
    
    def test_validate_mission(self):
        """Test mission validation."""
        validator = MissionValidator()
        
        mission = {
            "id": "mission1",
            "name": "Test Mission",
            "mission_type": "uav",
            "objectives": [
                {
                    "name": "Survey",
                    "type": "survey",
                    "target_location": {"lat": 40.7128, "lon": -74.0060},
                    "success_criteria": ["Coverage > 90%"]
                }
            ],
            "assigned_assets": [{"asset_id": "uav1", "role": "primary"}],
            "regulatory_requirements": ["No-fly zone clearance"]
        }
        
        status, errors, warnings = validator.validate_mission(mission)
        
        assert status.value == "valid"
        assert len(errors) == 0


# ==================== SWARM TESTS ====================

class TestSwarmManager:
    """Test Swarm Manager."""
    
    def test_create_swarm(self):
        """Test swarm creation."""
        manager = SwarmManager()
        
        agents = [
            SwarmAgent(agent_id=f"uav{i}", agent_type="uav")
            for i in range(3)
        ]
        
        swarm = manager.create_swarm(
            "Test Swarm",
            "homogeneous",
            agents
        )
        
        assert swarm.name == "Test Swarm"
        assert len(swarm.agents) == 3
        assert swarm.status == SwarmStatus.IDLE
    
    def test_form_swarm(self):
        """Test forming swarm with formation."""
        manager = SwarmManager()
        
        agents = [SwarmAgent(agent_id=f"uav{i}", agent_type="uav") for i in range(3)]
        swarm = manager.create_swarm("Test", "homogeneous", agents)
        
        success, result = manager.form_swarm(
            swarm.id,
            "line",
            formation_spacing=5.0
        )
        
        assert success
        assert swarm.status == SwarmStatus.COORDINATED
        assert swarm.formation_type == "line"


class TestFormationController:
    """Test Formation Controller."""
    
    def test_establish_formation(self):
        """Test formation establishment."""
        controller = FormationController()
        
        success, result = controller.establish_formation(
            "swarm1",
            "line",
            {"x": 0, "y": 0, "z": 100},
            agents_count=4
        )
        
        assert success
        assert len(result["positions"]) == 3  # 3 members + 1 leader


class TestTaskAllocator:
    """Test Task Allocator."""
    
    def test_allocate_tasks(self):
        """Test task allocation."""
        allocator = TaskAllocator()
        
        task1 = allocator.create_task(
            "swarm1",
            "survey",
            priority=8,
            required_capabilities=["gps", "camera"]
        )
        
        agents = [
            {"id": "uav1", "capabilities": ["gps", "camera", "lidar"]},
            {"id": "uav2", "capabilities": ["gps"]},
        ]
        
        success, allocation = allocator.allocate_tasks(
            "swarm1",
            agents,
            AllocationStrategy.GREEDY
        )
        
        assert success
        assert task1 in allocation


# ==================== COMMAND & CONTROL TESTS ====================

class TestC2Engine:
    """Test C2 Engine."""
    
    def test_issue_command(self):
        """Test command issuance."""
        engine = C2Engine()
        
        cmd_id = engine.issue_command(
            CommandType.MISSION_START,
            "target1",
            {"mission_id": "m1"},
            "operator1"
        )
        
        cmd = engine.get_command(cmd_id)
        assert cmd["status"] == CommandStatus.PENDING.value
        assert cmd["target"] == "target1"
    
    def test_authorize_command(self):
        """Test command authorization."""
        engine = C2Engine()
        
        cmd_id = engine.issue_command(
            CommandType.MISSION_START,
            "target1",
            {},
            "operator1"
        )
        
        success = engine.authorize_command(cmd_id, "supervisor1")
        assert success
        
        cmd = engine.get_command(cmd_id)
        assert cmd["status"] == CommandStatus.AUTHORIZED.value


class TestSituationalAwareness:
    """Test Situational Awareness."""
    
    def test_update_entity_position(self):
        """Test entity position update."""
        sa = SituationalAwareness()
        
        sa.update_entity_position(
            "uav1",
            {"x": 100, "y": 200, "z": 300},
            {"vx": 10, "vy": 0, "vz": 0}
        )
        
        picture = sa.get_operational_picture()
        assert len(picture["entity_positions"]) == 1


# ==================== SENSOR FUSION TESTS ====================

class TestFusionEngine:
    """Test Sensor Fusion Engine."""
    
    def test_ingest_measurement(self):
        """Test measurement ingestion."""
        engine = FusionEngine()
        
        engine.register_sensor("radar1", "radar", {"x": 0, "y": 0})
        engine.ingest_measurement("radar1", {"x": 100, "y": 200, "z": 50})
        
        assert len(engine.sensor_streams["radar1"]) == 1


class TestTrackManager:
    """Test Track Manager."""
    
    def test_create_track(self):
        """Test track creation."""
        manager = TrackManager()
        
        track_id = manager.create_track(
            {"x": 100, "y": 200, "z": 50},
            "aircraft"
        )
        
        track = manager.get_track(track_id)
        assert track is not None
        assert track.state["classification"] == "aircraft"


# ==================== OPERATIONAL TWINS TESTS ====================

class TestOperationalTwin:
    """Test Operational Twin."""
    
    def test_update_state(self):
        """Test twin state update."""
        twin = OperationalTwin("asset1", "uav")
        
        twin.update_state({
            "position": {"x": 100, "y": 200, "z": 300},
            "velocity": {"vx": 10, "vy": 0, "vz": 0},
            "health": 0.95,
            "battery": 85,
            "status": "active"
        })
        
        health = twin.get_health_status()
        assert health["health"] == 0.95
        assert health["battery"] == 85


# ==================== LOGISTICS TESTS ====================

class TestReadinessEngine:
    """Test Readiness Engine."""
    
    def test_assess_readiness(self):
        """Test readiness assessment."""
        engine = ReadinessEngine()
        
        readiness = engine.assess_readiness(
            "asset1",
            {
                "health": 0.95,
                "fuel": 1.0,
                "maintenance_due": 0.8,
                "communications": 1.0,
            }
        )
        
        assert 0 <= readiness <= 1
        assert readiness > 0.8


# ==================== MISSION ANALYTICS TESTS ====================

class TestAnalyticsEngine:
    """Test Analytics Engine."""
    
    def test_analyze_mission(self):
        """Test mission analysis."""
        engine = AnalyticsEngine()
        
        analysis_id = engine.analyze_mission(
            "mission1",
            {
                "success": True,
                "duration": 120,
                "completion_rate": 1.0,
                "efficiency": 0.92,
                "safety_score": 0.98,
            }
        )
        
        analysis = engine.get_analysis(analysis_id)
        assert analysis["mission_id"] == "mission1"


# ==================== OPERATIONS ORCHESTRATOR TESTS ====================

class TestOperationsOrchestrator:
    """Test Operations Orchestrator."""
    
    def test_initiate_operation(self):
        """Test operation initiation."""
        orchestrator = OperationsOrchestrator()
        
        op_id = orchestrator.initiate_operation(
            "Op-001",
            "mission1",
            ["pilot1", "navigator1"]
        )
        
        op = orchestrator.get_operation(op_id)
        assert op["name"] == "Op-001"
        assert op["phase"] == OperationPhase.PLANNING.value
    
    def test_advance_phase(self):
        """Test operation phase advancement."""
        orchestrator = OperationsOrchestrator()
        
        op_id = orchestrator.initiate_operation(
            "Op-001",
            "mission1",
            ["pilot1"]
        )
        
        success = orchestrator.advance_phase(op_id, OperationPhase.SIMULATION)
        assert success
        
        op = orchestrator.get_operation(op_id)
        assert op["phase"] == OperationPhase.SIMULATION.value


# ==================== INTEGRATION TESTS ====================

class TestIntegration:
    """Integration tests."""
    
    def test_end_to_end_mission_workflow(self):
        """Test complete mission workflow."""
        # Mission creation
        engine = MissionEngine()
        mission = engine.create_mission("Integration Test", "Full workflow", "uav")
        
        # Mission planning
        planner = MissionPlanner()
        success, plan, result = planner.create_mission_plan(
            mission.id,
            [],
            []
        )
        
        assert success or "error" in result
        
        # Mission execution
        success = engine.update_mission_status(mission.id, MissionStatus.EXECUTING)
        assert success
        
        # Analytics
        analytics = AnalyticsEngine()
        analysis_id = analytics.analyze_mission(mission.id, {"success": True})
        assert analysis_id
    
    def test_swarm_coordination_workflow(self):
        """Test swarm coordination workflow."""
        manager = SwarmManager()
        controller = FormationController()
        
        # Create swarm
        agents = [SwarmAgent(agent_id=f"uav{i}", agent_type="uav") for i in range(3)]
        swarm = manager.create_swarm("Swarm1", "homogeneous", agents)
        
        # Form swarm
        success, _ = manager.form_swarm(swarm.id, "line")
        assert success
        
        # Move formation
        success, _ = controller.move_formation(
            swarm.id,
            {"x": 100, "y": 200, "z": 300},
            0.0,
            10.0
        )
        assert success


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
