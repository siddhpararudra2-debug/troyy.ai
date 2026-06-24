"""
Schematic Generator — produces KiCad-compatible schematic files.
Uses KiCad's S-expression format.
"""
from typing import List, Dict
import hashlib
import json
from electronics_platform.schemas.models import Schematic, Component, Net

class SchematicGenerator:
    """Generates KiCad schematic files."""
    
    KICAD_VERSION = "20231120"
    
    def generate_kicad_schematic(self, schematic: Schematic) -> str:
        """Generate a complete KiCad schematic file content."""
        lines = []
        
        # Header
        lines.append(f'(kicad_sch (version {self.KICAD_VERSION}) (generator "engineering_os")')
        lines.append(f'  (uuid "{schematic.id}")')
        
        # Paper
        lines.append('  (paper "A4")')
        
        # Lib symbols (empty for now — KiCad will resolve from libraries)
        lines.append('  (lib_symbols')
        lines.append('  )')
        
        # Components
        for i, comp in enumerate(schematic.components):
            x = 100 + (i % 5) * 50
            y = 100 + (i // 5) * 50
            lines.extend(self._generate_symbol(comp, x, y))
            
        # Nets as wires (simplified — real KiCad uses wire objects)
        pin_coords = {}
        for i, comp in enumerate(schematic.components):
            x = 100 + (i % 5) * 50
            y = 100 + (i // 5) * 50
            for j, pin in enumerate(comp.pins):
                pin_coords[(comp.ref, pin.number)] = (x + 10, y + j * 10)
                
        # Draw small wires from each pin and label them with net name
        for net in schematic.nets:
            for ref, pin_num in net.connections:
                coords = pin_coords.get((ref, pin_num))
                if coords:
                    cx, cy = coords
                    lines.append('  (wire')
                    lines.append(f'    (pts (xy {cx} {cy}) (xy {cx + 5} {cy}))')
                    lines.append(f'    (uuid "{self._generate_uuid(net.name + ref + pin_num)}")')
                    lines.append('  )')
                    
                    label_type = "global_label" if net.is_power or net.is_ground or net.net_class.value in ["POWER", "GROUND"] else "label"
                    lines.append(f'  ({label_type} "{net.name}" (at {cx + 5} {cy} 0)')
                    lines.append(f'    (effects (font (size 1.27 1.27)) (justify left))')
                    lines.append(f'    (uuid "{self._generate_uuid(net.name + ref + pin_num + "_label")}")')
                    lines.append('  )')
                    
        lines.append(')')
        return "\n".join(lines)
        
    def _generate_symbol(self, comp: Component, x: float, y: float) -> List[str]:
        lib_map = {
            "RESISTOR": "Device:R",
            "CAPACITOR": "Device:C",
            "INDUCTOR": "Device:L",
            "DIODE": "Device:D",
            "TRANSISTOR": "Device:Q",
            "LED": "Device:LED",
        }
        lib_id = lib_map.get(comp.category.value, f"Device:{comp.category.value}")
        
        symbol_lines = [
            f'  (symbol (lib_id "{lib_id}") (at {x} {y} 0)',
            f'    (in_bom yes) (on_board yes) (dnp no)',
            f'    (uuid "{comp.id}")',
            f'    (property "Reference" "{comp.ref}" (id 0) (at {x} {y - 6} 0)',
            f'      (effects (font (size 1.27 1.27)))',
            '    )',
            f'    (property "Value" "{comp.value}" (id 1) (at {x} {y + 6} 0)',
            f'      (effects (font (size 1.27 1.27)))',
            '    )',
            f'    (property "Footprint" "{comp.footprint}" (id 2) (at {x} {y + 12} 0)',
            f'      (effects (font (size 1.27 1.27)) hide)',
            '    )',
            '  )'
        ]
        return symbol_lines

    def _generate_uuid(self, seed: str) -> str:
        """Deterministically generate a UUID from a seed string."""
        h = hashlib.md5(seed.encode('utf-8')).hexdigest()
        return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"
