"""
Booking Trades API Routes
Provides trade and service data optimized for the booking flow
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from uuid import UUID

from app.api.deps import get_supabase_client
from supabase import Client


class BookingService(BaseModel):
    """Service model optimized for booking flow"""
    id: str
    service_id: str
    name: str
    description: Optional[str] = None
    base_price: Optional[float] = None
    estimated_duration_minutes: Optional[int] = None
    is_bookable: bool = True
    service_type_code: Optional[str] = None
    service_type_display_name: Optional[str] = None


class BookingTrade(BaseModel):
    """Trade model optimized for booking flow"""
    trade_slug: str
    trade_display_name: str
    trade_icon: str
    trade_color: str
    market_type: str
    service_count: int
    services: List[BookingService]


class BookingTradesResponse(BaseModel):
    """Response model for booking trades"""
    trades: List[BookingTrade]
    total_services: int


router = APIRouter()


@router.get("/booking-trades", response_model=BookingTradesResponse)
async def get_booking_trades(
    business_id: UUID,
    supabase: Client = Depends(get_supabase_client)
) -> BookingTradesResponse:
    """
    Get trades and services optimized for the booking flow.
    
    Returns trades with their associated bookable services, including
    trade metadata (icons, colors) and service details.
    """
    try:
        # Query trades with their services using the service catalog view
        response = supabase.table("v_service_catalog").select(
            """
            trade_id,
            trade_slug,
            trade_display_name,
            trade_icon,
            trade_color,
            trade_market_type,
            id,
            service_name,
            description,
            base_price,
            estimated_duration_minutes,
            is_bookable,
            service_type_code,
            service_type_display_name
            """
        ).eq("business_id", str(business_id)).eq("is_active", True).eq("is_bookable", True).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="No bookable services found for this business")
        
        # Group services by trade
        trades_dict = {}
        total_services = 0
        
        for row in response.data:
            trade_slug = row["trade_slug"]
            
            if trade_slug not in trades_dict:
                trades_dict[trade_slug] = {
                    "trade_slug": trade_slug,
                    "trade_display_name": row["trade_display_name"],
                    "trade_icon": row["trade_icon"],
                    "trade_color": row["trade_color"],
                    "market_type": row["trade_market_type"],
                    "service_count": 0,
                    "services": []
                }
            
            # Add service to trade
            service = BookingService(
                id=row["id"],
                service_id=row["id"],  # Using id as service_id since that's the business_service id
                name=row["service_name"],
                description=row["description"],
                base_price=row["base_price"],
                estimated_duration_minutes=row["estimated_duration_minutes"],
                is_bookable=row["is_bookable"],
                service_type_code=row["service_type_code"],
                service_type_display_name=row["service_type_display_name"]
            )
            
            trades_dict[trade_slug]["services"].append(service)
            trades_dict[trade_slug]["service_count"] += 1
            total_services += 1
        
        # Convert to list and sort by trade display name
        trades = [
            BookingTrade(**trade_data) 
            for trade_data in sorted(
                trades_dict.values(), 
                key=lambda x: x["trade_display_name"]
            )
        ]
        
        return BookingTradesResponse(
            trades=trades,
            total_services=total_services
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to retrieve booking trades: {str(e)}")
