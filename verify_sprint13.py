#!/usr/bin/env python3
"""Verify Sprint 13 modules are all available and working."""

import sys

print("=== Verifying Sprint 13 Modules ===")

try:
    print("\n1. Testing mission_systems...")
    from mission_systems import MissionEngine, ObjectiveManager, MissionPlanner, MissionValidator
    print("OK: mission_systems imported successfully!")
    
    # Test mission engine
    mission_engine = MissionEngine()
    mission = mission_engine.create_mission("Test Mission", "Sprint 13 Test", "uav")
    print(f"OK: Created mission: {mission.name} (ID: {mission.id})")
    
except Exception as e:
    print(f"ERROR importing mission_systems: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n2. Testing swarm_ops...")
    from swarm_ops import SwarmManager, SwarmStatus, SwarmAgent, FormationController, TaskAllocator, AllocationStrategy
    print("OK: swarm_ops imported successfully!")
    
    # Test swarm manager
    swarm_manager = SwarmManager()
    agents = [SwarmAgent(agent_id="uav1", agent_type="uav"), SwarmAgent(agent_id="uav2", agent_type="uav")]
    swarm = swarm_manager.create_swarm("Test Swarm", "homogeneous", agents)
    print(f"OK: Created swarm successfully!")
    
except Exception as e:
    print(f"ERROR importing swarm_ops: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n3. Testing command_control...")
    from command_control import C2Engine, CommandRouter, SituationalAwareness
    print("OK: command_control imported successfully!")
except Exception as e:
    print(f"ERROR importing command_control: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n4. Testing battlespace...")
    from battlespace import EnvironmentBuilder, TerrainEngine, OperationalMap, ScenarioGenerator
    print("OK: battlespace imported successfully!")
except Exception as e:
    print(f"ERROR importing battlespace: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n5. Testing rehearsal...")
    from rehearsal import RehearsalEngine, ScenarioRunner, MissionReplayer
    print("OK: rehearsal imported successfully!")
except Exception as e:
    print(f"ERROR importing rehearsal: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n6. Testing sensor_fusion...")
    from sensor_fusion import FusionEngine, TrackManager, TargetCorrelator
    print("OK: sensor_fusion imported successfully!")
except Exception as e:
    print(f"ERROR importing sensor_fusion: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n7. Testing operational_twins...")
    from operational_twins import OperationalTwin, FleetTwin, MissionTwin
    print("OK: operational_twins imported successfully!")
except Exception as e:
    print(f"ERROR importing operational_twins: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n8. Testing logistics_readiness...")
    from logistics_readiness import LogisticsManager, ReadinessEngine, AssetTracker, MaintenanceForecaster
    print("OK: logistics_readiness imported successfully!")
except Exception as e:
    print(f"ERROR importing logistics_readiness: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n9. Testing mission_analytics...")
    from mission_analytics import AnalyticsEngine, MissionMetrics, PerformanceEvaluator
    print("OK: mission_analytics imported successfully!")
except Exception as e:
    print(f"ERROR importing mission_analytics: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n10. Testing operations_core...")
    from operations_core import OperationsOrchestrator, OperationPhase, CampaignManager, OperationalLifecycle
    print("OK: operations_core imported successfully!")
except Exception as e:
    print(f"ERROR importing operations_core: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n=== Verification Complete: ALL MODULES OK ===")
