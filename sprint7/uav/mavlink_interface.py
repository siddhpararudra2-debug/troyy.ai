"""
MAVLink Interface — abstraction over pymavlink for PX4/ArduPilot.
"""
import asyncio
import struct
from typing import Dict, List, Optional, Callable
from datetime import datetime
from sprint7.schemas.enums import AutopilotType, FlightMode

class MAVLinkInterface:
    """MAVLink interface for communicating with PX4/ArduPilot."""
    
    # MAVLink message IDs
    MSG_HEARTBEAT = 0
    MSG_SYS_STATUS = 1
    MSG_GPS_RAW = 24
    MSG_ATTITUDE = 30
    MSG_GLOBAL_POSITION = 33
    MSG_COMMAND_LONG = 76
    MSG_MISSION_ITEM = 39
    MSG_COMMAND_ACK = 77
    
    # MAV_CMD values
    CMD_NAV_TAKEOFF = 22
    CMD_NAV_LAND = 21
    CMD_COMPONENT_ARM_DISARM = 400
    CMD_SET_MODE = 176
    CMD_MISSION_START = 300
    
    # PX4 Main modes
    PX4_MODES = {
        "MANUAL": (1, 0, 0),
        "ALTCTL": (1, 1, 0),
        "POSCTL": (1, 1, 3),
        "AUTO_MISSION": (1, 0, 4),
        "AUTO_LOITER": (1, 0, 3),
        "AUTO_RTL": (1, 0, 5),
        "AUTO_LAND": (1, 0, 6),
        "AUTO_TAKEOFF": (1, 0, 5),
    }
    
    def __init__(self, connection_string: str = "udp:127.0.0.1:14540",
                autopilot: AutopilotType = AutopilotType.PX4,
                baud: int = 57600):
        self.connection_string = connection_string
        self.autopilot = autopilot
        self.baud = baud
        self.connection = None
        self.connected = False
        self.telemetry: Dict = {}
        self.message_handlers: Dict[int, List[Callable]] = {}
        self._heartbeat_count = 0
        self.last_heartbeat = None
        
    def connect(self) -> bool:
        """Establish MAVLink connection."""
        try:
            from pymavlink import mavutil
            self.connection = mavutil.mavlink_connection(
                self.connection_string,
                baud=self.baud
            )
            # Wait for heartbeat
            self.connection.wait_heartbeat(timeout=5)
            self.connected = True
            self.last_heartbeat = datetime.utcnow()
            return True
        except ImportError:
            print("pymavlink not available — using simulated connection")
            self.connected = True  # Simulated
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            self.connected = False
            return False
            
    def disconnect(self) -> None:
        """Close connection."""
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
        self.connected = False
        
    def arm(self) -> bool:
        """Arm the vehicle."""
        if not self.connected:
            return False
        return self._send_command(self.CMD_COMPONENT_ARM_DISARM, param1=1)
        
    def disarm(self) -> bool:
        """Disarm the vehicle."""
        if not self.connected:
            return False
        return self._send_command(self.CMD_COMPONENT_ARM_DISARM, param1=0)
        
    def set_mode(self, mode: str) -> bool:
        """Set flight mode."""
        if not self.connected:
            return False
            
        if self.autopilot == AutopilotType.PX4:
            if mode not in self.PX4_MODES:
                return False
            base_mode, custom_mode, custom_sub_mode = self.PX4_MODES[mode]
            # PX4 uses custom mode encoding
            custom_mode_encoded = (custom_sub_mode << 16) | (custom_mode << 24)
            return self._send_command(self.CMD_SET_MODE,
                                     param1=base_mode,
                                     param2=custom_mode_encoded)
        else:
            # ArduPilot uses simpler mode numbers
            mode_map = {
                "STABILIZE": 0, "ALT_HOLD": 2, "LOITER": 5,
                "RTL": 6, "AUTO": 3, "LAND": 9, "TAKEOFF": 13
            }
            mode_num = mode_map.get(mode, 0)
            return self._send_command(self.CMD_SET_MODE, param1=mode_num)
            
    def takeoff(self, altitude_m: float) -> bool:
        """Command takeoff to specified altitude."""
        return self._send_command(self.CMD_NAV_TAKEOFF, param7=altitude_m)
        
    def land(self) -> bool:
        """Command landing."""
        return self._send_command(self.CMD_NAV_LAND)
        
    def upload_mission(self, waypoints: List[Dict]) -> bool:
        """Upload mission waypoints."""
        if not self.connected:
            return False
            
        try:
            # Clear existing mission
            if hasattr(self.connection, 'mission_clear_all'):
                self.connection.mission_clear_all()
                
            # Upload each waypoint
            for i, wp in enumerate(waypoints):
                lat = int(wp.get("latitude", 0) * 1e7)
                lon = int(wp.get("longitude", 0) * 1e7)
                alt = wp.get("altitude", 50)
                
                if hasattr(self.connection, 'mission_write_partial_list'):
                    self.connection.mav.mission_item_int_send(
                        1,  # target system
                        1,  # target component
                        i,  # seq
                        3,  # frame (MAV_FRAME_GLOBAL_RELATIVE_ALT)
                        16, # command (MAV_CMD_NAV_WAYPOINT)
                        0,  # current
                        1,  # autocontinue
                        0, 0, 0, 0,  # params (unused for waypoint)
                        lat, lon, alt
                    )
                    
            # Wait for ack (simplified)
            return True
        except Exception as e:
            print(f"Mission upload failed: {e}")
            return False
            
    def start_mission(self) -> bool:
        """Start executing uploaded mission."""
        return self._send_command(self.CMD_MISSION_START)
        
    def get_telemetry(self) -> Dict:
        """Get current telemetry snapshot."""
        if not self.connected:
            return {}
            
        try:
            # Request specific messages
            if hasattr(self.connection, 'messages'):
                msgs = self.connection.messages
                
                telemetry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "connected": self.connected,
                    "autopilot": self.autopilot.value,
                }
                
                # GPS
                if 'GPS_RAW_INT' in msgs:
                    gps = msgs['GPS_RAW_INT']
                    telemetry.update({
                        "latitude": gps.lat / 1e7,
                        "longitude": gps.lon / 1e7,
                        "altitude_m": gps.alt / 1000,
                        "gps_fix": gps.fix_type,
                        "satellites": gps.satellites_visible
                    })
                    
                # Attitude
                if 'ATTITUDE' in msgs:
                    att = msgs['ATTITUDE']
                    import math
                    telemetry.update({
                        "roll_deg": math.degrees(att.roll),
                        "pitch_deg": math.degrees(att.pitch),
                        "yaw_deg": math.degrees(att.yaw)
                    })
                    
                # Battery
                if 'SYS_STATUS' in msgs:
                    sys = msgs['SYS_STATUS']
                    telemetry.update({
                        "battery_voltage_v": sys.voltage_battery / 1000,
                        "battery_current_a": sys.current_battery / 100,
                        "battery_remaining_pct": sys.battery_remaining
                    })
                    
                return telemetry
            else:
                # Simulated telemetry
                return self._simulated_telemetry()
                
        except Exception as e:
            return {"error": str(e), "connected": self.connected}
            
    def _simulated_telemetry(self) -> Dict:
        """Generate simulated telemetry for testing."""
        import random
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "connected": self.connected,
            "autopilot": self.autopilot.value,
            "latitude": 47.397742 + random.uniform(-0.001, 0.001),
            "longitude": 8.545594 + random.uniform(-0.001, 0.001),
            "altitude_m": 50 + random.uniform(-2, 2),
            "roll_deg": random.uniform(-5, 5),
            "pitch_deg": random.uniform(-5, 5),
            "yaw_deg": random.uniform(0, 360),
            "ground_speed_ms": random.uniform(0, 15),
            "battery_voltage_v": 14.8 - random.uniform(0, 2),
            "battery_remaining_pct": max(0, 100 - random.uniform(0, 30)),
            "gps_fix": 3,
            "satellites": random.randint(8, 14),
            "flight_mode": "AUTO_MISSION"
        }
        
    def _send_command(self, command: int, **params) -> bool:
        """Send a MAVLink command."""
        if not self.connected:
            return False
            
        try:
            if hasattr(self.connection, 'mav'):
                self.connection.mav.command_long_send(
                    1, 1,  # target system/component
                    command,
                    0,  # confirmation
                    params.get("param1", 0),
                    params.get("param2", 0),
                    params.get("param3", 0),
                    params.get("param4", 0),
                    params.get("param5", 0),
                    params.get("param6", 0),
                    params.get("param7", 0)
                )
                return True
            else:
                # Simulated
                return True
        except Exception as e:
            print(f"Command send failed: {e}")
            return False
            
    def register_message_handler(self, msg_id: int, handler: Callable) -> None:
        """Register handler for specific MAVLink message."""
        self.message_handlers.setdefault(msg_id, []).append(handler)
