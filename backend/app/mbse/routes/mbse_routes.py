"""
MBSE Routes
"""
from fastapi import APIRouter
from app.mbse.schemas.schemas import CreateModelRequest, ModelResponse
from app.mbse.services.architecture_model_service import ArchitectureModelService

router = APIRouter(prefix="/mbse", tags=["MBSE"])
arch_service = ArchitectureModelService()


@router.post("/model", response_model=ModelResponse)
async def create_model(request: CreateModelRequest):
    result = arch_service.create_architecture(request.name, request.type)
    return ModelResponse(**result)


@router.get("/model/{id}", response_model=ModelResponse)
async def get_model(id: str):
    result = arch_service.get_architecture(id)
    return ModelResponse(**result)
