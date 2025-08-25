"""
Booking System Domain Entities

Comprehensive Pydantic models for the booking system including:
- Technicians and Skills
- Services and Requirements  
- Availability and Scheduling
- Bookings and Customer Management
- Notifications and Events
"""

from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

# Type aliases for compatibility (simplified for now)
EmailStr = str  # Will add email validation in validators
IPvAnyAddress = str  # Will add IP validation in validators


# =====================================================
# ENUMS & CONSTANTS
# =====================================================

class ProficiencyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class TimeOffType(str, Enum):
    VACATION = "vacation"
    SICK = "sick"
    TRAINING = "training"
    LUNCH = "lunch"
    BREAK = "break"
    PERSONAL = "personal"


class TimeOffStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"


class BookingEventType(str, Enum):
    CREATED = "created"
    CONFIRMED = "confirmed"
    RESCHEDULED = "rescheduled"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    STATUS_CHANGED = "status_changed"
    UPDATED = "updated"
    DELETED = "deleted"


class ContactMethod(str, Enum):
    PHONE = "phone"
    EMAIL = "email"
    SMS = "sms"


class PriceType(str, Enum):
    FIXED = "fixed"
    HOURLY = "hourly"
    ESTIMATE = "estimate"


class BookingSource(str, Enum):
    WEBSITE = "website"
    PHONE = "phone"
    MOBILE_APP = "mobile_app"
    REFERRAL = "referral"
    WALK_IN = "walk_in"


# =====================================================
# TECHNICIANS & SKILLS
# =====================================================

