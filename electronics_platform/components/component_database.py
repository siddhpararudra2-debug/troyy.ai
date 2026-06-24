"""
Component Database — stores electronic component information.
Seed data + API integration for production.
"""
from typing import List, Dict, Optional
from datetime import datetime
from electronics_platform.schemas.models import ComponentInfo
from electronics_platform.schemas.enums import ComponentCategory, ComponentStatus

class ComponentDatabase:
    """In-memory component database with seed data."""
    
    def __init__(self):
        self.components: Dict[str, ComponentInfo] = {}
        self._seed_data()
        
    def _seed_data(self):
        """Seed with common electronic components."""
        seed = [
            # Resistors
            ComponentInfo(mpn="RC0402FR-0710KL", manufacturer="Yageo",
                         category=ComponentCategory.RESISTOR,
                         description="10kΩ 1% 0402 Resistor", package="0402",
                         footprint="Resistor_SMD:R_0402_1005Metric",
                         value_range="10kΩ", power_rating=0.0625, tolerance=0.01,
                         price_usd=0.002, stock_available=1000000),
            ComponentInfo(mpn="RC0402FR-074K7L", manufacturer="Yageo",
                         category=ComponentCategory.RESISTOR,
                         description="4.7kΩ 1% 0402 Resistor", package="0402",
                         footprint="Resistor_SMD:R_0402_1005Metric",
                         value_range="4.7kΩ", power_rating=0.0625, tolerance=0.01,
                         price_usd=0.002, stock_available=500000),
            ComponentInfo(mpn="RC0402FR-071KL", manufacturer="Yageo",
                         category=ComponentCategory.RESISTOR,
                         description="1kΩ 1% 0402 Resistor", package="0402",
                         footprint="Resistor_SMD:R_0402_1005Metric",
                         value_range="1kΩ", power_rating=0.0625, tolerance=0.01,
                         price_usd=0.002, stock_available=800000),
                         
            # Capacitors
            ComponentInfo(mpn="GRM155R71C104KA88D", manufacturer="Murata",
                         category=ComponentCategory.CAPACITOR,
                         description="100nF 16V X7R 0402 Capacitor", package="0402",
                         footprint="Capacitor_SMD:C_0402_1005Metric",
                         value_range="100nF", voltage_rating=16,
                         price_usd=0.005, stock_available=2000000),
            ComponentInfo(mpn="GRM155R71H103KA88D", manufacturer="Murata",
                         category=ComponentCategory.CAPACITOR,
                         description="10nF 50V X7R 0402 Capacitor", package="0402",
                         footprint="Capacitor_SMD:C_0402_1005Metric",
                         value_range="10nF", voltage_rating=50,
                         price_usd=0.004, stock_available=1500000),
            ComponentInfo(mpn="GRM155R61A106ME15D", manufacturer="Murata",
                         category=ComponentCategory.CAPACITOR,
                         description="10uF 10V X5R 0402 Capacitor", package="0402",
                         footprint="Capacitor_SMD:C_0402_1005Metric",
                         value_range="10uF", voltage_rating=10,
                         price_usd=0.02, stock_available=500000),
                         
            # Microcontrollers
            ComponentInfo(mpn="STM32F103C8T6", manufacturer="STMicroelectronics",
                         category=ComponentCategory.MICROCONTROLLER,
                         description="ARM Cortex-M3 MCU, 72MHz, 64KB Flash",
                         package="LQFP-48", footprint="Package_QFP:LQFP-48_7x7mm_P0.5mm",
                         price_usd=2.30, stock_available=12500,
                         properties={"flash_kb": 64, "ram_kb": 20, "gpio_count": 37,
                                    "uart": 3, "spi": 2, "i2c": 2, "adc": 2, "pwm": 15}),
            ComponentInfo(mpn="STM32F407VGT6", manufacturer="STMicroelectronics",
                         category=ComponentCategory.MICROCONTROLLER,
                         description="ARM Cortex-M4 MCU, 168MHz, 1MB Flash",
                         package="LQFP-100", footprint="Package_QFP:LQFP-100_14x14mm_P0.5mm",
                         price_usd=12.50, stock_available=5420,
                         properties={"flash_kb": 1024, "ram_kb": 192, "gpio_count": 82,
                                    "uart": 4, "spi": 3, "i2c": 3, "adc": 3, "pwm": 14}),
            ComponentInfo(mpn="ESP32-WROOM-32E", manufacturer="Espressif",
                         category=ComponentCategory.MICROCONTROLLER,
                         description="WiFi+BT SoC, 240MHz Dual-Core",
                         package="Module", footprint="RF_Module:ESP32-WROOM-32",
                         price_usd=3.50, stock_available=25000,
                         properties={"flash_kb": 4096, "ram_kb": 520, "gpio_count": 34,
                                    "uart": 3, "spi": 4, "i2c": 2, "adc": 18, "pwm": 16}),
                                    
            # Regulators
            ComponentInfo(mpn="AP2112K-3.3TRG1", manufacturer="Diodes Inc",
                         category=ComponentCategory.REGULATOR,
                         description="3.3V 600mA LDO Regulator",
                         package="SOT-23-5", footprint="Package_TO_SOT_SMD:SOT-23-5",
                         price_usd=0.20, stock_available=50000,
                         properties={"vin_max": 6.0, "vout_fixed": 3.3, "iout_max": 0.6,
                                    "topology": "LDO", "iq_ua": 80}),
            ComponentInfo(mpn="TPS5430DDAR", manufacturer="Texas Instruments",
                         category=ComponentCategory.REGULATOR,
                         description="3A 5.5-36V Step-Down Converter",
                         package="SOP-8", footprint="Package_SO:TI-SOP-8",
                         price_usd=1.50, stock_available=15000,
                         properties={"vin_max": 36, "vout_adj": True, "iout_max": 3.0,
                                    "topology": "BUCK", "efficiency": 0.95}),
                                    
            # Sensors
            ComponentInfo(mpn="BME280", manufacturer="Bosch",
                         category=ComponentCategory.SENSOR,
                         description="Temperature/Humidity/Pressure Sensor",
                         package="LGA-8", footprint="Sensor:Bosch_LGA-8_2.5x2.5mm_P0.65mm",
                         price_usd=2.50, stock_available=30000,
                         properties={"interface": "I2C/SPI", "vcc_v": 3.3}),
            ComponentInfo(mpn="MPU-6050", manufacturer="TDK InvenSense",
                         category=ComponentCategory.SENSOR,
                         description="6-Axis IMU (Gyro + Accelerometer)",
                         package="QFN-24", footprint="Sensor:InvenSense_QFN-24",
                         price_usd=3.00, stock_available=20000,
                         properties={"interface": "I2C", "vcc_v": 3.3}),
        ]
        
        for comp in seed:
            self.components[comp.mpn] = comp
            
    def search(self, category: ComponentCategory = None, package: str = None,
              manufacturer: str = None, query: str = None) -> List[ComponentInfo]:
        """Search components by criteria."""
        results = list(self.components.values())
        
        if category:
            results = [c for c in results if c.category == category]
        if package:
            results = [c for c in results if c.package == package]
        if manufacturer:
            results = [c for c in results if c.manufacturer == manufacturer]
        if query:
            query_lower = query.lower()
            results = [c for c in results if 
                      query_lower in c.description.lower() or
                      query_lower in c.mpn.lower()]
                      
        return results
        
    def get_by_mpn(self, mpn: str) -> Optional[ComponentInfo]:
        return self.components.get(mpn)
        
    def check_lifecycle(self, mpn: str) -> Dict:
        """Check lifecycle status of a component."""
        comp = self.components.get(mpn)
        if not comp:
            return {"status": "UNKNOWN", "risk": "HIGH"}
            
        risk = "LOW"
        if comp.status == ComponentStatus.NRND:
            risk = "MEDIUM"
        elif comp.status == ComponentStatus.OBSOLETE:
            risk = "CRITICAL"
        elif comp.stock_available < 100:
            risk = "MEDIUM"
            
        return {
            "mpn": mpn,
            "status": comp.status.value,
            "lifecycle_stage": comp.lifecycle_stage,
            "risk": risk,
            "stock_available": comp.stock_available,
            "alternatives": comp.alternatives
        }
