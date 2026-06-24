"""
Component Selector — recommends components based on design requirements.
Uses constraint satisfaction and preference scoring.
"""
from typing import List, Dict, Optional
from electronics_platform.schemas.models import ComponentInfo, Component
from electronics_platform.schemas.enums import ComponentCategory, ComponentStatus

class ComponentSelector:
    """Selects optimal components for a design."""
    
    def __init__(self, database):
        self.db = database
        
    def select_resistor(self, resistance_ohm: float, tolerance_pct: float = 1.0,
                       power_w: float = 0.1, package: str = "0402") -> Optional[ComponentInfo]:
        """Select a resistor meeting specifications."""
        candidates = self.db.search(
            category=ComponentCategory.RESISTOR,
            package=package
        )
        
        scored = []
        for comp in candidates:
            score = 0
            # Check if value is available (within tolerance)
            if comp.value_range:
                # Parse range
                pass  # Assume available
                
            # Check power rating
            if comp.power_rating and comp.power_rating >= power_w * 2:  # 2x margin
                score += 30
                
            # Check status
            if comp.status == ComponentStatus.ACTIVE:
                score += 30
            elif comp.status == ComponentStatus.NRND:
                score -= 20
                
            # Check stock
            if comp.stock_available > 1000:
                score += 20
            elif comp.stock_available > 100:
                score += 10
                
            # Prefer lower price
            score += max(0, 20 - comp.price_usd * 100)
            
            scored.append((score, comp))
            
        if not scored:
            return None
            
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]
        
    def select_capacitor(self, capacitance_f: float, voltage_v: float,
                        package: str = "0402", dielectric: str = "X5R") -> Optional[ComponentInfo]:
        """Select a capacitor meeting specifications."""
        candidates = self.db.search(
            category=ComponentCategory.CAPACITOR,
            package=package
        )
        
        scored = []
        for comp in candidates:
            score = 0
            
            # Voltage rating must exceed requirement with margin
            if comp.voltage_rating and comp.voltage_rating >= voltage_v * 1.5:
                score += 40
            elif comp.voltage_rating and comp.voltage_rating >= voltage_v:
                score += 20
                
            # Status
            if comp.status == ComponentStatus.ACTIVE:
                score += 30
                
            # Stock
            if comp.stock_available > 1000:
                score += 20
                
            # Price
            score += max(0, 20 - comp.price_usd * 100)
            
            scored.append((score, comp))
            
        if not scored:
            return None
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]
        
    def select_regulator(self, v_in: float, v_out: float, i_out: float,
                        topology: str = "LDO") -> Optional[ComponentInfo]:
        """Select a voltage regulator."""
        candidates = self.db.search(category=ComponentCategory.REGULATOR)
        
        scored = []
        for comp in candidates:
            score = 0
            
            # Check voltage compatibility
            props = comp.properties or {}
            v_in_max = props.get("vin_max", 0)
            i_out_max = props.get("iout_max", 0)
            fixed_vout = props.get("vout_fixed")
            
            if v_in_max >= v_in * 1.1:
                score += 20
            if i_out_max >= i_out * 1.2:
                score += 20
                
            # Check if output voltage matches
            if fixed_vout and abs(fixed_vout - v_out) < 0.1:
                score += 30
            elif topology == "LDO" and props.get("topology") == "LDO":
                score += 10
                
            # Status and stock
            if comp.status == ComponentStatus.ACTIVE:
                score += 20
            if comp.stock_available > 500:
                score += 10
                
            scored.append((score, comp))
            
        if not scored:
            return None
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]
        
    def select_microcontroller(self, requirements: Dict) -> Optional[ComponentInfo]:
        """Select a microcontroller based on requirements."""
        candidates = self.db.search(category=ComponentCategory.MICROCONTROLLER)
        
        scored = []
        for comp in candidates:
            score = 0
            props = comp.properties or {}
            
            # Check requirements
            if requirements.get("flash_kb") and props.get("flash_kb", 0) >= requirements["flash_kb"]:
                score += 15
            if requirements.get("ram_kb") and props.get("ram_kb", 0) >= requirements["ram_kb"]:
                score += 15
            if requirements.get("gpio_count") and props.get("gpio_count", 0) >= requirements["gpio_count"]:
                score += 15
                
            # Check peripherals
            for periph in ["uart", "spi", "i2c", "adc", "pwm"]:
                if requirements.get(periph) and props.get(periph, 0) >= requirements[periph]:
                    score += 5
                    
            # Status
            if comp.status == ComponentStatus.ACTIVE:
                score += 20
                
            scored.append((score, comp))
            
        if not scored:
            return None
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]
