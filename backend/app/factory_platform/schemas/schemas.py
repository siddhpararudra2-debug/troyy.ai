"""
Factory Platform Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class ProductionRunRequest(BaseModel):
    product_id: str
    quantity: int


class WorkOrderRequest(BaseModel):
    product_id: str
    quantity: int
    due_date: str
