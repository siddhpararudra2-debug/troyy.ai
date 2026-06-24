"""
Machine Monitor — MQTT-based machine monitoring.
"""
import asyncio
import json
from typing import Dict, Callable, Optional
from datetime import datetime

class MachineMonitor:
    """Monitors machines via MQTT or simulated interface."""
    
    def __init__(self, factory_orchestrator, mqtt_broker: str = "localhost",
                mqtt_port: int = 1883, use_mqtt: bool = False):
        self.factory = factory_orchestrator
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.use_mqtt = use_mqtt
        self.callbacks: Dict[str, Callable] = {}
        self.running = False
        self._client = None
        
    async def start(self) -> None:
        """Start monitoring machines."""
        self.running = True
        if self.use_mqtt:
            await self._start_mqtt()
        else:
            # Simulated mode — just run heartbeat checker
            asyncio.create_task(self._heartbeat_checker())
            
    async def stop(self) -> None:
        """Stop monitoring."""
        self.running = False
        if self._client:
            await self._client.disconnect()
            
    async def _start_mqtt(self) -> None:
        """Connect to MQTT broker and subscribe to machine topics."""
        try:
            import aiomqtt
            async with aiomqtt.Client(self.mqtt_broker, self.mqtt_port) as client:
                self._client = client
                # Subscribe to all machine topics
                await client.subscribe("factory/+/status")
                await client.subscribe("factory/+/metrics")
                
                async for message in client.messages:
                    if not self.running:
                        break
                    await self._handle_mqtt_message(message)
        except ImportError:
            print("aiomqtt not available — falling back to simulated mode")
            self.use_mqtt = False
            asyncio.create_task(self._heartbeat_checker())
        except Exception as e:
            print(f"MQTT connection failed: {e} — falling back to simulated mode")
            self.use_mqtt = False
            asyncio.create_task(self._heartbeat_checker())
            
    async def _handle_mqtt_message(self, message) -> None:
        """Process incoming MQTT message."""
        topic = message.topic.value if hasattr(message.topic, 'value') else str(message.topic)
        parts = topic.split("/")
        if len(parts) >= 2:
            machine_name = parts[1]
            # Find machine by name
            machine = next((m for m in self.factory.machines.values()
                          if m.name == machine_name), None)
            if machine:
                try:
                    payload = json.loads(message.payload)
                    if "state" in payload:
                        self.factory.update_machine_state(machine.id, payload["state"])
                    if "metrics" in payload:
                        self.factory.heartbeat(machine.id, payload["metrics"])
                except json.JSONDecodeError:
                    pass
                    
    async def _heartbeat_checker(self) -> None:
        """Check for machines with stale heartbeats."""
        while self.running:
            now = datetime.utcnow()
            for machine in list(self.factory.machines.values()):
                age = (now - machine.last_heartbeat).total_seconds()
                if age > 30 and machine.state != "OFFLINE":
                    self.factory.update_machine_state(machine.id, "OFFLINE")
            await asyncio.sleep(5)
            
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Register callback for specific events."""
        self.callbacks[event_type] = callback
        
    def simulate_machine_event(self, machine_id: str, state: str,
                              metrics: Dict = None) -> None:
        """Simulate a machine event (for testing without MQTT)."""
        self.factory.update_machine_state(machine_id, state)
        if metrics:
            self.factory.heartbeat(machine_id, metrics)
