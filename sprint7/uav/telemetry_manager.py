"""
Telemetry Manager — collects, stores, and streams telemetry data.
"""
import asyncio
from typing import Dict, List, Optional, Callable
from datetime import datetime
from collections import deque
from sprint7.schemas.models import TelemetryRecord

class TelemetryManager:
    """Manages telemetry ingestion and storage."""
    
    def __init__(self, max_records_per_vehicle: int = 10000,
                downsample_interval_s: float = 1.0):
        self.max_records = max_records_per_vehicle
        self.downsample_interval = downsample_interval_s
        self.telemetry_buffers: Dict[str, deque] = {}
        self.persisted_records: Dict[str, List[TelemetryRecord]] = {}
        self.subscribers: List[Callable] = []
        self.last_downsample: Dict[str, datetime] = {}
        
    def ingest(self, vehicle_id: str, data: Dict) -> None:
        """Ingest a telemetry sample."""
        record = TelemetryRecord(
            vehicle_id=vehicle_id,
            timestamp=datetime.utcnow(),
            latitude=data.get("latitude", 0.0),
            longitude=data.get("longitude", 0.0),
            altitude_m=data.get("altitude_m", 0.0),
            roll_deg=data.get("roll_deg", 0.0),
            pitch_deg=data.get("pitch_deg", 0.0),
            yaw_deg=data.get("yaw_deg", 0.0),
            ground_speed_ms=data.get("ground_speed_ms", 0.0),
            battery_pct=data.get("battery_remaining_pct", 100.0),
            flight_mode=data.get("flight_mode", "MANUAL"),
            additional={k: v for k, v in data.items()
                       if k not in ["latitude", "longitude", "altitude_m",
                                   "roll_deg", "pitch_deg", "yaw_deg",
                                   "ground_speed_ms", "battery_remaining_pct",
                                   "flight_mode"]}
        )
        
        # Buffer for downsampling
        buffer = self.telemetry_buffers.setdefault(vehicle_id, deque(maxlen=1000))
        buffer.append(record)
        
        # Downsample if needed
        last = self.last_downsample.get(vehicle_id)
        now = datetime.utcnow()
        if not last or (now - last).total_seconds() >= self.downsample_interval:
            self._persist_latest(vehicle_id, record)
            self.last_downsample[vehicle_id] = now
            
        # Notify subscribers
        for sub in self.subscribers:
            try:
                sub(record)
            except Exception:
                pass
                
    def _persist_latest(self, vehicle_id: str, record: TelemetryRecord) -> None:
        """Persist a downsampled record."""
        persisted = self.persisted_records.setdefault(vehicle_id, [])
        persisted.append(record)
        # Bound memory
        if len(persisted) > self.max_records:
            self.persisted_records[vehicle_id] = persisted[-self.max_records:]
            
    def get_latest(self, vehicle_id: str) -> Optional[TelemetryRecord]:
        """Get latest telemetry record for a vehicle."""
        records = self.persisted_records.get(vehicle_id, [])
        return records[-1] if records else None
        
    def get_history(self, vehicle_id: str, limit: int = 100) -> List[TelemetryRecord]:
        """Get recent telemetry history."""
        records = self.persisted_records.get(vehicle_id, [])
        return records[-limit:]
        
    def subscribe(self, callback: Callable) -> None:
        """Subscribe to telemetry updates."""
        self.subscribers.append(callback)
        
    def get_vehicle_ids(self) -> List[str]:
        """Get list of vehicles with telemetry."""
        return list(self.persisted_records.keys())
        
    def get_statistics(self, vehicle_id: str) -> Dict:
        """Get telemetry statistics for a vehicle."""
        records = self.persisted_records.get(vehicle_id, [])
        if not records:
            return {}
        
        altitudes = [r.altitude_m for r in records]
        speeds = [r.ground_speed_ms for r in records]
        batteries = [r.battery_pct for r in records]
        
        return {
            "sample_count": len(records),
            "max_altitude_m": max(altitudes),
            "min_altitude_m": min(altitudes),
            "avg_altitude_m": sum(altitudes) / len(records),
            "max_speed_ms": max(speeds),
            "avg_speed_ms": sum(speeds) / len(records),
            "min_battery_pct": min(batteries)
        }
