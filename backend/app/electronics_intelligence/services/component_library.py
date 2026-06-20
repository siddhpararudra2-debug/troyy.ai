"""
Component Library Service
Predefined electronic components and component management.
"""

import uuid
from typing import Dict, List, Any
from app.electronics_intelligence.schemas.schemas import Component


def get_predefined_components() -> List[Dict[str, Any]]:
    """Get all predefined components for initialization."""
    return [
        # Microcontrollers
        {
            "id": str(uuid.uuid4()),
            "component_type": "mcu",
            "manufacturer": "STMicroelectronics",
            "part_number": "STM32F407VGT6",
            "description": "High-performance STM32F407 ARM Cortex-M4 MCU",
            "specifications": {
                "core": "ARM Cortex-M4F",
                "clock_speed_mhz": 168,
                "flash_kb": 1024,
                "sram_kb": 192,
                "gpio_count": 140,
                "adc_channels": 24,
                "adc_resolution_bits": 12,
                "dac_channels": 2,
                "timers": 17,
                "pwm_channels": 30,
                "uart_count": 6,
                "spi_count": 3,
                "i2c_count": 3,
                "can_count": 2,
                "usb": "OTG FS/HS",
                "ethernet": True,
                "dma_channels": 16,
            },
            "package": "LQFP100",
            "operating_voltage_min": 1.8,
            "operating_voltage_max": 3.6,
            "operating_current_max": 120,
            "operating_temp_min": -40,
            "operating_temp_max": 85,
            "interfaces": ["UART", "SPI", "I2C", "CAN", "USB", "Ethernet", "SDIO"],
            "cost_usd": 8.50,
            "availability_score": 0.95,
            "datasheet_url": "https://www.st.com/resource/en/datasheet/stm32f407vg.pdf",
        },
        {
            "id": str(uuid.uuid4()),
            "component_type": "mcu",
            "manufacturer": "Espressif",
            "part_number": "ESP32-WROOM-32",
            "description": "Dual-core Wi-Fi & Bluetooth MCU module",
            "specifications": {
                "core": "Xtensa LX6 (Dual-core)",
                "clock_speed_mhz": 240,
                "flash_kb": 4096,
                "sram_kb": 520,
                "gpio_count": 34,
                "adc_channels": 18,
                "adc_resolution_bits": 12,
                "dac_channels": 2,
                "timers": 4,
                "pwm_channels": 16,
                "uart_count": 3,
                "spi_count": 4,
                "i2c_count": 2,
                "wifi": "802.11 b/g/n",
                "bluetooth": "BLE 4.2, Classic",
            },
            "package": "Module",
            "operating_voltage_min": 2.3,
            "operating_voltage_max": 3.6,
            "operating_current_max": 240,
            "operating_temp_min": -40,
            "operating_temp_max": 125,
            "interfaces": ["UART", "SPI", "I2C", "Wi-Fi", "Bluetooth"],
            "cost_usd": 3.50,
            "availability_score": 0.98,
            "datasheet_url": "https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32_datasheet_en.pdf",
        },
        {
            "id": str(uuid.uuid4()),
            "component_type": "mcu",
            "manufacturer": "Raspberry Pi",
            "part_number": "RP2040",
            "description": "Dual-core ARM Cortex-M0+ MCU",
            "specifications": {
                "core": "ARM Cortex-M0+ (Dual-core)",
                "clock_speed_mhz": 133,
                "flash_kb": 0,  # External flash
                "sram_kb": 264,
                "gpio_count": 30,
                "adc_channels": 4,
                "adc_resolution_bits": 12,
                "timers": 8,
                "pwm_channels": 16,
                "uart_count": 2,
                "spi_count": 2,
                "i2c_count": 2,
                "pio_sm": 8,
            },
            "package": "QFN56",
            "operating_voltage_min": 1.8,
            "operating_voltage_max": 3.3,
            "operating_current_max": 100,
            "operating_temp_min": -40,
            "operating_temp_max": 85,
            "interfaces": ["UART", "SPI", "I2C", "PIO"],
            "cost_usd": 1.00,
            "availability_score": 0.92,
            "datasheet_url": "https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf",
        },
        # Sensors
        {
            "id": str(uuid.uuid4()),
            "component_type": "sensor",
            "manufacturer": "Bosch",
            "part_number": "BME280",
            "description": "Combined humidity, pressure, and temperature sensor",
            "specifications": {
                "sensor_type": "environmental",
                "temperature_range": "-40 to +85",
                "temperature_accuracy": "+-1.0",
                "pressure_range": "300 to 1100 hPa",
                "pressure_accuracy": "+-1 hPa",
                "humidity_range": "0 to 100%",
                "humidity_accuracy": "+-3%",
                "supply_current": "2.7 uA",
            },
            "package": "LGA",
            "operating_voltage_min": 1.71,
            "operating_voltage_max": 3.6,
            "operating_current_max": 0.0027,
            "operating_temp_min": -40,
            "operating_temp_max": 85,
            "interfaces": ["I2C", "SPI"],
            "cost_usd": 2.20,
            "availability_score": 0.95,
            "datasheet_url": "https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf",
        },
        {
            "id": str(uuid.uuid4()),
            "component_type": "sensor",
            "manufacturer": "TDK InvenSense",
            "part_number": "MPU6050",
            "description": "6-axis motion tracking device (accelerometer + gyroscope)",
            "specifications": {
                "sensor_type": "imu",
                "accel_range": "±2, ±4, ±8, ±16 g",
                "gyro_range": "±250, ±500, ±1000, ±2000 °/s",
                "temp_sensor": True,
                "supply_current": "3.9 mA",
            },
            "package": "QFN24",
            "operating_voltage_min": 2.375,
            "operating_voltage_max": 3.46,
            "operating_current_max": 3.9,
            "operating_temp_min": -40,
            "operating_temp_max": 85,
            "interfaces": ["I2C", "SPI"],
            "cost_usd": 1.50,
            "availability_score": 0.96,
            "datasheet_url": "https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet1.pdf",
        },
        # Regulators
        {
            "id": str(uuid.uuid4()),
            "component_type": "regulator",
            "manufacturer": "Texas Instruments",
            "part_number": "AMS1117-3.3",
            "description": "3.3V 1A linear voltage regulator (LDO)",
            "specifications": {
                "regulator_type": "ldo",
                "output_voltage": 3.3,
                "output_current_max": 1.0,
                "dropout_voltage": "1.1V @ 1A",
                "line_regulation": "0.2%",
                "load_regulation": "0.4%",
            },
            "package": "SOT-223, TO-252",
            "operating_voltage_min": 4.75,
            "operating_voltage_max": 15,
            "operating_current_max": 1000,
            "operating_temp_min": -40,
            "operating_temp_max": 125,
            "interfaces": [],
            "cost_usd": 0.30,
            "availability_score": 0.99,
            "datasheet_url": "https://www.ti.com/lit/ds/symlink/ams1117.pdf",
        },
        {
            "id": str(uuid.uuid4()),
            "component_type": "regulator",
            "manufacturer": "Texas Instruments",
            "part_number": "LM2596",
            "description": "3A step-down switching regulator",
            "specifications": {
                "regulator_type": "buck",
                "input_voltage_range": "4.5 to 40V",
                "output_voltage_range": "1.23 to 37V",
                "output_current_max": 3.0,
                "switching_frequency": "150 kHz",
                "efficiency": "92%",
            },
            "package": "TO-263, TO-220",
            "operating_voltage_min": 4.5,
            "operating_voltage_max": 40,
            "operating_current_max": 3000,
            "operating_temp_min": -40,
            "operating_temp_max": 125,
            "interfaces": [],
            "cost_usd": 0.80,
            "availability_score": 0.98,
            "datasheet_url": "https://www.ti.com/lit/ds/symlink/lm2596.pdf",
        },
        # MOSFETs
        {
            "id": str(uuid.uuid4()),
            "component_type": "mosfet",
            "manufacturer": "Infineon",
            "part_number": "IRL540N",
            "description": "N-channel power MOSFET",
            "specifications": {
                "mosfet_type": "n-channel",
                "vds": 100,
                "id": 33,
                "rds_on": "0.077 ohm",
                "vgs_th": "2 to 4V",
                "package": "TO-220",
            },
            "package": "TO-220",
            "operating_voltage_min": 0,
            "operating_voltage_max": 100,
            "operating_current_max": 33000,
            "operating_temp_min": -55,
            "operating_temp_max": 175,
            "interfaces": [],
            "cost_usd": 0.60,
            "availability_score": 0.97,
            "datasheet_url": "https://www.infineon.com/dgdl/Infineon-IRL540N-DataSheet-v01_01-EN.pdf",
        },
        # Communication
        {
            "id": str(uuid.uuid4()),
            "component_type": "communication",
            "manufacturer": "Maxim",
            "part_number": "MAX485",
            "description": "RS-485/RS-422 transceiver",
            "specifications": {
                "protocol": "rs485",
                "data_rate": "2.5 Mbps",
                "supply_voltage": "5V",
                "num_drivers": 1,
                "num_receivers": 1,
            },
            "package": "DIP8, SOIC8",
            "operating_voltage_min": 4.75,
            "operating_voltage_max": 5.25,
            "operating_current_max": 300,
            "operating_temp_min": -40,
            "operating_temp_max": 85,
            "interfaces": ["UART", "RS-485"],
            "cost_usd": 0.45,
            "availability_score": 0.98,
            "datasheet_url": "https://www.analog.com/en/products/max485.html",
        },
        {
            "id": str(uuid.uuid4()),
            "component_type": "communication",
            "manufacturer": "Microchip",
            "part_number": "MCP2515",
            "description": "CAN controller with SPI interface",
            "specifications": {
                "protocol": "can",
                "can_version": "2.0A, 2.0B",
                "data_rate": "1 Mbps",
                "supply_voltage": "2.7 to 5.5V",
            },
            "package": "DIP18, SOIC18",
            "operating_voltage_min": 2.7,
            "operating_voltage_max": 5.5,
            "operating_current_max": 10,
            "operating_temp_min": -40,
            "operating_temp_max": 85,
            "interfaces": ["SPI", "CAN"],
            "cost_usd": 1.20,
            "availability_score": 0.94,
            "datasheet_url": "https://www.microchip.com/en-us/product/MCP2515",
        },
    ]


def get_components_by_type(component_type: str) -> List[Dict[str, Any]]:
    """Get all components of a specific type."""
    components = get_predefined_components()
    return [c for c in components if c["component_type"] == component_type]


def get_component_by_id(component_id: str) -> Dict[str, Any]:
    """Get a component by its ID."""
    components = get_predefined_components()
    for comp in components:
        if comp["id"] == component_id:
            return comp
    return None


def get_component_by_part_number(part_number: str) -> Dict[str, Any]:
    """Get a component by its part number."""
    components = get_predefined_components()
    for comp in components:
        if comp["part_number"] == part_number:
            return comp
    return None
