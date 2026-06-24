"""
Process Planning Engine — generates manufacturing process plans.
"""
from typing import Dict, List
from sprint7.schemas.enums import ProcessType

class ProcessPlan:
    """A complete manufacturing process plan."""
    def __init__(self, part_number: str, process_type: ProcessType):
        self.part_number = part_number
        self.process_type = process_type
        self.operations: List[Dict] = []
        self.total_time_minutes: float = 0.0
        self.tooling_required: List[str] = []
        self.material_required: Dict[str, float] = {}
        self.quality_checks: List[Dict] = []
        
    def add_operation(self, name: str, duration_min: float, parameters: Dict = None,
                     machine_type: str = None, skill_level: str = "OPERATOR") -> None:
        self.operations.append({
            "sequence": len(self.operations) + 1,
            "name": name,
            "duration_minutes": duration_min,
            "parameters": parameters or {},
            "machine_type": machine_type,
            "skill_level": skill_level
        })
        self.total_time_minutes += duration_min


class ProcessGenerator:
    """Generates process plans for different manufacturing methods."""
    
    def generate_cnc_milling(self, part_specs: Dict) -> ProcessPlan:
        """Generate CNC milling process plan."""
        plan = ProcessPlan(part_specs.get("part_number", "PART"), ProcessType.CNC_MILLING)
        
        material = part_specs.get("material", "ALUMINUM_6061")
        thickness_mm = part_specs.get("thickness_mm", 10)
        complexity = part_specs.get("complexity", "MEDIUM")  # LOW, MEDIUM, HIGH
        
        # Setup
        plan.add_operation("Load material stock", 5, machine_type="CNC_MILL")
        plan.add_operation("Install vise and indicate", 10, machine_type="CNC_MILL")
        plan.add_operation("Set work coordinate system", 5, machine_type="CNC_MILL")
        plan.tooling_required.extend(["End mill 10mm", "End mill 6mm", "Drill 3mm", "Face mill"])
        
        # Machining operations based on complexity
        plan.add_operation("Face top surface", 3, {"depth_mm": 0.5}, machine_type="CNC_MILL")
        
        if complexity in ["MEDIUM", "HIGH"]:
            plan.add_operation("Rough profile", 15, {"depth_per_pass_mm": 2}, machine_type="CNC_MILL")
            plan.add_operation("Finish profile", 10, {"depth_per_pass_mm": 0.2}, machine_type="CNC_MILL")
            
        if complexity == "HIGH":
            plan.add_operation("Pocket roughing", 20, machine_type="CNC_MILL")
            plan.add_operation("Pocket finishing", 15, machine_type="CNC_MILL")
            plan.add_operation("Drill holes", 5, machine_type="CNC_MILL")
            plan.add_operation("Tap holes", 3, machine_type="CNC_MILL")
            plan.add_operation("Chamfer edges", 5, machine_type="CNC_MILL")
            
        # Deburring and inspection
        plan.add_operation("Deburr edges", 5, skill_level="OPERATOR")
        plan.add_operation("Final inspection", 10, skill_level="INSPECTOR")
        
        plan.quality_checks.append({
            "name": "Dimensional inspection",
            "method": "CMM or calipers",
            "critical_dimensions": part_specs.get("critical_dims", [])
        })
        
        plan.material_required[material] = part_specs.get("material_volume_cm3", 100)
        
        return plan
        
    def generate_3d_printing(self, part_specs: Dict) -> ProcessPlan:
        """Generate 3D printing (FDM/SLA/SLS) process plan."""
        plan = ProcessPlan(part_specs.get("part_number", "PART"), ProcessType.THREE_D_PRINTING)
        
        technology = part_specs.get("technology", "FDM")  # FDM, SLA, SLS
        material = part_specs.get("material", "PLA")
        volume_cm3 = part_specs.get("volume_cm3", 50)
        infill_pct = part_specs.get("infill_pct", 20)
        
        # Pre-processing
        plan.add_operation("Slice model", 5, {
            "layer_height_mm": 0.2 if technology == "FDM" else 0.05,
            "infill_pct": infill_pct,
            "support": part_specs.get("needs_support", True)
        }, machine_type="SLICER")
        
        # Machine setup
        plan.add_operation("Load filament/resin", 5, machine_type="3D_PRINTER")
        plan.add_operation("Level build plate", 10, machine_type="3D_PRINTER")
        
        # Print time estimation (rough: 1 hour per 10cm³ at 0.2mm layers)
        print_hours = volume_cm3 / 10 * (100 / max(infill_pct, 1))
        plan.add_operation("Print part", print_hours * 60, machine_type="3D_PRINTER")
        
        # Post-processing
        if technology == "FDM":
            plan.add_operation("Remove supports", 10, skill_level="OPERATOR")
            plan.add_operation("Sand surfaces", 15, skill_level="OPERATOR")
        elif technology == "SLA":
            plan.add_operation("Wash in IPA", 15, machine_type="WASH_STATION")
            plan.add_operation("UV cure", 30, machine_type="UV_OVEN")
            plan.add_operation("Remove supports", 10, skill_level="OPERATOR")
            
        plan.add_operation("Final inspection", 5, skill_level="INSPECTOR")
        
        plan.material_required[material] = volume_cm3 * 1.2  # 20% waste factor
        plan.quality_checks.append({
            "name": "Visual and dimensional inspection",
            "method": "Calipers + visual"
        })
        
        return plan
        
    def generate_pcb_assembly(self, part_specs: Dict) -> ProcessPlan:
        """Generate PCB assembly process plan."""
        plan = ProcessPlan(part_specs.get("part_number", "PCB"), ProcessType.PCB_ASSEMBLY)
        
        smd_count = part_specs.get("smd_components", 50)
        th_count = part_specs.get("th_components", 10)
        bgas = part_specs.get("bga_components", 0)
        quantity = part_specs.get("quantity", 1)
        
        # Solder paste application
        plan.add_operation("Apply solder paste (stencil)", 5 * quantity,
                          machine_type="PASTE_PRINTER")
        plan.tooling_required.append(f"Solder paste stencil for {part_specs.get('part_number')}")
        
        # SMT placement
        plan.add_operation("Pick and place SMD components",
                          max(5, smd_count * 0.1) * quantity,
                          machine_type="PICK_AND_PLACE")
                          
        # Reflow
        plan.add_operation("Reflow soldering", 15 * quantity,
                          {"profile": "LEAD_FREE"},
                          machine_type="REFLOW_OVEN")
                          
        # AOI inspection
        plan.add_operation("Automated optical inspection", 5 * quantity,
                          machine_type="AOI")
                          
        # Through-hole (if any)
        if th_count > 0:
            plan.add_operation("Insert TH components", 10 * quantity, skill_level="TECHNICIAN")
            plan.add_operation("Wave solder TH components", 10 * quantity,
                              machine_type="WAVE_SOLDER")
                              
        # BGA rework (if any)
        if bgas > 0:
            plan.add_operation("BGA placement and reflow", 20 * quantity * bgas,
                              machine_type="BGA_REWORK")
            plan.add_operation("BGA X-ray inspection", 10 * quantity * bgas,
                              machine_type="XRAY")
                              
        # Final steps
        plan.add_operation("Conformal coating (if required)", 10 * quantity,
                          machine_type="COATING_SYSTEM")
        plan.add_operation("Final inspection and testing", 15 * quantity,
                          skill_level="TECHNICIAN")
                          
        plan.quality_checks.extend([
            {"name": "AOI inspection", "method": "Automated optical"},
            {"name": "ICT/Flying probe", "method": "Electrical test"},
            {"name": "Visual inspection", "method": "IPC-A-610 Class 2/3"}
        ])
        
        return plan
        
    def generate_composite(self, part_specs: Dict) -> ProcessPlan:
        """Generate composite manufacturing process plan."""
        plan = ProcessPlan(part_specs.get("part_number", "COMP"), ProcessType.COMPOSITE)
        
        layup_type = part_specs.get("layup_type", "WET_LAYUP")  # WET_LAYUP, PREPREG, VARI
        plies = part_specs.get("plies", 8)
        area_m2 = part_specs.get("area_m2", 0.1)
        
        # Mold prep
        plan.add_operation("Prepare mold (clean, apply release)", 30, skill_level="TECHNICIAN")
        
        # Layup
        if layup_type == "PREPREG":
            plan.add_operation("Cut prepreg plies", 60, skill_level="TECHNICIAN")
            plan.add_operation("Layup plies with consolidation", plies * 5,
                              skill_level="TECHNICIAN")
            plan.add_operation("Vacuum bag and debulk", 30, machine_type="VACUUM_PUMP")
            plan.add_operation("Autoclave cure", 240,
                              {"temp_c": 120, "pressure_bar": 3},
                              machine_type="AUTOCLAVE")
        else:
            plan.add_operation("Cut dry fabric", 30, skill_level="TECHNICIAN")
            plan.add_operation("Mix resin system", 15, skill_level="TECHNICIAN")
            plan.add_operation("Wet layup plies", plies * 8, skill_level="TECHNICIAN")
            plan.add_operation("Vacuum bag", 20, machine_type="VACUUM_PUMP")
            plan.add_operation("Cure at room temp", 1440, skill_level="OPERATOR")
            
        # Demold and trim
        plan.add_operation("Demold part", 20, skill_level="TECHNICIAN")
        plan.add_operation("Trim edges", 30, machine_type="CNC_MILL")
        plan.add_operation("Drill holes", 15, machine_type="CNC_MILL")
        
        # Inspection
        plan.add_operation("Visual inspection", 15, skill_level="INSPECTOR")
        plan.add_operation("NDT inspection (if required)", 30,
                          machine_type="ULTRASONIC")
                          
        plan.quality_checks.extend([
            {"name": "Visual per AMS-STD-600", "method": "Visual"},
            {"name": "Ultrasonic C-scan", "method": "NDT"},
            {"name": "Dimensional", "method": "Fixture + CMM"}
        ])
        
        return plan
        
    def generate_for_part(self, part_specs: Dict) -> ProcessPlan:
        """Route to appropriate process generator based on part type."""
        process_type = part_specs.get("process_type", "CNC_MILLING")
        
        generators = {
            "CNC_MILLING": self.generate_cnc_milling,
            "CNC_TURNING": self.generate_cnc_milling,  # Similar
            "THREE_D_PRINTING": self.generate_3d_printing,
            "PCB_ASSEMBLY": self.generate_pcb_assembly,
            "COMPOSITE": self.generate_composite,
        }
        
        generator = generators.get(process_type, self.generate_cnc_milling)
        return generator(part_specs)
