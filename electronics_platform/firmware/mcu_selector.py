"""
MCU Selector — selects microcontrollers based on design requirements.
Uses constraint satisfaction with weighted scoring.
"""
from typing import List, Dict, Optional
from electronics_platform.schemas.electronics_models import MCUInfo, MCUFamily, PeripheralType

class MCUSelector:
    """Selects optimal MCU based on requirements."""
    
    def __init__(self):
        self.mcu_database: Dict[str, MCUInfo] = {}
        self._seed_database()
        
    def _seed_database(self):
        """Seed with common MCU families."""
        mcus = [
            # STM32F1 series
            MCUInfo(
                part_number="STM32F103C8T6",
                family=MCUFamily.STM32F1,
                manufacturer="STMicroelectronics",
                package="LQFP-48",
                footprint="Package_QFP:LQFP-48_7x7mm_P0.5mm",
                flash_kb=64, ram_kb=20, clock_max_mhz=72,
                voltage_min_v=2.0, voltage_max_v=3.6,
                gpio_count=37,
                peripherals={
                    PeripheralType.UART: 3, PeripheralType.SPI: 2,
                    PeripheralType.I2C: 2, PeripheralType.USB: 1,
                    PeripheralType.TIMER: 7, PeripheralType.DMA: 2
                },
                adc_channels=10, adc_resolution_bits=12,
                pwm_channels=15, dma_channels=7,
                price_usd=2.30
            ),
            MCUInfo(
                part_number="STM32F103RCT6",
                family=MCUFamily.STM32F1,
                manufacturer="STMicroelectronics",
                package="LQFP-64",
                footprint="Package_QFP:LQFP-64_10x10mm_P0.5mm",
                flash_kb=256, ram_kb=48, clock_max_mhz=72,
                voltage_min_v=2.0, voltage_max_v=3.6,
                gpio_count=51,
                peripherals={
                    PeripheralType.UART: 5, PeripheralType.SPI: 3,
                    PeripheralType.I2C: 2, PeripheralType.USB: 1,
                    PeripheralType.CAN: 1, PeripheralType.TIMER: 8,
                    PeripheralType.DMA: 2
                },
                adc_channels=16, adc_resolution_bits=12,
                pwm_channels=15, dma_channels=12,
                price_usd=4.50
            ),
            # STM32F4 series
            MCUInfo(
                part_number="STM32F407VGT6",
                family=MCUFamily.STM32F4,
                manufacturer="STMicroelectronics",
                package="LQFP-100",
                footprint="Package_QFP:LQFP-100_14x14mm_P0.5mm",
                flash_kb=1024, ram_kb=192, clock_max_mhz=168,
                voltage_min_v=1.8, voltage_max_v=3.6,
                gpio_count=82,
                peripherals={
                    PeripheralType.UART: 4, PeripheralType.SPI: 3,
                    PeripheralType.I2C: 3, PeripheralType.USB: 2,
                    PeripheralType.CAN: 2, PeripheralType.ETHERNET: 1,
                    PeripheralType.TIMER: 14, PeripheralType.DMA: 2
                },
                adc_channels=16, adc_resolution_bits=12,
                dac_channels=2, pwm_channels=14, dma_channels=16,
                price_usd=12.50
            ),
            MCUInfo(
                part_number="STM32F411CEU6",
                family=MCUFamily.STM32F4,
                manufacturer="STMicroelectronics",
                package="UFQFPN-48",
                footprint="Package_DFN_QFN:UFQFPN-48_7x7mm_P0.5mm",
                flash_kb=512, ram_kb=128, clock_max_mhz=100,
                voltage_min_v=1.7, voltage_max_v=3.6,
                gpio_count=36,
                peripherals={
                    PeripheralType.UART: 3, PeripheralType.SPI: 5,
                    PeripheralType.I2C: 3, PeripheralType.USB: 1,
                    PeripheralType.TIMER: 6, PeripheralType.DMA: 2
                },
                adc_channels=16, adc_resolution_bits=12,
                pwm_channels=11, dma_channels=16,
                price_usd=4.20
            ),
            # ESP32 series
            MCUInfo(
                part_number="ESP32-WROOM-32E",
                family=MCUFamily.ESP32,
                manufacturer="Espressif",
                package="Module",
                footprint="RF_Module:ESP32-WROOM-32",
                flash_kb=4096, ram_kb=520, clock_max_mhz=240,
                voltage_min_v=2.3, voltage_max_v=3.6,
                gpio_count=34,
                peripherals={
                    PeripheralType.UART: 3, PeripheralType.SPI: 4,
                    PeripheralType.I2C: 2, PeripheralType.PWM: 16,
                    PeripheralType.TIMER: 4
                },
                adc_channels=18, adc_resolution_bits=12,
                dac_channels=2, pwm_channels=16,
                price_usd=3.50,
            ),
            MCUInfo(
                part_number="ESP32-S3-WROOM-1",
                family=MCUFamily.ESP32S3,
                manufacturer="Espressif",
                package="Module",
                footprint="RF_Module:ESP32-S3-WROOM-1",
                flash_kb=8192, ram_kb=512, clock_max_mhz=240,
                voltage_min_v=3.0, voltage_max_v=3.6,
                gpio_count=45,
                peripherals={
                    PeripheralType.UART: 3, PeripheralType.SPI: 4,
                    PeripheralType.I2C: 2, PeripheralType.USB: 1,
                    PeripheralType.PWM: 8, PeripheralType.TIMER: 4
                },
                adc_channels=20, adc_resolution_bits=12,
                pwm_channels=8,
                price_usd=4.50
            ),
            # RP2040
            MCUInfo(
                part_number="RP2040",
                family=MCUFamily.RP2040,
                manufacturer="Raspberry Pi",
                package="QFN-56",
                footprint="Package_DFN_QFN:QFN-56_7x7mm_P0.4mm",
                flash_kb=0, ram_kb=264, clock_max_mhz=133,
                voltage_min_v=1.8, voltage_max_v=3.3,
                gpio_count=30,
                peripherals={
                    PeripheralType.UART: 2, PeripheralType.SPI: 2,
                    PeripheralType.I2C: 2, PeripheralType.USB: 1,
                    PeripheralType.PWM: 8, PeripheralType.TIMER: 4,
                    PeripheralType.DMA: 1
                },
                adc_channels=4, adc_resolution_bits=12,
                pwm_channels=8, dma_channels=12,
                price_usd=0.70
            ),
            # AVR
            MCUInfo(
                part_number="ATMEGA328P-AU",
                family=MCUFamily.AVR_ATMEGA,
                manufacturer="Microchip",
                package="TQFP-32",
                footprint="Package_QFP:TQFP-32_7x7mm_P0.8mm",
                flash_kb=32, ram_kb=2, clock_max_mhz=20,
                voltage_min_v=2.7, voltage_max_v=5.5,
                gpio_count=23,
                peripherals={
                    PeripheralType.UART: 1, PeripheralType.SPI: 1,
                    PeripheralType.I2C: 1, PeripheralType.TIMER: 3,
                    PeripheralType.PWM: 6
                },
                adc_channels=8, adc_resolution_bits=10,
                pwm_channels=6,
                price_usd=2.00
            ),
        ]
        
        for mcu in mcus:
            self.mcu_database[mcu.part_number] = mcu
            
    def select(self, requirements: Dict) -> List[Dict]:
        """
        Select MCUs matching requirements.
        requirements: {
            "flash_kb": 64, "ram_kb": 20, "clock_mhz": 72,
            "uart": 2, "spi": 1, "i2c": 1, "adc_channels": 4,
            "gpio": 20, "voltage_v": 3.3, "usb": false, "can": false,
            "wifi": false, "ethernet": false, "package_max_pins": 100
        }
        Returns: list of {mcu, score, reasons}
        """
        scored = []
        
        for part, mcu in self.mcu_database.items():
            score = 0
            reasons = []
            
            # Hard constraints (disqualify if not met)
            if mcu.flash_kb < requirements.get("flash_kb", 0):
                continue
            if mcu.ram_kb < requirements.get("ram_kb", 0):
                continue
            if mcu.clock_max_mhz < requirements.get("clock_mhz", 0):
                continue
            if mcu.gpio_count < requirements.get("gpio", 0):
                continue
            if not (mcu.voltage_min_v <= requirements.get("voltage_v", 3.3) <= mcu.voltage_max_v):
                continue
                
            # Peripheral requirements
            for periph_type in [PeripheralType.UART, PeripheralType.SPI, 
                               PeripheralType.I2C, PeripheralType.USB,
                               PeripheralType.CAN, PeripheralType.ETHERNET]:
                required = requirements.get(periph_type.value.lower(), 0)
                available = mcu.peripherals.get(periph_type, 0)
                if available < required:
                    # Disqualify
                    break
                elif available == required:
                    score += 10
                    reasons.append(f"{periph_type.value}: exact match")
                elif available > required:
                    score += 5
                    reasons.append(f"{periph_type.value}: {available} available (>{required})")
            else:
                # ADC channels
                req_adc = requirements.get("adc_channels", 0)
                if mcu.adc_channels >= req_adc:
                    score += 10 if mcu.adc_channels == req_adc else 5
                    
                # PWM channels
                req_pwm = requirements.get("pwm_channels", 0)
                if mcu.pwm_channels >= req_pwm:
                    score += 5
                    
                # WiFi requirement
                if requirements.get("wifi") and mcu.family not in [MCUFamily.ESP32, MCUFamily.ESP32S3]:
                    continue
                    
                # Package size preference
                max_pins = requirements.get("package_max_pins", 100)
                pin_count = self._get_pin_count(mcu.package)
                if pin_count <= max_pins:
                    score += 10
                    
                # Prefer lower cost (normalize)
                score += max(0, 20 - mcu.price_usd * 2)
                
                # Prefer smaller packages (lower pin count = smaller)
                score += max(0, 10 - pin_count / 10)
                
                scored.append({
                    "mcu": mcu.model_dump(),
                    "score": score,
                    "reasons": reasons
                })
                
        # Sort by score descending
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored
        
    def _get_pin_count(self, package: str) -> int:
        """Extract pin count from package name."""
        import re
        match = re.search(r'(\d+)', package)
        return int(match.group(1)) if match else 50
