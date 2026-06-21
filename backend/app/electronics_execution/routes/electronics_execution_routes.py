"""
Electronics Execution Routes
"""
import uuid
from datetime import datetime
from fastapi import APIRouter
from app.electronics_execution.schemas.schemas import (
    ElectronicsArchitectureRequest,
    ElectronicsArchitectureResponse,
    PowerSystemDesignRequest,
    PowerSystemDesignResponse,
    SignalChainDesignRequest,
    SignalChainDesignResponse,
)
from app.electronics_execution.services.electronics_architect import ElectronicsArchitect
from app.electronics_execution.services.power_system_designer import PowerSystemDesigner
from app.electronics_execution.services.signal_chain_designer import SignalChainDesigner


router = APIRouter(prefix="/electronics-execution", tags=["Electronics Execution"])
architect = ElectronicsArchitect()
power_designer = PowerSystemDesigner()
signal_designer = SignalChainDesigner()


@router.post("/architectures", response_model=ElectronicsArchitectureResponse)
async def create_architecture(request: ElectronicsArchitectureRequest):
    """Create electronics architecture"""
    result = architect.create_architecture(request.requirements)
    return ElectronicsArchitectureResponse(
        id=result["id"],
        project_id=request.project_id,
        name=request.name,
        status=result["status"],
        power_tree=result["power_tree"],
        signal_chain=result["signal_chain"],
        created_at=datetime.utcnow()
    )


@router.post("/power-systems", response_model=PowerSystemDesignResponse)
async def design_power_system(request: PowerSystemDesignRequest):
    """Design power system"""
    result = power_designer.design(request.requirements)
    return PowerSystemDesignResponse(
        id=result["id"],
        electronics_architecture_id=request.electronics_architecture_id,
        voltages=result["voltages"],
        regulators=result["regulators"],
        created_at=datetime.utcnow()
    )


@router.post("/signal-chains", response_model=SignalChainDesignResponse)
async def design_signal_chain(request: SignalChainDesignRequest):
    """Design signal chain"""
    result = signal_designer.design(request.requirements)
    return SignalChainDesignResponse(
        id=result["id"],
        electronics_architecture_id=request.electronics_architecture_id,
        sensors=result["sensors"],
        interfaces=result["interfaces"],
        created_at=datetime.utcnow()
    )
