from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timedelta
from supplier_network.schemas.enums import SupplierCategory, RiskLevel, ProcurementStatus

class Supplier(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: SupplierCategory
    country: str
    certifications: List[str] = Field(default_factory=list)  # AS9100, ISO9001, etc.
    lead_time_days: int = 14
    reliability_score: float = 0.9  # 0-1
    price_index: float = 1.0  # Relative to market average
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class Component(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mpn: str  # Manufacturer Part Number
    description: str
    category: str
    specifications: Dict[str, Any] = Field(default_factory=dict)
    suppliers: List[str] = Field(default_factory=list)  # supplier IDs
    unit_price_usd: float = 0.0
    moq: int = 1  # Minimum order quantity

class Quote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    component_id: str
    supplier_id: str
    unit_price_usd: float
    lead_time_days: int
    moq: int
    valid_until: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))
    currency: str = "USD"

class ProcurementRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    component_id: str
    supplier_id: str
    quantity: int
    unit_price_usd: float
    total_cost_usd: float
    expected_delivery: datetime
    status: ProcurementStatus = ProcurementStatus.QUOTED
    order_date: datetime = Field(default_factory=datetime.utcnow)
    tracking_number: Optional[str] = None

class SupplyChainRisk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    supplier_id: str
    risk_type: str  # "GEOGRAPHIC", "FINANCIAL", "SINGLE_SOURCE", "LEAD_TIME"
    severity: RiskLevel
    description: str
    mitigation: str
    probability: float = 0.5  # 0-1
