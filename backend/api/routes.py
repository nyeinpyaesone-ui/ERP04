"""API routes for AI ERP system."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime

from backend.models.schemas import (
    TaxCalculationRequest,
    TaxCalculationResponse,
    DeliveryCalculationRequest,
    DeliveryCalculationResponse,
    HealthCheckResponse,
    Township as TownshipSchema,
)
from backend.services.tax_service import TaxService
from backend.services.township_service import TownshipService
from backend.config import settings

router = APIRouter()

# Initialize services
tax_service = TaxService()
township_service = TownshipService()


@router.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """Check API health status."""
    return HealthCheckResponse(
        status="healthy",
        version=settings.APP_VERSION,
        database_connected=False  # Would check actual DB connection in production
    )


@router.get("/taxes", tags=["Tax"])
async def list_taxes():
    """List all available tax types."""
    return {"taxes": tax_service.list_available_taxes()}


@router.post("/tax/calculate", response_model=TaxCalculationResponse, tags=["Tax"])
async def calculate_tax(request: TaxCalculationRequest):
    """
    Calculate tax for a given amount and tax type.
    
    Supports Myanmar tax types:
    - commercial: Commercial Tax (2%)
    - income_individual: Individual Income Tax
    - income_corporate: Corporate Income Tax
    - customs: Customs Duty
    - specific_goods: Specific Goods Tax
    - property: Property Tax
    """
    try:
        result = tax_service.calculate_tax(
            amount=request.amount,
            tax_type=request.tax_type,
            township=request.township
        )
        return TaxCalculationResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/townships", response_model=List[TownshipSchema], tags=["Township"])
async def list_townships(
    state: Optional[str] = Query(None, description="Filter by state/region"),
    district: Optional[str] = Query(None, description="Filter by district"),
    search: Optional[str] = Query(None, description="Search by name")
):
    """List townships with optional filters."""
    if search:
        results = township_service.search_townships(search)
    elif state:
        results = township_service.get_townships_by_state(state)
    elif district:
        results = township_service.get_townships_by_district(district)
    else:
        results = township_service.get_all_townships()
    
    return results


@router.get("/townships/{township_name}", tags=["Township"])
async def get_township(township_name: str):
    """Get details of a specific township."""
    township = township_service.get_township_by_name(township_name)
    if not township:
        raise HTTPException(
            status_code=404, 
            detail=f"Township '{township_name}' not found"
        )
    return township


@router.post("/delivery/calculate", response_model=DeliveryCalculationResponse, tags=["Delivery"])
async def calculate_delivery(request: DeliveryCalculationRequest):
    """
    Calculate delivery cost between two townships.
    
    Uses simplified distance-based calculation.
    In production, this would integrate with actual logistics data.
    """
    # Validate townships
    from_town = township_service.get_township_by_name(request.from_township)
    to_town = township_service.get_township_by_name(request.to_township)
    
    if not from_town:
        raise HTTPException(
            status_code=404, 
            detail=f"Origin township '{request.from_township}' not found"
        )
    if not to_town:
        raise HTTPException(
            status_code=404, 
            detail=f"Destination township '{request.to_township}' not found"
        )
    
    # Simplified calculation (in production, use actual distance matrix)
    base_rate = 500  # MMK base rate
    per_km_rate = 100  # MMK per km
    per_kg_rate = 50  # MMK per kg
    
    # Mock distance (in production, calculate actual distance)
    if from_town.get("state_region") == to_town.get("state_region"):
        distance_km = 50  # Same region
    else:
        distance_km = 300  # Different regions
    
    base_cost = base_rate + (distance_km * per_km_rate)
    weight_cost = request.weight_kg * per_kg_rate
    total_cost = base_cost + weight_cost
    
    # Estimate delivery days
    if distance_km < 100:
        estimated_days = 1
    elif distance_km < 300:
        estimated_days = 2
    else:
        estimated_days = 3
    
    return DeliveryCalculationResponse(
        from_township=request.from_township,
        to_township=request.to_township,
        distance_km=distance_km,
        base_cost=base_cost,
        weight_cost=weight_cost,
        total_cost=total_cost,
        estimated_days=estimated_days
    )
