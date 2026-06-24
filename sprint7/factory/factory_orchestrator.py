"""
Factory Automation Platform — manages machine fleet, scheduling, monitoring.
"""
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
from sprint7.schemas.models import Machine, WorkOrder
from sprint7.schemas.enums import MachineState

class FactoryOrchestrator:
    """Orchestrates factory operations and machine fleet."""
    
    def __init__(self):
        self.machines: Dict[str, Machine] = {}
        self.job_queue: List[WorkOrder] = []
        self.event_log: List[Dict] = []
        
    def register_machine(self, name: str, machine_type: str,
                        capabilities: List[str] = None,
                        mqtt_topic: str = None) -> Machine:
        """Register a new machine in the factory."""
        machine = Machine(
            name=name,
            machine_type=machine_type,
            capabilities=capabilities or [],
            mqtt_topic=mqtt_topic
        )
        self.machines[machine.id] = machine
        self._log_event("MACHINE_REGISTERED", {"machine_id": machine.id, "name": name})
        return machine
        
    def update_machine_state(self, machine_id: str, new_state: str,
                            current_job: str = None) -> Machine:
        """Update machine state."""
        machine = self.machines.get(machine_id)
        if not machine:
            raise ValueError(f"Machine {machine_id} not found")
            
        old_state = machine.state
        machine.state = new_state
        machine.current_job = current_job
        machine.last_heartbeat = datetime.utcnow()
        
        self._log_event("MACHINE_STATE_CHANGE", {
            "machine_id": machine_id,
            "from": old_state,
            "to": new_state,
            "job": current_job
        })
        
        return machine
        
    def heartbeat(self, machine_id: str, metrics: Dict = None) -> Machine:
        """Process machine heartbeat with optional metrics."""
        machine = self.machines.get(machine_id)
        if not machine:
            raise ValueError(f"Machine {machine_id} not found")
            
        machine.last_heartbeat = datetime.utcnow()
        if metrics:
            machine.properties.update(metrics)
            
        return machine
        
    def schedule_job(self, work_order: WorkOrder) -> Optional[str]:
        """Schedule a work order to an available machine."""
        # Find capable machines
        capable = [m for m in self.machines.values()
                  if m.state == MachineState.IDLE.value]
                  
        if not capable:
            self.job_queue.append(work_order)
            return None
            
        # Assign to first available
        machine = capable[0]
        machine.state = MachineState.RUNNING.value
        machine.current_job = work_order.id
        work_order.assigned_machine = machine.id
        
        self._log_event("JOB_SCHEDULED", {
            "work_order_id": work_order.id,
            "machine_id": machine.id
        })
        
        return machine.id
        
    def complete_job(self, machine_id: str, work_order_id: str) -> None:
        """Mark a job as complete on a machine."""
        machine = self.machines.get(machine_id)
        if machine and machine.current_job == work_order_id:
            machine.state = MachineState.IDLE.value
            machine.current_job = None
            self._log_event("JOB_COMPLETED", {
                "machine_id": machine_id,
                "work_order_id": work_order_id
            })
            
        # Schedule next from queue
        if self.job_queue:
            next_wo = self.job_queue.pop(0)
            self.schedule_job(next_wo)
            
    def get_machine(self, machine_id: str) -> Optional[Machine]:
        return self.machines.get(machine_id)
        
    def list_machines(self, state: str = None) -> List[Machine]:
        result = list(self.machines.values())
        if state:
            result = [m for m in result if m.state == state]
        return result
        
    def get_factory_status(self) -> Dict:
        """Get overall factory status."""
        total = len(self.machines)
        by_state = {}
        for m in self.machines.values():
            by_state[m.state] = by_state.get(m.state, 0) + 1
            
        running = by_state.get(MachineState.RUNNING.value, 0)
        utilization = running / total * 100 if total > 0 else 0
        
        return {
            "total_machines": total,
            "by_state": by_state,
            "utilization_pct": utilization,
            "queued_jobs": len(self.job_queue),
            "recent_events": self.event_log[-10:]
        }
        
    def _log_event(self, event_type: str, data: Dict) -> None:
        self.event_log.append({
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
        # Keep log bounded
        if len(self.event_log) > 1000:
            self.event_log = self.event_log[-500:]
