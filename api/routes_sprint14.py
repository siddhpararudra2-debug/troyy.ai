"""Sprint 14 API Routes - FastAPI routes for Sprint 14 (Robotics & Autonomous Systems)."""

from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
import uuid

router = APIRouter(prefix="/api/sprint14", tags=["Sprint 14 - Robotics"])

# In-memory storage for demo
robots_db = {}
missions_db = {}
fleets_db = {}
maps_db = {}


@router.post("/robot/create")
async def create_robot(
    name: str,
    robot_type: str,
    description: Optional[str] = None,
    serial_number: Optional[str] = None,
):
    """Create a new robot."""
    from robotics import RobotManager
    manager = RobotManager()
    robot = manager.create_robot(name, robot_type, description, serial_number)
    robots_db[robot["id"]] = robot
    return robot


@router.get("/robot/{robot_id}")
async def get_robot(robot_id: str):
    """Get a robot by ID."""
    if robot_id not in robots_db:
        raise HTTPException(status_code=404, detail="Robot not found")
    return robots_db[robot_id]


@router.post("/mission/assign")
async def assign_mission(
    robot_id: str,
    mission_name: str,
    mission_data: Optional[Dict[str, Any]] = None,
):
    """Assign a mission to a robot."""
    mission_id = str(uuid.uuid4())
    mission = {
        "id": mission_id,
        "name": mission_name,
        "robot_id": robot_id,
        "data": mission_data or {},
        "status": "pending",
    }
    missions_db[mission_id] = mission
    if robot_id in robots_db:
        if "assigned_missions" not in robots_db[robot_id]:
            robots_db[robot_id]["assigned_missions"] = []
        robots_db[robot_id]["assigned_missions"].append(mission_id)
    return mission


@router.get("/mission/{mission_id}")
async def get_mission(mission_id: str):
    """Get a mission by ID."""
    if mission_id not in missions_db:
        raise HTTPException(status_code=404, detail="Mission not found")
    return missions_db[mission_id]


@router.post("/path/generate")
async def generate_path(
    start: Dict[str, float],
    goal: Dict[str, float],
    obstacles: Optional[List[Dict[str, Any]]] = None,
):
    """Generate a path from start to goal."""
    from motion_planning import PathPlanner
    planner = PathPlanner()
    success, path_data = planner.plan_path(start, goal, obstacles)
    return path_data


@router.post("/vision/detect")
async def detect_objects():
    """Detect objects (placeholder)."""
    from vision import ObjectDetection
    detector = ObjectDetection()
    detections = detector.detect(None)
    return {"detections": detections}


@router.post("/slam/run")
async def run_slam():
    """Run SLAM (placeholder)."""
    from slam import MappingEngine
    mapper = MappingEngine()
    map_data = mapper.build_map({})
    maps_db[map_data["id"]] = map_data
    return map_data


@router.get("/map/{map_id}")
async def get_map(map_id: str):
    """Get a map by ID."""
    if map_id not in maps_db:
        raise HTTPException(status_code=404, detail="Map not found")
    return maps_db[map_id]


@router.post("/fleet/manage")
async def manage_fleet(name: str, robot_ids: List[str]):
    """Create and manage a fleet."""
    from fleet import FleetManager
    manager = FleetManager()
    fleet = manager.create_fleet(name, robot_ids)
    fleets_db[fleet["id"]] = fleet
    return fleet


@router.get("/fleet/{fleet_id}")
async def get_fleet(fleet_id: str):
    """Get a fleet by ID."""
    if fleet_id not in fleets_db:
        raise HTTPException(status_code=404, detail="Fleet not found")
    return fleets_db[fleet_id]


@router.post("/twin/create")
async def create_twin(robot_id: str):
    """Create a digital twin for a robot."""
    from robot_twins import RobotTwin
    twin = RobotTwin(robot_id)
    return {
        "twin_id": twin.twin_id,
        "robot_id": twin.robot_id,
        "state": twin.state,
    }


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "sprint14",
        "components": {
            "robots": len(robots_db),
            "missions": len(missions_db),
            "fleets": len(fleets_db),
            "maps": len(maps_db),
        },
    }