class Skill(BaseModel):
    """Skill that technicians can possess"""
    id: Optional[UUID] = None
    business_id: UUID
    name: str = Field(..., max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    requires_certification: bool = False
    min_experience_years: int = 0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TechnicianSkill(BaseModel):
    """Association between technician and skill with proficiency"""
    id: Optional[UUID] = None
    technician_id: UUID
    skill_id: UUID
    proficiency_level: ProficiencyLevel = ProficiencyLevel.INTERMEDIATE
    certified_date: Optional[date] = None
    certification_expires: Optional[date] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @field_validator('certification_expires')
    @classmethod
    def validate_certification_expires(cls, v, info):
        if v and info.data.get('certified_date') and v <= info.data['certified_date']:
            raise ValueError('Certification expiry must be after certified date')
        return v


class Technician(BaseModel):
    """Technician with skills, availability, and service areas"""
    id: Optional[UUID] = None
    business_id: UUID
    
    # Basic Info
    employee_id: Optional[str] = Field(None, max_length=50)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    
    # Professional Info
    title: Optional[str] = Field(None, max_length=100)
    hire_date: Optional[date] = None
    hourly_rate: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    
    # Scheduling
    is_active: bool = True
    can_be_booked: bool = True
    default_buffer_minutes: int = Field(30, ge=0, le=480)  # Max 8 hours
    max_daily_hours: int = Field(8, ge=1, le=24)
    
    # Service Areas
    service_areas: List[str] = Field(default_factory=list)
    
    # Relationships
    skills: List[TechnicianSkill] = Field(default_factory=list)
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def skill_names(self) -> List[str]:
        return [skill.skill_id for skill in self.skills]  # Would need to resolve to names


# =====================================================
# SERVICES & REQUIREMENTS
# =====================================================

class BookableService(BaseModel):
    """Service that can be booked by customers"""
    id: Optional[UUID] = None
    business_id: UUID
    
    # Service Details
    name: str = Field(..., max_length=200)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    
    # Booking Configuration
    is_bookable: bool = True
    requires_site_visit: bool = True
    
    # Duration & Scheduling
    estimated_duration_minutes: int = Field(60, ge=15, le=1440)  # 15 min to 24 hours
    min_duration_minutes: Optional[int] = Field(None, ge=15)
    max_duration_minutes: Optional[int] = Field(None, le=1440)
    
    # Pricing
    base_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    price_type: PriceType = PriceType.FIXED
    
    # Requirements
    required_skills: List[UUID] = Field(default_factory=list)
    min_technicians: int = Field(1, ge=1, le=10)
    max_technicians: int = Field(1, ge=1, le=10)
    
    # Lead Time
    min_lead_time_hours: int = Field(2, ge=0, le=168)  # Max 1 week
    max_advance_days: int = Field(90, ge=1, le=365)  # Max 1 year
    
    # Availability
    available_days: List[int] = Field(default_factory=lambda: [1, 2, 3, 4, 5])  # Mon-Fri
    available_times: Dict[str, str] = Field(default_factory=lambda: {"start": "08:00", "end": "17:00"})
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @field_validator('available_days')
    @classmethod
    def validate_available_days(cls, v):
        if not all(1 <= day <= 7 for day in v):
            raise ValueError('Available days must be between 1 (Monday) and 7 (Sunday)')
        return sorted(list(set(v)))  # Remove duplicates and sort

    @field_validator('max_technicians')
    @classmethod
    def validate_max_technicians(cls, v, info):
        min_tech = info.data.get('min_technicians', 1)
        if v < min_tech:
            raise ValueError('max_technicians must be >= min_technicians')
        return v

    @field_validator('max_duration_minutes')
    @classmethod
    def validate_max_duration(cls, v, info):
        min_duration = info.data.get('min_duration_minutes')
        if v and min_duration and v < min_duration:
            raise ValueError('max_duration_minutes must be >= min_duration_minutes')
        return v


# =====================================================
# BUSINESS HOURS & AVAILABILITY
# =====================================================

class BusinessHours(BaseModel):
    """Business operating hours by location and day"""
    id: Optional[UUID] = None
    business_id: UUID
    location_id: Optional[UUID] = None
    
    # Day of week (1=Monday, 7=Sunday)
    day_of_week: int = Field(..., ge=1, le=7)
    
    # Hours
    is_open: bool = True
    open_time: Optional[time] = None
    close_time: Optional[time] = None
    
    # Breaks
    lunch_start: Optional[time] = None
    lunch_end: Optional[time] = None
    
    # Special handling
    is_emergency_only: bool = False
    
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @field_validator('close_time')
    @classmethod
    def validate_close_time(cls, v, info):
        open_time = info.data.get('open_time')
        if v and open_time and v <= open_time:
            raise ValueError('close_time must be after open_time')
        return v

    @field_validator('lunch_end')
    @classmethod
    def validate_lunch_end(cls, v, info):
        lunch_start = info.data.get('lunch_start')
        if v and lunch_start and v <= lunch_start:
            raise ValueError('lunch_end must be after lunch_start')
        return v


class TimeOff(BaseModel):
    """Technician time off and unavailability"""
    id: Optional[UUID] = None
    technician_id: UUID
    
    # Time Range
    start_at: datetime
    end_at: datetime
    
    # Type
    type: TimeOffType
    reason: Optional[str] = Field(None, max_length=200)
    
    # Status
    status: TimeOffStatus = TimeOffStatus.APPROVED
    is_recurring: bool = False
    recurrence_pattern: Optional[Dict[str, Any]] = None
    
    # Approval
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @field_validator('end_at')
    @classmethod
    def validate_end_at(cls, v, info):
        start_at = info.data.get('start_at')
        if start_at and v <= start_at:
            raise ValueError('end_at must be after start_at')
        return v


# =====================================================
# AVAILABILITY & TIME SLOTS
# =====================================================

class TimeSlot(BaseModel):
    """Available time slot for booking"""
    start_time: datetime
    end_time: datetime
    available_technicians: List[UUID] = Field(default_factory=list)
    capacity: int = Field(1, ge=1)
    booked_count: int = Field(0, ge=0)
    price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    
    @property
    def is_available(self) -> bool:
        return self.booked_count < self.capacity
    
    @property
    def remaining_capacity(self) -> int:
        return max(0, self.capacity - self.booked_count)


class AvailabilityRequest(BaseModel):
    """Request for available time slots"""
    business_id: UUID
    service_id: UUID
    
    # Date range
    start_date: date
    end_date: Optional[date] = None  # If None, use start_date
    
    # Time preferences
    preferred_times: Optional[Dict[str, str]] = None  # {"start": "09:00", "end": "17:00"}
    
    # Location (for travel time calculation)
    customer_address: Optional[str] = None
    customer_coordinates: Optional[tuple[float, float]] = None
    
    # Preferences
    preferred_technician_id: Optional[UUID] = None
    exclude_technician_ids: List[UUID] = Field(default_factory=list)

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        start_date = info.data.get('start_date')
        if v and start_date and v < start_date:
            raise ValueError('end_date must be >= start_date')
        return v


class AvailabilityResponse(BaseModel):
    """Response with available time slots"""
    business_id: UUID
    service_id: UUID
    service_name: str
    
    # Availability by date
    available_dates: Dict[str, List[TimeSlot]] = Field(default_factory=dict)  # date -> slots
    
    # Metadata
    total_slots: int = 0
    earliest_available: Optional[datetime] = None
    latest_available: Optional[datetime] = None
    
    # Service info
    estimated_duration_minutes: int
    base_price: Optional[Decimal] = None


# =====================================================
# BOOKINGS & CUSTOMER MANAGEMENT
# =====================================================

class CustomerContact(BaseModel):
    """Customer contact information and preferences"""
    id: Optional[UUID] = None
    business_id: UUID
    
    # Identity
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    
    # Personal Info
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    company_name: Optional[str] = Field(None, max_length=200)
    
    # Preferences
    preferred_contact_method: ContactMethod = ContactMethod.PHONE
    preferred_contact_time: Optional[Dict[str, str]] = None
    
    # Service History
    total_bookings: int = 0
    last_booking_at: Optional[datetime] = None
    customer_since: Optional[date] = None
    
    # Communication Consents
    sms_consent: bool = False
    sms_consent_date: Optional[datetime] = None
    sms_consent_ip: Optional[IPvAnyAddress] = None
    
    email_consent: bool = True
    email_consent_date: Optional[datetime] = None
    email_consent_ip: Optional[IPvAnyAddress] = None
    
    marketing_consent: bool = False
    marketing_consent_date: Optional[datetime] = None
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @model_validator(mode='after')
    def validate_contact_info(self):
        if not self.email and not self.phone:
            raise ValueError('Either email or phone must be provided')
        return self


class BookingRequest(BaseModel):
    """Customer booking request"""
    # Service Details
    business_id: UUID
    service_id: UUID
    
    # Scheduling
    requested_at: datetime
    
    # Customer Information
    customer_name: str = Field(..., max_length=200)
    customer_email: Optional[EmailStr] = None
    customer_phone: str = Field(..., max_length=20)
    
    # Service Address
    service_address: str = Field(..., max_length=500)
    service_city: Optional[str] = Field(None, max_length=100)
    service_state: Optional[str] = Field(None, max_length=50)
    service_zip: Optional[str] = Field(None, max_length=20)
    
    # Booking Details
    problem_description: Optional[str] = None
    special_instructions: Optional[str] = None
    access_instructions: Optional[str] = None
    
    # Communication Preferences
    preferred_contact_method: ContactMethod = ContactMethod.PHONE
    sms_consent: bool = False
    email_consent: bool = True
    
    # Metadata
    source: BookingSource = BookingSource.WEBSITE
    user_agent: Optional[str] = None
    ip_address: Optional[IPvAnyAddress] = None
    
    # Idempotency
    idempotency_key: Optional[str] = Field(None, max_length=100)

    @model_validator(mode='after')
    def validate_contact_info(self):
        if self.sms_consent and not self.customer_phone:
            raise ValueError('Phone number required for SMS consent')
        
        if not self.customer_email and not self.customer_phone:
            raise ValueError('Either email or phone must be provided')
        
        return self


class Booking(BaseModel):
    """Customer booking/appointment"""
    id: Optional[UUID] = None
    business_id: UUID
    booking_number: Optional[str] = None
    
    # Service Details
    service_id: UUID
    service_name: str = Field(..., max_length=200)
    estimated_duration_minutes: int
    
    # Scheduling
    requested_at: datetime
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Assignment
    primary_technician_id: Optional[UUID] = None
    additional_technicians: List[UUID] = Field(default_factory=list)
    
    # Customer Information
    customer_name: str = Field(..., max_length=200)
    customer_email: Optional[EmailStr] = None
    customer_phone: str = Field(..., max_length=20)
    
    # Service Address
    service_address: str
    service_city: Optional[str] = None
    service_state: Optional[str] = None
    service_zip: Optional[str] = None
    service_coordinates: Optional[tuple[float, float]] = None
    
    # Booking Details
    problem_description: Optional[str] = None
    special_instructions: Optional[str] = None
    access_instructions: Optional[str] = None
    
    # Pricing
    quoted_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    final_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    
    # Status Tracking
    status: BookingStatus = BookingStatus.PENDING
    cancellation_reason: Optional[str] = None
    cancelled_by: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    
    # Communication Preferences
    preferred_contact_method: ContactMethod = ContactMethod.PHONE
    sms_consent: bool = False
    email_consent: bool = True
    
    # Metadata
    source: BookingSource = BookingSource.WEBSITE
    user_agent: Optional[str] = None
    ip_address: Optional[IPvAnyAddress] = None
    idempotency_key: Optional[str] = None
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @property
    def is_confirmed(self) -> bool:
        return self.status == BookingStatus.CONFIRMED and self.scheduled_at is not None

    @property
    def can_be_cancelled(self) -> bool:
        return self.status in [BookingStatus.PENDING, BookingStatus.CONFIRMED]

    @property
    def can_be_rescheduled(self) -> bool:
        return self.status in [BookingStatus.PENDING, BookingStatus.CONFIRMED]


class BookingEvent(BaseModel):
    """Booking status change audit trail"""
    id: Optional[UUID] = None
    booking_id: UUID
    
    # Event Details
    event_type: BookingEventType
    old_status: Optional[BookingStatus] = None
    new_status: Optional[BookingStatus] = None
    
    # Changes
    changed_fields: Optional[Dict[str, Any]] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    
    # Context
    triggered_by: Optional[str] = None  # customer, technician, admin, system
    user_id: Optional[UUID] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    
    # Metadata
    ip_address: Optional[IPvAnyAddress] = None
    user_agent: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# =====================================================
# REQUEST/RESPONSE MODELS
# =====================================================

class BookingConfirmationRequest(BaseModel):
    """Request to confirm a booking"""
    booking_id: UUID
    scheduled_at: Optional[datetime] = None
    assigned_technician_id: Optional[UUID] = None
    notes: Optional[str] = None


class BookingRescheduleRequest(BaseModel):
    """Request to reschedule a booking"""
    booking_id: UUID
    new_scheduled_at: datetime
    reason: Optional[str] = None
    notify_customer: bool = True


class BookingCancellationRequest(BaseModel):
    """Request to cancel a booking"""
    booking_id: UUID
    reason: str = Field(..., max_length=500)
    cancelled_by: str = Field(..., max_length=50)  # customer, business, system
    refund_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    notify_customer: bool = True


class BookingResponse(BaseModel):
    """Response for booking operations"""
    booking: Booking
    message: str
    next_steps: List[str] = Field(default_factory=list)
    
    # Additional info
    estimated_arrival_time: Optional[datetime] = None
    technician_info: Optional[Dict[str, Any]] = None
    payment_info: Optional[Dict[str, Any]] = None


class BookingListResponse(BaseModel):
    """Response for booking list queries"""
    bookings: List[Booking]
    total_count: int
    page: int = 1
    page_size: int = 20
    has_next: bool = False
    has_previous: bool = False


# =====================================================
# CACHE & OPTIMIZATION
# =====================================================

class AvailabilityCache(BaseModel):
    """Pre-computed availability slots for performance"""
    id: Optional[UUID] = None
    business_id: UUID
    service_id: UUID
    
    # Time Slot
    date: date
    start_time: time
    end_time: time
    
    # Capacity
    available_slots: int = Field(1, ge=0)
    booked_slots: int = Field(0, ge=0)
    
    # Assignment
    available_technicians: List[UUID] = Field(default_factory=list)
    
    # Cache Management
    computed_at: Optional[datetime] = None
    expires_at: datetime

    class Config:
        from_attributes = True

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

    @property
    def remaining_capacity(self) -> int:
        return max(0, self.available_slots - self.booked_slots)


# =====================================================
# VALIDATION HELPERS
# =====================================================

def validate_business_hours(hours: List[BusinessHours]) -> bool:
    """Validate that business hours don't overlap for the same day"""
    days_seen = set()
    for hour in hours:
        if hour.day_of_week in days_seen:
            return False
        days_seen.add(hour.day_of_week)
    return True


def validate_time_slot_availability(
    slot: TimeSlot,
    existing_bookings: List[Booking],
    technician_availability: List[TimeOff]
) -> bool:
    """Validate that a time slot is actually available"""
    # Check for booking conflicts
    for booking in existing_bookings:
        if (booking.scheduled_at and 
            booking.status in [BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS]):
            booking_end = booking.scheduled_at + timedelta(minutes=booking.estimated_duration_minutes)
            if (slot.start_time < booking_end and slot.end_time > booking.scheduled_at):
                return False
    
    # Check technician availability
    for time_off in technician_availability:
        if (time_off.status == TimeOffStatus.APPROVED and
            slot.start_time < time_off.end_at and slot.end_time > time_off.start_at):
            return False
    
    return True
