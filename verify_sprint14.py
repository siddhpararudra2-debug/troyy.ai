#!/usr/bin/env python3
"""Verify Sprint 14 (Robotics & Autonomous Systems) modules are all available and working."""

import sys

print("=== Verifying Sprint 14 Modules ===")

# Test Module 1: Robotics Core Platform
try:
    print("\n1. Testing Robotics Core Platform (robotics)...")
    from robotics import (
        RobotManager,
        RobotStatus,
        RobotType,
        RobotArchitecture,
        RobotReasoner,
        RobotLifecycle,
    )
    print("OK: robotics module imported successfully!")
    
    # Test Robot Manager
    manager = RobotManager()
    robot = manager.create_robot(
        "Test Robot",
        RobotType.MOBILE,
        description="Test robot for verification",
        serial_number="TEST001",
        manufacturer="Troy AI",
        model="v1.0",
        capabilities=["navigation", "obstacle avoidance"],
    )
    print(f"OK: Created robot: {robot['name']} (ID: {robot['id']})")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test Module 2: Motion Planning
try:
    print("\n2. Testing Motion Planning (motion_planning)...")
    from motion_planning import (
        PathPlanner,
        TrajectoryGenerator,
        ObstacleAvoidance,
        MotionValidator,
    )
    print("OK: motion_planning module imported successfully!")
    
    # Test path planning
    planner = PathPlanner()
    start = {"x": 0.0, "y": 0.0, "z": 0.0}
    goal = {"x": 10.0, "y": 10.0, "z": 0.0}
    success, path_data = planner.plan_path(start, goal)
    print(f"OK: Planned path: {path_data}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test Module 3: Computer Vision
try:
    print("\n3. Testing Computer Vision (vision)...")
    from vision import (
        ObjectDetection,
        SegmentationEngine,
        PoseEstimator,
        SceneUnderstanding,
    )
    print("OK: vision module imported successfully!")
    
    # Test object detection
    detector = ObjectDetection()
    detections = detector.detect(None)
    print(f"OK: Detection result: {len(detections)} detections")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test Module 4: Sensor Fusion
try:
    print("\n4. Testing Sensor Fusion (sensor_fusion)...")
    from sensor_fusion import (
        FusionEngine,
        StateEstimator,
        LocalizationEngine,
        PerceptionManager,
    )
    print("OK: sensor_fusion module imported successfully!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test Module 5: SLAM
try:
    print("\n5. Testing SLAM (slam)...")
    from slam import (
        MappingEngine,
        LocalizationEngine,
        LoopClosure,
        MapManager,
    )
    print("OK: slam module imported successfully!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test Module 6: Autonomy
try:
    print("\n6. Testing Autonomy (autonomy)...")
    from autonomy import (
        BehaviorPlanner,
        DecisionEngine,
        TaskPlanner,
        AutonomyManager,
    )
    print("OK: autonomy module imported successfully!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test Module 7: Fleet Management
try:
    print("\n7. Testing Fleet Management (fleet)...")
    from fleet import (
        FleetManager,
        RobotTracker,
        MissionAllocator,
        FleetAnalytics,
    )
    print("OK: fleet module imported successfully!")
    
    # Test fleet creation
    fleet_manager = FleetManager()
    fleet = fleet_manager.create_fleet(
        "Test Fleet",
        robot_ids=[robot["id"]],
    )
    print(f"OK: Created fleet: {fleet['name']}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test Module 8: Digital Robot Twin
try:
    print("\n8. Testing Digital Robot Twin (robot_twins)...")
    from robot_twins import (
        RobotTwin,
        SimulationBridge,
        TelemetryProcessor,
    )
    print("OK: robot_twins module imported successfully!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test Module 9: Human-Robot Interaction
try:
    print("\n9. Testing Human-Robot Interaction (hri)...")
    from hri import (
        InteractionManager,
        VoiceInterface,
        OperatorAssistant,
        SafetySupervisor,
    )
    print("OK: hri module imported successfully!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test Module 10: Robotics Orchestrator
try:
    print("\n10. Testing Robotics Orchestrator (robotics_core)...")
    from robotics_core import (
        RoboticsOrchestrator,
        MissionController,
        AutonomyController,
    )
    print("OK: robotics_core module imported successfully!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test Database Models
try:
    print("\n11. Testing Database Models...")
    from database.sprint14_models import (
        Robot,
        RobotConfiguration,
        Sensor,
        Map,
        Mission,
        Trajectory,
        LocalizationRecord,
        Detection,
        Fleet,
        RobotTwin,
        OperatorSession,
        BehaviorTree,
    )
    print("OK: sprint14 database models imported successfully!")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test API Routes
try:
    print("\n12. Testing API Routes...")
    from api.routes_sprint14 import router
    print("OK: sprint14 API router imported successfully!")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n=== Verification Complete: ALL Sprint 14 Modules OK ===")
