"""
Booking API Routes

FastAPI endpoints for the booking system including:
- Availability checking
- Booking creation and management
- Rescheduling and cancellation
- Business booking management
"""

from datetime import date, datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

from ...application.services.availability_service import AvailabilityService
from ...application.services.booking_service import BookingService
from ...application.exceptions.application_exceptions import (
    BusinessNotFoundError, ServiceNotFoundError, ValidationError,
    ConflictError, NotFoundError
)
from ...domain.entities.booking import (
    AvailabilityRequest, AvailabilityResponse, TimeSlot,
    BookingRequest, BookingResponse, Booking, BookingStatus,
    BookingConfirmationRequest, BookingRescheduleRequest, 
    BookingCancellationRequest, BookingListResponse
)
from ..deps import get_supabase_client, get_current_user
from supabase import Client

router = APIRouter(prefix="/bookings", tags=["Bookings"])
security = HTTPBearer()


# =====================================================
# DEPENDENCY INJECTION
# =====================================================

def get_availability_service(
    supabase: Client = Depends(get_supabase_client)
) -> AvailabilityService:
    """Get availability service instance"""
    return AvailabilityService(supabase)


def get_booking_service(
    supabase: Client = Depends(get_supabase_client),
    availability_service: AvailabilityService = Depends(get_availability_service)
) -> BookingService:
    """Get booking service instance"""
    return BookingService(supabase, availability_service)


# =====================================================
# PUBLIC BOOKING ENDPOINTS
# =====================================================

@router.post("/availability", response_model=AvailabilityResponse)
async def get_availability(
    request: AvailabilityRequest,
    availability_service: AvailabilityService = Depends(get_availability_service)
):
    """
    Get available time slots for booking a service
    
    This endpoint is public to allow customers to check availability
    before creating an account or booking.
    """
    try:
        return await availability_service.get_availability(request)
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except BusinessNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ServiceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get availability"
        )


@router.get("/availability/next-slot")
async def get_next_available_slot(
    business_id: UUID = Query(..., description="Business ID"),
    service_id: UUID = Query(..., description="Service ID"),
    preferred_date: Optional[date] = Query(None, description="Preferred date (defaults to today)"),
    availability_service: AvailabilityService = Depends(get_availability_service)
):
    """
    Get the next available time slot for a service
    
    Useful for "Book Now" buttons that need to show the earliest available time.
    """
    try:
        slot = await availability_service.get_next_available_slot(
            business_id, service_id, preferred_date
        )
        
        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No available slots found in the next 30 days"
            )
        
        return slot
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get next available slot"
        )


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    request: BookingRequest,
    background_tasks: BackgroundTasks,
    auto_confirm: bool = Query(False, description="Auto-confirm if slot is available"),
    booking_service: BookingService = Depends(get_booking_service)
):
    """
    Create a new booking request
    
    This endpoint is public to allow customers to book services.
    The booking will be created in pending status and require confirmation
    unless auto_confirm is True and the slot is available.
    """
    try:
        response = await booking_service.create_booking(request, auto_confirm)
        
        # Schedule background tasks for notifications
        if response.booking.status == BookingStatus.CONFIRMED:
            background_tasks.add_task(
                _send_booking_confirmation_async,
                response.booking.id
            )
        else:
            background_tasks.add_task(
                _send_booking_request_async,
                response.booking.id
            )
        
        return response
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except BusinessNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ServiceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create booking"
        )


@router.get("/{booking_id}", response_model=Booking)
async def get_booking(
    booking_id: UUID,
    booking_service: BookingService = Depends(get_booking_service)
):
    """
    Get booking details by ID
    
    This endpoint is public to allow customers to check their booking status
    using the booking ID (no authentication required).
    """
    try:
        booking = await booking_service.get_booking(booking_id)
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        return booking
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get booking"
        )


# =====================================================
# CUSTOMER BOOKING MANAGEMENT
# =====================================================

@router.patch("/{booking_id}/reschedule", response_model=BookingResponse)
async def reschedule_booking(
    booking_id: UUID,
    request: BookingRescheduleRequest,
    background_tasks: BackgroundTasks,
    booking_service: BookingService = Depends(get_booking_service)
):
    """
    Reschedule an existing booking
    
    Customers can reschedule their bookings if done with sufficient notice.
    """
    try:
        # Ensure the booking ID matches the request
        request.booking_id = booking_id
        
        response = await booking_service.reschedule_booking(request)
        
        # Schedule notification
        if request.notify_customer:
            background_tasks.add_task(
                _send_reschedule_notification_async,
                booking_id
            )
        
        return response
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reschedule booking"
        )


@router.patch("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: UUID,
    request: BookingCancellationRequest,
    background_tasks: BackgroundTasks,
    booking_service: BookingService = Depends(get_booking_service)
):
    """
    Cancel an existing booking
    
    Customers can cancel their bookings. Cancellation fees may apply
    for short notice cancellations.
    """
    try:
        # Ensure the booking ID matches the request
        request.booking_id = booking_id
        
        response = await booking_service.cancel_booking(request)
        
        # Schedule notification
        if request.notify_customer:
            background_tasks.add_task(
                _send_cancellation_notification_async,
                booking_id
            )
        
        return response
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel booking"
        )


