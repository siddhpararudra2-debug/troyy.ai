"""
Communication Selection Service
Selects communication protocols (UART, SPI, I2C, CAN, RS485, Ethernet, USB, Wireless).
"""

import uuid
import time
from typing import Dict, Any, List
from app.electronics_intelligence.schemas.schemas import (
    CommunicationSelectionRequest,
    CommunicationSelectionResponse,
    EngineeringJustification,
    Tradeoff,
)


class CommunicationSelectionService:
    """Service for selecting communication protocols."""

    PROTOCOLS = {
        "uart": {
            "name": "UART",
            "distance": "Short (<10m)",
            "speed": "Low to Medium (up to 1Mbps)",
            "wires": 2,
            "complexity": "Low",
            "use_case": "Simple point-to-point communication",
        },
        "spi": {
            "name": "SPI",
            "distance": "Very short (<1m)",
            "speed": "High (up to 100+ Mbps)",
            "wires": 4,
            "complexity": "Medium",
            "use_case": "High-speed communication with peripherals",
        },
        "i2c": {
            "name": "I2C",
            "distance": "Short (<10m)",
            "speed": "Low to Medium (up to 400kbps)",
            "wires": 2,
            "complexity": "Low",
            "use_case": "Communication with multiple sensors and peripherals",
        },
        "can": {
            "name": "CAN",
            "distance": "Medium (up to 1km)",
            "speed": "Medium (up to 1Mbps)",
            "wires": 2,
            "complexity": "High",
            "use_case": "Automotive and industrial networks",
        },
        "rs485": {
            "name": "RS-485",
            "distance": "Long (up to 1.2km)",
            "speed": "Low to Medium (up to 10Mbps)",
            "wires": 2,
            "complexity": "Medium",
            "use_case": "Industrial networks, long distances",
        },
        "ethernet": {
            "name": "Ethernet",
            "distance": "Medium (up to 100m)",
            "speed": "Very high (10/100/1000 Mbps)",
            "wires": 8,
            "complexity": "High",
            "use_case": "High-speed networking, IoT",
        },
        "usb": {
            "name": "USB",
            "distance": "Short (<5m)",
            "speed": "Very high (up to 20+ Gbps)",
            "wires": 4,
            "complexity": "High",
            "use_case": "PC peripherals, high-speed data transfer",
        },
        "wifi": {
            "name": "Wi-Fi",
            "distance": "Medium (up to 100m)",
            "speed": "High (up to 1+ Gbps)",
            "wires": 0,
            "complexity": "High",
            "use_case": "Wireless IoT, internet connectivity",
        },
        "bluetooth": {
            "name": "Bluetooth",
            "distance": "Short (<10m)",
            "speed": "Medium (up to 2 Mbps)",
            "wires": 0,
            "complexity": "Medium",
            "use_case": "Short-range wireless, wearables",
        },
    }

    @staticmethod
    def _select_protocol(request: CommunicationSelectionRequest) -> str:
        """Select the best communication protocol."""
        req_distance = request.requirements.get("distance", "short")
        req_speed = request.requirements.get("speed", "low")
        req_wireless = request.requirements.get("wireless", False)

        if req_wireless:
            if req_distance in ["medium", "long"]:
                return "wifi"
            return "bluetooth"

        if req_distance in ["long"]:
            return "rs485"
        if req_distance in ["medium"] and request.requirements.get("automotive", False):
            return "can"
        if req_speed in ["high", "very_high"]:
            return "spi"
        if request.requirements.get("multiple_devices", False):
            return "i2c"
        return "uart"

    @staticmethod
    def select(request: CommunicationSelectionRequest) -> CommunicationSelectionResponse:
        """Select communication protocol."""
        start_time = time.time()

        selected_protocol = CommunicationSelectionService._select_protocol(request)
        alternatives = []
        for proto in CommunicationSelectionService.PROTOCOLS.keys():
            if proto != selected_protocol:
                alternatives.append(proto)

        justification = EngineeringJustification(
            requirements=request.requirements,
            constraints={},
            selection_criteria=[
                "Distance requirement",
                "Speed requirement",
                "Wireless preference",
                "Use case",
            ],
            reasoning=f"Selected {selected_protocol.upper()} based on requirements.",
        )

        tradeoffs = []

        execution_time_ms = (time.time() - start_time) * 1000

        return CommunicationSelectionResponse(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            selected_protocol=selected_protocol.upper(),
            alternatives=[a.upper() for a in alternatives[:5]],
            justification=justification,
            tradeoffs=tradeoffs,
            execution_time_ms=execution_time_ms,
            created_at=time.time(),
        )
