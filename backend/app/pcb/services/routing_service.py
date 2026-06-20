"""
PCB Routing Service
"""
import uuid
import time
from datetime import datetime
from app.pcb.schemas.schemas import (
    PCBRoutingRequest,
    PCBRoutingResponse,
    RoutingRule,
)


class RoutingService:
    @staticmethod
    def generate(request: PCBRoutingRequest) -> PCBRoutingResponse:
        start_time = time.time()

        rules = [
            RoutingRule(
                signal_name="3.3V Power",
                trace_width_mm=0.5,
                trace_spacing_mm=0.2,
                priority=1
            ),
            RoutingRule(
                signal_name="GND",
                trace_width_mm=1.0,
                trace_spacing_mm=0.3,
                priority=1
            ),
            RoutingRule(
                signal_name="I2C SCL",
                trace_width_mm=0.2,
                trace_spacing_mm=0.2,
                priority=2
            ),
            RoutingRule(
                signal_name="I2C SDA",
                trace_width_mm=0.2,
                trace_spacing_mm=0.2,
                priority=2
            ),
            RoutingRule(
                signal_name="UART TX",
                trace_width_mm=0.2,
                trace_spacing_mm=0.2,
                priority=3
            ),
        ]

        return PCBRoutingResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            routing_rules=rules,
            routing_priorities=[
                {"category": "Power", "priority": 1},
                {"category": "Ground", "priority": 1},
                {"category": "Critical Signals", "priority": 2},
                {"category": "General Signals", "priority": 3},
            ],
            execution_time_ms=(time.time() - start_time) * 1000,
            created_at=datetime.utcnow(),
        )
