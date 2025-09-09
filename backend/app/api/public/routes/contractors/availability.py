"""
Contractor Availability API Routes

Public endpoints for retrieving contractor availability slots.
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import List
from datetime import date, datetime
import logging

from .schemas import AvailabilitySlot
from app.application.services.availability_service import AvailabilityService
from app.application.dto.availability_dto import AvailabilitySearchCriteria
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError, EntityNotFoundError
)
from app.infrastructure.config.dependency_injection import get_business_repository
from app.core.db import get_supabase_client
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()


def get_availability_service():
    """Dependency injection for AvailabilityService."""
    business_repo = get_business_repository()
    return AvailabilityService(business_repo)


class AvailabilitySlotsRequest(BaseModel):
    """Request body for POST /availability/slots used by the website builder."""
    business_id: str
    service_id: str | None = Field(default=None, description="Business service ID")
    postal_code: str
    country_code: str | None = "US"
    timezone: str
    date_range: dict

    class Config:
        arbitrary_types_allowed = True


@router.post("/availability/slots")
async def get_available_slots(
    payload: AvailabilitySlotsRequest,
    availability_service: AvailabilityService = Depends(get_availability_service),
):
    """
    Public endpoint that returns available time slots. This matches the
    website-builder client which POSTs to /availability/slots.

    It adapts the request into our internal AvailabilitySearchCriteria and
    returns slots in a simplified shape `{ slots: [{start, end}], first_available }`.
    """
    try:
        # Parse date range
        start_iso = payload.date_range.get("from")
        end_iso = payload.date_range.get("to")
        if not start_iso or not end_iso:
            raise ValidationError("date_range.from and date_range.to are required")

        start_date = date.fromisoformat(start_iso)
        end_date = date.fromisoformat(end_iso)

        # Determine desired duration (fallback to 60 minutes)
        duration_minutes = 60
        try:
            if payload.service_id:
                supabase = get_supabase_client()
                view = supabase.table("v_service_catalog").select(
                    "estimated_duration_minutes"
                ).eq("id", payload.service_id).limit(1).execute()
                if view.data and view.data[0].get("estimated_duration_minutes"):
                    duration_minutes = int(view.data[0]["estimated_duration_minutes"]) or 60
        except Exception:
            # Non-fatal; keep default
            pass

        # Build search criteria
        criteria = AvailabilitySearchCriteria(
            start_date=start_date,
            end_date=end_date,
            duration_minutes=duration_minutes,
            available_only=True,
        )

        # Fetch availability
        slots_dto = await availability_service.get_availability_slots(payload.business_id, criteria)

        # Transform to public response
        slots = []
        first_available_slots = []
        for s in slots_dto:
            start_dt = datetime.combine(s.date, s.start_time).isoformat()
            end_dt = datetime.combine(s.date, s.end_time).isoformat()
            if s.is_available:
                slot_data = {"start": start_dt, "end": end_dt, "capacity": 1}
                slots.append(slot_data)
                # Collect first 6 available slots for quick booking
                if len(first_available_slots) < 6:
                    first_available_slots.append(slot_data)

        return {
            "slots": slots, 
            "first_available": first_available_slots[0] if first_available_slots else None,
            "first_available_slots": first_available_slots
        }

    except EntityNotFoundError as e:
        logger.warning(f"Business not found: {payload.business_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error retrieving availability: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve availability")
    except Exception as e:
        logger.error(f"Unexpected error retrieving availability: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/availability/{business_id}", response_model=List[AvailabilitySlot])
async def get_contractor_availability(
    business_id: str = Path(..., description="Business ID"),
    start_date: date = Query(..., description="Start date for availability"),
    end_date: date = Query(..., description="End date for availability"),
    service_type: str = Query(None, description="Filter by service type"),
    duration_minutes: int = Query(None, ge=15, le=480, description="Required duration in minutes"),
    emergency_only: bool = Query(False, description="Show only emergency slots"),
    availability_service: AvailabilityService = Depends(get_availability_service)
):
    """
    Get contractor availability for a date range.
    
    Returns available time slots for booking appointments.
    
    Args:
        business_id: The unique identifier of the business
        start_date: Start date for availability search
        end_date: End date for availability search
        service_type: Optional service type filter
        duration_minutes: Required duration in minutes
        emergency_only: Show only emergency slots
        availability_service: Injected availability service
        
    Returns:
        List[AvailabilitySlot]: List of available time slots
        
    Raises:
        HTTPException: If business not found or retrieval fails
    """
    
    try:
        # Validate date range
        if start_date > end_date:
            raise ValidationError("Start date must be before or equal to end date")
        
        # Create search criteria
        search_criteria = AvailabilitySearchCriteria(
            start_date=start_date,
            end_date=end_date,
            service_type=service_type,
            duration_minutes=duration_minutes,
            emergency_only=emergency_only,
            available_only=True
        )
        
        # Get availability from service layer
        slot_dtos = await availability_service.get_availability_slots(business_id, search_criteria)
        
        # Convert DTOs to API response models
        slots = []
        for slot_dto in slot_dtos:
            slot_data = AvailabilitySlot(
                id=slot_dto.id,
                date=slot_dto.date,
                start_time=slot_dto.start_time.strftime("%H:%M"),
                end_time=slot_dto.end_time.strftime("%H:%M"),
                duration_minutes=slot_dto.duration_minutes,
                available=slot_dto.is_available,
                slot_type=slot_dto.slot_type,
                is_emergency=slot_dto.is_emergency,
                price_modifier=slot_dto.price_modifier
            )
            slots.append(slot_data)
        
        return slots
        
    except EntityNotFoundError as e:
        logger.warning(f"Business not found: {business_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error for business {business_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error retrieving availability for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve availability")
    except Exception as e:
        logger.error(f"Unexpected error retrieving availability for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/availability/{business_id}/check")
async def check_slot_availability(
    business_id: str = Path(..., description="Business ID"),
    slot_date: date = Query(..., description="Date of the slot"),
    start_time: str = Query(..., description="Start time (HH:MM format)"),
    duration_minutes: int = Query(..., ge=15, le=480, description="Duration in minutes"),
    availability_service: AvailabilityService = Depends(get_availability_service)
):
    """
    Check if a specific time slot is available.
    
    Returns boolean indicating availability status.
    
    Args:
        business_id: The unique identifier of the business
        slot_date: Date of the slot to check
        start_time: Start time in HH:MM format
        duration_minutes: Duration in minutes
        availability_service: Injected availability service
        
    Returns:
        Dict: Availability status and details
        
    Raises:
        HTTPException: If business not found or check fails
    """
    
    try:
        # Parse start time
        from datetime import time
        hour, minute = map(int, start_time.split(':'))
        start_time_obj = time(hour, minute)
        
        # Check availability
        is_available = await availability_service.check_slot_availability(
            business_id, slot_date, start_time_obj, duration_minutes
        )
        
        return {
            "available": is_available,
            "date": slot_date.isoformat(),
            "start_time": start_time,
            "duration_minutes": duration_minutes,
            "checked_at": date.today().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid time format: {start_time}")
    except EntityNotFoundError as e:
        logger.warning(f"Business not found: {business_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error for business {business_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error checking availability for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check availability")
    except Exception as e:
        logger.error(f"Unexpected error checking availability for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/business-hours/{business_id}")
async def get_business_hours(
    business_id: str = Path(..., description="Business ID"),
    availability_service: AvailabilityService = Depends(get_availability_service)
):
    """
    Get business hours for a contractor.
    
    Returns weekly business hours and availability settings.
    
    Args:
        business_id: The unique identifier of the business
        availability_service: Injected availability service
        
    Returns:
        List[Dict]: Business hours for each day of the week
        
    Raises:
        HTTPException: If business not found or retrieval fails
    """
    
    try:
        # Get business hours from service layer
        hours_dtos = await availability_service.get_business_hours(business_id)
        
        # Convert DTOs to API response format
        business_hours = []
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for hours_dto in hours_dtos:
            hours_data = {
                "day_of_week": hours_dto.day_of_week,
                "day_name": day_names[hours_dto.day_of_week],
                "is_open": hours_dto.is_open,
                "open_time": hours_dto.open_time.strftime("%H:%M") if hours_dto.open_time else None,
                "close_time": hours_dto.close_time.strftime("%H:%M") if hours_dto.close_time else None,
                "break_start": hours_dto.break_start.strftime("%H:%M") if hours_dto.break_start else None,
                "break_end": hours_dto.break_end.strftime("%H:%M") if hours_dto.break_end else None,
                "is_emergency_available": hours_dto.is_emergency_available
            }
            business_hours.append(hours_data)
        
        return business_hours
        
    except EntityNotFoundError as e:
        logger.warning(f"Business not found: {business_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error for business {business_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error retrieving business hours for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve business hours")
    except Exception as e:
        logger.error(f"Unexpected error retrieving business hours for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")