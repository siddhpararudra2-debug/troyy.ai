"""
Manufacturing Intelligence Platform Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class BaseManufacturingRequest(BaseModel):
    project_id: str
    requirements: Optional[Dict[str, Any]] = Field(default_factory=dict)


class BOMRequest(BaseManufacturingRequest):
    cad_project_id: Optional[str] = None
    electronics_project_id: Optional[str] = None


class BOMItem(BaseModel):
    part_number: str
    name: str
    quantity: int
    material: Optional[str] = None
    source: Optional[str] = None


class BOMResponse(BaseModel):
    id: str
    project_id: str
    items: List[BOMItem]
    total_items: int
    execution_time_ms: Optional[float] = None
    created_at: datetime


class CostEstimateRequest(BaseManufacturingRequest):
    pass


class CostBreakdown(BaseModel):
    materials: float
    machining: float
    printing: float
    electronics: float
    pcb: float
    labor: float
    testing: float
    logistics: float
    total: float


class CostEstimateResponse(BaseModel):
    id: str
    project_id: str
    cost_breakdown: CostBreakdown
    unit_cost: Optional[float] = None
    batch_size: Optional[int] = None
    execution_time_ms: Optional[float] = None
    created_at: datetime


class SourcingRequest(BaseManufacturingRequest):
    part_ids: Optional[List[str]] = None


class SupplierOption(BaseModel):
    name: str
    part_number: str
    lead_time_days: int
    price: float
    availability: str


class SourcingResponse(BaseModel):
    id: str
    project_id: str
    suppliers: List[SupplierOption]
    availability_analysis: List[Dict[str, Any]]
    risk_analysis: List[Dict[str, Any]]
    execution_time_ms: Optional[float] = None
    created_at: datetime


class CNCPlanRequest(BaseManufacturingRequest):
    part_id: Optional[str] = None


class CNCOperation(BaseModel):
    name: str
    tool: str
    spindle_speed: int
    feed_rate: int
    estimated_time_min: float


class CNCPlanResponse(BaseModel):
    id: str
    project_id: str
    operations: List[CNCOperation]
    tool_selection: List[str]
    sequence: List[str]
    cycle_time_min: float
    dfm_recommendations: List[str]
    execution_time_ms: Optional[float] = None
    created_at: datetime


class PrintPlanRequest(BaseManufacturingRequest):
    part_id: Optional[str] = None
    technology: str = "FDM"


class PrintPlanResponse(BaseModel):
    id: str
    project_id: str
    orientation: str
    support_strategy: str
    material: str
    print_time_hours: float
    recommendations: List[str]
    execution_time_ms: Optional[float] = None
    created_at: datetime


class ProcurementPlanRequest(BaseManufacturingRequest):
    pass


class ProcurementPlanResponse(BaseModel):
    id: str
    project_id: str
    purchase_orders: List[Dict[str, Any]]
    supplier_list: List[str]
    lead_time_estimates: Dict[str, int]
    critical_components: List[str]
    procurement_risks: List[str]
    execution_time_ms: Optional[float] = None
    created_at: datetime


class ProductionRouteRequest(BaseManufacturingRequest):
    pass


class ProductionStep(BaseModel):
    step_number: int
    name: str
    description: str
    duration_min: Optional[float] = None


class ProductionRouteResponse(BaseModel):
    id: str
    project_id: str
    fabrication: List[ProductionStep]
    assembly: List[ProductionStep]
    testing: List[ProductionStep]
    inspection: List[ProductionStep]
    packaging: List[ProductionStep]
    execution_time_ms: Optional[float] = None
    created_at: datetime


class RiskAssessmentRequest(BaseManufacturingRequest):
    pass


class RiskItem(BaseModel):
    category: str
    severity: str
    description: str
    mitigation_plan: str


class RiskAssessmentResponse(BaseModel):
    id: str
    project_id: str
    risks: List[RiskItem]
    execution_time_ms: Optional[float] = None
    created_at: datetime


class BuildPackageRequest(BaseManufacturingRequest):
    pass


class BuildPackageResponse(BaseModel):
    id: str
    project_id: str
    cad_files: List[str]
    drawings: List[str]
    bom: str
    assembly_instructions: str
    manufacturing_plans: str
    testing_plans: str
    execution_time_ms: Optional[float] = None
    created_at: datetime
