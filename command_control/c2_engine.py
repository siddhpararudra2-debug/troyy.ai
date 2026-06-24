"""C2 Engine - Command and Control execution."""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class CommandType(str, Enum):
    """Command types."""
    MISSION_START = "mission_start"
    MISSION_PAUSE = "mission_pause"
    MISSION_ABORT = "mission_abort"
    ASSET_REDIRECT = "asset_redirect"
    FORMATION_CHANGE = "formation_change"
    PRIORITY_CHANGE = "priority_change"
    EMERGENCY_RECALL = "emergency_recall"


class CommandStatus(str, Enum):
    """Command status states."""
    PENDING = "pending"
    AUTHORIZED = "authorized"
    TRANSMITTED = "transmitted"
    ACKNOWLEDGED = "acknowledged"
    EXECUTED = "executed"
    FAILED = "failed"


class C2Engine:
    """Core Command and Control engine."""
    
    def __init__(self):
        """Initialize C2 engine."""
        self.commands: Dict[str, Dict[str, Any]] = {}
        self.command_history: List[Dict[str, Any]] = []
        self.authorized_operators: List[str] = []
    
    def issue_command(
        self,
        command_type: CommandType,
        target_id: str,
        parameters: Dict[str, Any],
        issued_by: str = "system"
    ) -> str:
        """Issue command to asset/swarm."""
        command_id = str(uuid.uuid4())
        
        command = {
            "id": command_id,
            "type": command_type.value,
            "target": target_id,
            "parameters": parameters,
            "status": CommandStatus.PENDING.value,
            "issued_by": issued_by,
            "issued_at": datetime.utcnow(),
            "authorized_at": None,
            "executed_at": None,
            "result": None,
        }
        
        self.commands[command_id] = command
        return command_id
    
    def authorize_command(
        self,
        command_id: str,
        authorized_by: str
    ) -> bool:
        """Authorize command for execution."""
        if command_id not in self.commands:
            return False
        
        command = self.commands[command_id]
        command["status"] = CommandStatus.AUTHORIZED.value
        command["authorized_at"] = datetime.utcnow()
        command["authorized_by"] = authorized_by
        
        return True
    
    def transmit_command(self, command_id: str) -> bool:
        """Transmit command to asset."""
        if command_id not in self.commands:
            return False
        
        command = self.commands[command_id]
        if command["status"] != CommandStatus.AUTHORIZED.value:
            return False
        
        command["status"] = CommandStatus.TRANSMITTED.value
        command["transmitted_at"] = datetime.utcnow()
        
        return True
    
    def acknowledge_command(
        self,
        command_id: str,
        ack_from: str
    ) -> bool:
        """Acknowledge command receipt."""
        if command_id not in self.commands:
            return False
        
        command = self.commands[command_id]
        command["status"] = CommandStatus.ACKNOWLEDGED.value
        command["acknowledged_by"] = ack_from
        command["acknowledged_at"] = datetime.utcnow()
        
        return True
    
    def execute_command(
        self,
        command_id: str,
        result: Dict[str, Any]
    ) -> bool:
        """Mark command as executed."""
        if command_id not in self.commands:
            return False
        
        command = self.commands[command_id]
        command["status"] = CommandStatus.EXECUTED.value
        command["executed_at"] = datetime.utcnow()
        command["result"] = result
        
        self.command_history.append(command.copy())
        
        return True
    
    def fail_command(
        self,
        command_id: str,
        error: str
    ) -> bool:
        """Mark command as failed."""
        if command_id not in self.commands:
            return False
        
        command = self.commands[command_id]
        command["status"] = CommandStatus.FAILED.value
        command["failed_at"] = datetime.utcnow()
        command["error"] = error
        
        self.command_history.append(command.copy())
        del self.commands[command_id]
        
        return True
    
    def get_command(self, command_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve command by ID."""
        return self.commands.get(command_id)
    
    def list_pending_commands(self, target_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List pending commands."""
        commands = [
            c for c in self.commands.values()
            if c["status"] in [CommandStatus.PENDING.value, CommandStatus.AUTHORIZED.value]
        ]
        
        if target_id:
            commands = [c for c in commands if c["target"] == target_id]
        
        return commands
    
    def get_command_metrics(self) -> Dict[str, Any]:
        """Get C2 metrics."""
        total_commands = len(self.commands) + len(self.command_history)
        executed = sum(1 for c in self.command_history if c["status"] == CommandStatus.EXECUTED.value)
        failed = sum(1 for c in self.command_history if c["status"] == CommandStatus.FAILED.value)
        
        return {
            "total_commands": total_commands,
            "executed": executed,
            "failed": failed,
            "pending": len(self.commands),
            "success_rate": executed / total_commands if total_commands > 0 else 0,
        }
