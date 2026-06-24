"""Logistics Manager - Module 8 for Sprint 13."""
import uuid
from typing import Dict, Any, List, Optional


class LogisticsManager:
    def __init__(self):
        self.records: Dict[str, Any] = {}

    def create_record(
        self,
        record_type: str,
        asset_id: str,
        data: Dict[str, Any]
    ) -> str:
        record_id = str(uuid.uuid4())
        record = {
            "id": record_id,
            "type": record_type,
            "asset_id": asset_id,
            "data": data,
            "timestamp": uuid.uuid4().hex,
        }
        self.records[record_id] = record
        return record_id

    def get_record(self, record_id: str) -> Optional[Any]:
        return self.records.get(record_id)

    def list_records(self, asset_id: Optional[str] = None, record_type: Optional[str] = None) -> List[Any]:
        records = list(self.records.values())
        if asset_id:
            records = [r for r in records if r["asset_id"] == asset_id]
        if record_type:
            records = [r for r in records if r["type"] == record_type]
        return records
