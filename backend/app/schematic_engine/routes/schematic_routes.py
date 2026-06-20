from fastapi import APIRouter, HTTPException
from app.schematic_engine.schemas.requests import SchematicGenerateRequest
from app.schematic_engine.schemas.engineering_report import EngineeringReport
from app.schematic_engine.services.circuit_topology_service import CircuitTopologyService
from app.schematic_engine.services.power_tree_service import PowerTreeService
from app.schematic_engine.services.pin_mapping_service import PinMappingService
from app.schematic_engine.services.connection_engine import ConnectionEngine
from app.schematic_engine.services.netlist_generator import NetlistGenerator
from app.schematic_engine.services.erc_service import ERCService
from app.schematic_engine.services.schematic_review_service import SchematicReviewService
from app.schematic_engine.services.schematic_generator import SchematicGenerator
from app.schematic_engine.repositories.schematic_repository import SchematicRepository

router = APIRouter(prefix="/schematics", tags=["Schematic Generation Engine"])

repo = SchematicRepository()
topo_svc = CircuitTopologyService()
pwr_svc = PowerTreeService()
pin_svc = PinMappingService()
conn_svc = ConnectionEngine()
net_svc = NetlistGenerator()
erc_svc = ERCService()
rev_svc = SchematicReviewService()

generator = SchematicGenerator(topo_svc, pwr_svc, pin_svc, conn_svc, net_svc, erc_svc, rev_svc)

@router.post("/generate")
async def generate_schematic(req: SchematicGenerateRequest):
    try:
        result = generator.generate_full_schematic(req.model_dump())
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/pin-map", response_model=EngineeringReport)
async def map_pins(req: SchematicGenerateRequest):
    return pin_svc.assign_pins(req.mcu_pinout, req.required_functions)

@router.post("/power-tree", response_model=EngineeringReport)
async def gen_power_tree(req: SchematicGenerateRequest):
    return pwr_svc.generate_tree(req.input_voltage, req.power_rails)

@router.post("/erc", response_model=EngineeringReport)
async def run_erc(req: SchematicGenerateRequest):
    # In a real app, this would take an existing netlist ID
    pin_rep = pin_svc.assign_pins(req.mcu_pinout, req.required_functions)
    conn_rep = conn_svc.build_nets(pin_rep.final_results['pin_mapping'], {"rails": []})
    net_rep = net_svc.generate([], conn_rep.final_results['nets'])
    return erc_svc.run_erc(net_rep.final_results['json_netlist'])

@router.get("/{schematic_id}")
async def get_schematic(schematic_id: str):
    return repo.get_schematic(schematic_id)
