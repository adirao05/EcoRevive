from pydantic import BaseModel, Field
from typing import Literal, Optional

class ProductCreate(BaseModel):
    category: Literal["Laptop", "Smartphone"]
    brand: str = Field(min_length=1, max_length=80)
    model: str = Field(min_length=1, max_length=100)
    manufacture_year: int = Field(ge=2005, le=2035)
    region: str = Field(default="Chennai", min_length=2, max_length=80)
    battery_health: Optional[float] = Field(default=80, ge=0, le=100)
    repair_count: int = Field(default=0, ge=0, le=50)
    functional_status: Literal["Functional", "Partially functional", "Non-functional"]
    repair_cost: float = Field(default=0, ge=0)
    resale_value: float = Field(default=0, ge=0)
    material_value: float = Field(default=0, ge=0)
    hazard_level: float = Field(default=.1, ge=0, le=1)

class EventCreate(BaseModel):
    event_type: Literal["COLLECTED","INSPECTED","REPAIRED","REFURBISHED","COMPONENT_RECOVERY","RECYCLED","CUSTODY_TRANSFER"]
    actor: str = Field(default="EcoRevive Operator", min_length=2, max_length=100)
    notes: str = Field(default="", max_length=1000)

class OptimizeRequest(BaseModel):
    start_latitude: float = 13.0827
    start_longitude: float = 80.2707
    max_stops: int = Field(default=20, ge=1, le=100)
