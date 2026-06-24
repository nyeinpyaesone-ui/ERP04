"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class TaxRate(BaseModel):
    """Tax rate schema."""
    tax_type: str
    rate: float
    description: str
    effective_date: Optional[str] = None


class Township(BaseModel):
    """Township schema."""
    name: str
    state_region: str
    district: Optional[str] = None
    postal_code: Optional[str] = None


class TaxCalculationRequest(BaseModel):
    """Request schema for tax calculation."""
    amount: float = Field(..., gt=0, description="Amount to calculate tax on")
    tax_type: str = Field(..., description="Type of tax (commercial, income, customs, etc.)")
    township: Optional[str] = Field(None, description="Township for local taxes")


class TaxCalculationResponse(BaseModel):
    """Response schema for tax calculation."""
    original_amount: float
    tax_type: str
    tax_rate: float
    tax_amount: float
    total_amount: float
    township: Optional[str] = None
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


class DeliveryCalculationRequest(BaseModel):
    """Request schema for delivery cost calculation."""
    from_township: str
    to_township: str
    weight_kg: float = Field(..., gt=0)
    package_type: Optional[str] = "standard"


class DeliveryCalculationResponse(BaseModel):
    """Response schema for delivery cost calculation."""
    from_township: str
    to_township: str
    distance_km: float
    base_cost: float
    weight_cost: float
    total_cost: float
    estimated_days: int


class HealthCheckResponse(BaseModel):
    """Health check response schema."""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    database_connected: bool = False


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: str
    status_code: int
