"""
System Architecture Service
"""
import uuid
import time
from datetime import datetime
from app.system_integration.schemas.schemas import (
    SystemArchitectureRequest,
    SystemArchitectureResponse,
    SubsystemInfo,
)


class SystemArchitectureService:
    @staticmethod
    def generate(request: SystemArchitectureRequest) -> SystemArchitectureResponse:
        start_time = time.time()

        subsystems = [
            SubsystemInfo(
                name="Mechanical Subsystem",
                type="mechanical",
                subcomponents=["Frame", "Joints", "Actuators"],
            ),
            SubsystemInfo(
                name="Electronics Subsystem",
                type="electronics",
                subcomponents=["Sensors", "Controllers", "Power"],
            ),
            SubsystemInfo(
                name="PCB Subsystem",
                type="pcb",
                subcomponents=["Main Board", "Power Board", "Sensor Board"],
            ),
            SubsystemInfo(
                name="Firmware Subsystem",
                type="firmware",
                subcomponents=["RTOS", "Drivers", "Controllers"],
            ),
            SubsystemInfo(
                name="Simulation Subsystem",
                type="simulation",
                subcomponents=["Dynamics Model", "Environment Model"],
            ),
        ]
        dependencies = {
            "Mechanical Subsystem": ["Electronics Subsystem"],
            "Electronics Subsystem": ["PCB Subsystem"],
            "PCB Subsystem": ["Firmware Subsystem"],
            "Firmware Subsystem": ["Simulation Subsystem"],
        }

        signal_flow = [{"source": "Sensors", "target": "RTOS", "signal": "sensor_data"}]
        power_flow = [{"source": "Power Board", "target": "Actuators", "power": "100W"}]
        control_flow = [{"source": "Controllers", "target": "Actuators", "command": "position"}]
        mechanical_interfaces = [{"type": "mount", "from": "Frame", "to": "Actuators"}]
        software_interfaces = [{"type": "API", "from": "RTOS", "to": "Drivers"}]

        return SystemArchitectureResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            subsystem_hierarchy=subsystems,
            dependency_map=dependencies,
            signal_flow=signal_flow,
            power_flow=power_flow,
            control_flow=control_flow,
            mechanical_interfaces=mechanical_interfaces,
            software_interfaces=software_interfaces,
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow(),
        )
