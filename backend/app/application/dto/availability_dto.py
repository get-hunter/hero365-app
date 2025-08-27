"""
Availability Data Transfer Objects

DTOs for availability-related data transfer between application layers.
"""

from typing import Optional, List
from datetime import date as Date, time as Time, datetime as DateTime
from pydantic import BaseModel, Field


class AvailabilitySlotDTO(BaseModel):
    """DTO for availability slot information."""
    
    id: str = Field(..., description="Slot ID")
    business_id: str = Field(..., description="Business ID")
    date: Date = Field(..., description="Slot date")
    start_time: Time = Field(..., description="Start time")
    end_time: Time = Field(..., description="End time")
    duration_minutes: int = Field(..., description="Duration in minutes")
    slot_type: str = Field("regular", description="Slot type (regular, emergency, maintenance)")
    is_available: bool = Field(True, description="Slot is available")
    is_emergency: bool = Field(False, description="Emergency slot")
    service_types: List[str] = Field(default_factory=list, description="Allowed service types")
    max_bookings: int = Field(1, description="Maximum concurrent bookings")
    current_bookings: int = Field(0, description="Current number of bookings")
    price_modifier: float = Field(1.0, description="Price modifier for this slot")
    notes: Optional[str] = Field(None, description="Internal notes")


class BusinessHoursDTO(BaseModel):
    """DTO for business hours information."""
    
    business_id: str = Field(..., description="Business ID")
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    is_open: bool = Field(True, description="Business is open on this day")
    open_time: Optional[Time] = Field(None, description="Opening time")
    close_time: Optional[Time] = Field(None, description="Closing time")
    break_start: Optional[Time] = Field(None, description="Break start time")
    break_end: Optional[Time] = Field(None, description="Break end time")
    is_emergency_available: bool = Field(False, description="Emergency services available")


class AvailabilitySearchCriteria(BaseModel):
    """DTO for availability search criteria."""
    
    start_date: Date = Field(..., description="Start date for search")
    end_date: Date = Field(..., description="End date for search")
    service_type: Optional[str] = Field(None, description="Filter by service type")
    duration_minutes: Optional[int] = Field(None, description="Required duration")
    emergency_only: bool = Field(False, description="Show only emergency slots")
    available_only: bool = Field(True, description="Show only available slots")


class CalendarEventDTO(BaseModel):
    """DTO for calendar event information."""
    
    id: str = Field(..., description="Event ID")
    business_id: str = Field(..., description="Business ID")
    title: str = Field(..., description="Event title")
    start_datetime: DateTime = Field(..., description="Event start datetime")
    end_datetime: DateTime = Field(..., description="Event end datetime")
    event_type: str = Field("booking", description="Event type (booking, block, maintenance)")
    status: str = Field("confirmed", description="Event status")
    customer_id: Optional[str] = Field(None, description="Customer ID if booking")
    service_id: Optional[str] = Field(None, description="Service ID if booking")
    notes: Optional[str] = Field(None, description="Event notes")
    is_recurring: bool = Field(False, description="Is recurring event")
    recurrence_pattern: Optional[str] = Field(None, description="Recurrence pattern")
