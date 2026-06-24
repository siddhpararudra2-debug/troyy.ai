"""
Manufacturing Execution System — manages work orders, production tracking, quality.
"""
from typing import Dict, List, Optional
from datetime import datetime
from sprint7.schemas.models import WorkOrder, ProductionRecord
from sprint7.schemas.enums import WorkOrderState

class MESEngine:
    """Core MES engine managing manufacturing execution."""
    
    # Valid state transitions
    TRANSITIONS = {
        WorkOrderState.CREATED: [WorkOrderState.RELEASED, WorkOrderState.SCRAPPED],
        WorkOrderState.RELEASED: [WorkOrderState.IN_PROGRESS, WorkOrderState.SCRAPPED],
        WorkOrderState.IN_PROGRESS: [WorkOrderState.ON_HOLD, WorkOrderState.COMPLETED, WorkOrderState.SCRAPPED],
        WorkOrderState.ON_HOLD: [WorkOrderState.IN_PROGRESS, WorkOrderState.SCRAPPED],
        WorkOrderState.COMPLETED: [],
        WorkOrderState.SCRAPPED: [],
    }
    
    def __init__(self):
        self.work_orders: Dict[str, WorkOrder] = {}
        self.production_records: Dict[str, ProductionRecord] = {}
        self.state_history: Dict[str, List[Dict]] = {}
        
    def create_work_order(self, project_id: str, part_number: str, quantity: int,
                         priority: int = 3) -> WorkOrder:
        """Create a new work order."""
        wo = WorkOrder(
            project_id=project_id,
            part_number=part_number,
            quantity=quantity,
            priority=priority
        )
        self.work_orders[wo.id] = wo
        self.state_history[wo.id] = [{
            "from": None,
            "to": WorkOrderState.CREATED.value,
            "timestamp": datetime.utcnow().isoformat(),
            "actor": "system"
        }]
        return wo
        
    def transition_state(self, work_order_id: str, new_state: str,
                        actor: str = "system", notes: str = "") -> WorkOrder:
        """Transition work order to new state with validation."""
        wo = self.work_orders.get(work_order_id)
        if not wo:
            raise ValueError(f"Work order {work_order_id} not found")
            
        current = WorkOrderState(wo.state)
        target = WorkOrderState(new_state)
        
        if target not in self.TRANSITIONS[current]:
            raise ValueError(f"Invalid transition: {current.value} → {target.value}")
            
        # Record transition
        self.state_history[work_order_id].append({
            "from": current.value,
            "to": target.value,
            "timestamp": datetime.utcnow().isoformat(),
            "actor": actor,
            "notes": notes
        })
        
        wo.state = target.value
        wo.updated_at = datetime.utcnow()
        
        # Set timestamps
        if target == WorkOrderState.IN_PROGRESS and not wo.actual_start:
            wo.actual_start = datetime.utcnow()
        elif target == WorkOrderState.COMPLETED:
            wo.actual_end = datetime.utcnow()
            
        return wo
        
    def record_production(self, work_order_id: str, serial_number: str,
                         operation_sequence: int, operation_name: str,
                         machine_id: str = None, operator_id: str = None,
                         parameters: Dict = None) -> ProductionRecord:
        """Record a production operation."""
        wo = self.work_orders.get(work_order_id)
        if not wo:
            raise ValueError(f"Work order {work_order_id} not found")
            
        record = ProductionRecord(
            work_order_id=work_order_id,
            serial_number=serial_number,
            operation_sequence=operation_sequence,
            operation_name=operation_name,
            machine_id=machine_id,
            operator_id=operator_id,
            parameters=parameters or {}
        )
        self.production_records[record.id] = record
        
        # Track serial number
        if serial_number not in wo.serial_numbers:
            wo.serial_numbers.append(serial_number)
            
        return record
        
    def complete_operation(self, record_id: str, quality_result: str,
                          defects: List[str] = None) -> ProductionRecord:
        """Mark a production operation as complete."""
        record = self.production_records.get(record_id)
        if not record:
            raise ValueError(f"Production record {record_id} not found")
            
        record.completed_at = datetime.utcnow()
        record.quality_result = quality_result
        record.defects = defects or []
        return record
        
    def get_work_order(self, work_order_id: str) -> Optional[WorkOrder]:
        return self.work_orders.get(work_order_id)
        
    def list_work_orders(self, state: str = None, project_id: str = None) -> List[WorkOrder]:
        result = list(self.work_orders.values())
        if state:
            result = [wo for wo in result if wo.state == state]
        if project_id:
            result = [wo for wo in result if wo.project_id == project_id]
        return sorted(result, key=lambda w: (-w.priority, w.created_at))
        
    def get_production_history(self, work_order_id: str) -> List[ProductionRecord]:
        return sorted(
            [r for r in self.production_records.values() if r.work_order_id == work_order_id],
            key=lambda r: r.operation_sequence
        )
        
    def get_state_history(self, work_order_id: str) -> List[Dict]:
        return self.state_history.get(work_order_id, [])
        
    def get_metrics(self) -> Dict:
        """Get MES metrics."""
        total = len(self.work_orders)
        by_state = {}
        for wo in self.work_orders.values():
            by_state[wo.state] = by_state.get(wo.state, 0) + 1
            
        completed = sum(1 for r in self.production_records.values() if r.completed_at)
        total_records = len(self.production_records)
        
        return {
            "total_work_orders": total,
            "by_state": by_state,
            "production_records": total_records,
            "completed_operations": completed,
            "completion_rate": completed / total_records if total_records > 0 else 0
        }