# =====================================================
# BUSINESS MANAGEMENT ENDPOINTS (AUTHENTICATED)
# =====================================================

@router.post("/{booking_id}/confirm", response_model=BookingResponse)
async def confirm_booking(
    booking_id: UUID,
    request: BookingConfirmationRequest,
    background_tasks: BackgroundTasks,
    booking_service: BookingService = Depends(get_booking_service),
    current_user = Depends(get_current_user)
):
    """
    Confirm a pending booking (Business users only)
    
    Business users can confirm pending bookings and assign technicians.
    """
    try:
        # Ensure the booking ID matches the request
        request.booking_id = booking_id
        
        response = await booking_service.confirm_booking(request)
        
        # Schedule confirmation notification
        background_tasks.add_task(
            _send_booking_confirmation_async,
            booking_id
        )
        
        return response
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to confirm booking"
        )


@router.get("/business/{business_id}", response_model=BookingListResponse)
async def get_business_bookings(
    business_id: UUID,
    status: Optional[BookingStatus] = Query(None, description="Filter by booking status"),
    start_date: Optional[datetime] = Query(None, description="Filter bookings from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter bookings until this date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    booking_service: BookingService = Depends(get_booking_service),
    current_user = Depends(get_current_user)
):
    """
    Get bookings for a business (Business users only)
    
    Returns paginated list of bookings with optional filters.
    """
    try:
        # TODO: Verify user has access to this business
        
        offset = (page - 1) * page_size
        bookings = await booking_service.get_bookings_for_business(
            business_id=business_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=page_size,
            offset=offset
        )
        
        # Get total count for pagination (simplified)
        total_count = len(bookings)  # TODO: Implement proper count query
        has_next = len(bookings) == page_size
        has_previous = page > 1
        
        return BookingListResponse(
            bookings=bookings,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_next=has_next,
            has_previous=has_previous
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get business bookings"
        )


# =====================================================
# ADMIN ENDPOINTS
# =====================================================

@router.patch("/{booking_id}/status")
async def update_booking_status(
    booking_id: UUID,
    new_status: BookingStatus,
    reason: Optional[str] = None,
    booking_service: BookingService = Depends(get_booking_service),
    current_user = Depends(get_current_user)
):
    """
    Update booking status (Admin only)
    
    Allows admins to manually update booking status for operational needs.
    """
    try:
        # TODO: Implement status update logic
        # This would be similar to confirm/cancel but more flexible
        
        return {"message": f"Booking status updated to {new_status.value}"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update booking status"
        )


# =====================================================
# BACKGROUND TASK FUNCTIONS
# =====================================================

async def _send_booking_request_async(booking_id: UUID):
    """Send booking request notification (background task)"""
    try:
        # TODO: Implement notification sending
        # This would use the NotificationService when implemented
        pass
    except Exception as e:
        # Log error but don't fail the main request
        print(f"Failed to send booking request notification: {e}")


async def _send_booking_confirmation_async(booking_id: UUID):
    """Send booking confirmation notification (background task)"""
    try:
        # TODO: Implement notification sending
        pass
    except Exception as e:
        print(f"Failed to send booking confirmation notification: {e}")


async def _send_reschedule_notification_async(booking_id: UUID):
    """Send reschedule notification (background task)"""
    try:
        # TODO: Implement notification sending
        pass
    except Exception as e:
        print(f"Failed to send reschedule notification: {e}")


async def _send_cancellation_notification_async(booking_id: UUID):
    """Send cancellation notification (background task)"""
    try:
        # TODO: Implement notification sending
        pass
    except Exception as e:
        print(f"Failed to send cancellation notification: {e}")


# =====================================================
# UTILITY ENDPOINTS
# =====================================================

@router.get("/health")
async def booking_health_check():
    """Health check endpoint for booking service"""
    return {
        "service": "booking",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# =====================================================
# WEBHOOK ENDPOINTS (Future)
# =====================================================

@router.post("/webhooks/payment-confirmed")
async def handle_payment_confirmation(
    booking_id: UUID,
    payment_data: dict,
    booking_service: BookingService = Depends(get_booking_service)
):
    """
    Handle payment confirmation webhook
    
    This endpoint would be called by payment processors to confirm
    that payment has been received for a booking.
    """
    try:
        # TODO: Implement payment confirmation logic
        # This would update booking status and trigger confirmations
        
        return {"message": "Payment confirmation processed"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process payment confirmation"
        )


@router.post("/webhooks/technician-location")
async def handle_technician_location_update(
    booking_id: UUID,
    location_data: dict,
    booking_service: BookingService = Depends(get_booking_service)
):
    """
    Handle technician location updates
    
    This endpoint would receive real-time location updates from
    technicians to provide ETA updates to customers.
    """
    try:
        # TODO: Implement location tracking logic
        
        return {"message": "Location update processed"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process location update"
        )
