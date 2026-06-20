"""
Tests for Electronics Intelligence Platform
"""
import pytest
from app.electronics_intelligence.services.component_recommendation_service import ComponentRecommendationService
from app.electronics_intelligence.services.microcontroller_service import MicrocontrollerSelectionService
from app.electronics_intelligence.services.sensor_selection_service import SensorSelectionService
from app.electronics_intelligence.services.compatibility_service import CompatibilityService
from app.electronics_intelligence.schemas.schemas import (
    ComponentRecommendationRequest,
    MicrocontrollerSelectionRequest,
    SensorSelectionRequest,
    CompatibilityAnalysisRequest,
)


def test_component_recommendation():
    """Test component recommendation service"""
    request = ComponentRecommendationRequest(
        project_id="test-123",
        component_type="mcu",
        requirements={"voltage_min": 3.0, "voltage_max": 3.6},
        constraints={"max_cost": 10.0},
    )
    response = ComponentRecommendationService.recommend(request)
    assert response.project_id == "test-123"
    assert response.component_type == "mcu"
    assert response.selected_component is not None


def test_mcu_selection():
    """Test MCU selection service"""
    request = MicrocontrollerSelectionRequest(
        project_id="test-123",
        requirements={},
        gpio_requirements={"count": 20},
        adc_requirements={"channels": 8},
        pwm_requirements={"channels": 6},
        memory_requirements={"flash_kb": 512, "sram_kb": 128},
        communication_requirements=["UART", "SPI"],
    )
    response = MicrocontrollerSelectionService.select(request)
    assert response.project_id == "test-123"
    assert response.selected_mcu is not None


def test_sensor_selection():
    """Test sensor selection service"""
    request = SensorSelectionRequest(
        project_id="test-123",
        sensor_type="imu",
        requirements={"interfaces": ["I2C"]},
    )
    response = SensorSelectionService.select(request)
    assert response.project_id == "test-123"
    assert response.selected_sensor is not None


def test_compatibility_analysis():
    """Test compatibility analysis"""
    from app.electronics_intelligence.services.component_library import get_predefined_components
    components = get_predefined_components()
    comp_ids = [c["id"] for c in components[:2]]
    
    request = CompatibilityAnalysisRequest(
        project_id="test-123",
        components=comp_ids,
    )
    response = CompatibilityService.analyze(request)
    assert response.project_id == "test-123"
