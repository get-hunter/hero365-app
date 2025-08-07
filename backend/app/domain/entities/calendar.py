"""
Calendar Domain Entities

Calendar management entities for user scheduling, time off, and availability.
Handles calendar events, working hours templates, and time off requests.
"""

import uuid
import logging
from datetime import datetime, timedelta, time, date
from typing import Optional, List, Annotated
from enum import Enum
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, model_validator, UUID4, BeforeValidator

from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError

# Configure logging
logger = logging.getLogger(__name__)


# Custom Pydantic validators for automatic string-to-enum conversion
def validate_recurrence_type(v) -> 'RecurrenceType':
    """Convert string to RecurrenceType enum."""
    if isinstance(v, str):
        return RecurrenceType(v)
    return v

def validate_time_off_type(v) -> 'TimeOffType':
    """Convert string to TimeOffType enum."""
    if isinstance(v, str):
        return TimeOffType(v)
    return v

def validate_calendar_event_type(v) -> 'CalendarEventType':
    """Convert string to CalendarEventType enum."""
    if isinstance(v, str):
        return CalendarEventType(v)
    return v


class RecurrenceType(Enum):
    """Types of recurring schedule patterns."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class TimeOffType(Enum):
    """Types of time off."""
    VACATION = "vacation"
    SICK_LEAVE = "sick_leave"
    PERSONAL = "personal"
    HOLIDAY = "holiday"
    TRAINING = "training"
    EMERGENCY = "emergency"
    UNPAID = "unpaid"


class CalendarEventType(Enum):
    """Types of calendar events."""
    WORK_SCHEDULE = "work_schedule"
    TIME_OFF = "time_off"
    BREAK = "break"
    MEETING = "meeting"
    TRAINING = "training"
    PERSONAL = "personal"


class CalendarEvent(BaseModel):
    """Calendar event entity for user scheduling."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    id: UUID4 = Field(default_factory=uuid.uuid4)
    user_id: str = Field(min_length=1)
    business_id: UUID4
    
    # Event details
    title: str = Field(min_length=1)
    
    # Time information (required fields first)
    start_datetime: datetime
    end_datetime: datetime
    
    # Optional event details
    description: Optional[str] = None
    event_type: Annotated[CalendarEventType, BeforeValidator(validate_calendar_event_type)] = CalendarEventType.WORK_SCHEDULE
    is_all_day: bool = False
    timezone: str = Field(default="UTC", min_length=1)
    
    # Recurrence
    recurrence_type: Annotated[RecurrenceType, BeforeValidator(validate_recurrence_type)] = RecurrenceType.NONE
    recurrence_end_date: Optional[date] = None
    recurrence_count: Optional[int] = Field(default=None, gt=0)
    recurrence_interval: int = Field(default=1, gt=0)  # Every N days/weeks/months
    recurrence_days_of_week: List[int] = Field(default_factory=list)  # 0=Monday, 6=Sunday
    
    # Availability impact
    blocks_scheduling: bool = True
    allows_emergency_override: bool = False
    
    # Metadata
    created_date: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    @field_validator('recurrence_days_of_week')
    @classmethod
    def validate_days_of_week(cls, v):
        """Validate days of week are in valid range."""
        for day in v:
            if not (0 <= day <= 6):
                raise ValueError("Days of week must be between 0 (Monday) and 6 (Sunday)")
        return v
    
    @model_validator(mode='after')
    def validate_calendar_event_rules(self):
        """Validate calendar event business rules."""
        if self.end_datetime <= self.start_datetime:
            raise ValueError("End time must be after start time")
        
        if self.recurrence_type != RecurrenceType.NONE:
            if self.recurrence_type == RecurrenceType.WEEKLY and not self.recurrence_days_of_week:
                raise ValueError("Weekly recurrence requires days of week")
        
        return self
    
    def is_recurring(self) -> bool:
        """Check if this event has recurrence."""
        return self.recurrence_type != RecurrenceType.NONE
    
    def conflicts_with(self, other: 'CalendarEvent') -> bool:
        """Check if this event conflicts with another event."""
        if not self.blocks_scheduling or not other.blocks_scheduling:
            return False
        
        return not (self.end_datetime <= other.start_datetime or 
                   other.end_datetime <= self.start_datetime)
    
    def is_active_on_date(self, check_date: date) -> bool:
        """Check if this event is active on a specific date."""
        if not self.is_active:
            return False
        
        event_date = self.start_datetime.date()
        
        # Non-recurring events
        if not self.is_recurring():
            return event_date == check_date
        
        # Check if date is within recurrence range
        if check_date < event_date:
            return False
        
        if self.recurrence_end_date and check_date > self.recurrence_end_date:
            return False
        
        # Check recurrence pattern
        days_diff = (check_date - event_date).days
        
        if self.recurrence_type == RecurrenceType.DAILY:
            return days_diff % self.recurrence_interval == 0
        
        elif self.recurrence_type == RecurrenceType.WEEKLY:
            if check_date.weekday() in self.recurrence_days_of_week:
                weeks_diff = days_diff // 7
                return weeks_diff % self.recurrence_interval == 0
        
        elif self.recurrence_type == RecurrenceType.BIWEEKLY:
            if check_date.weekday() in self.recurrence_days_of_week:
                weeks_diff = days_diff // 7
                return weeks_diff % 2 == 0
        
        elif self.recurrence_type == RecurrenceType.MONTHLY:
            return (check_date.day == event_date.day and 
                   (check_date.year - event_date.year) * 12 + 
                   (check_date.month - event_date.month) % self.recurrence_interval == 0)
        
        return False


class TimeOffRequest(BaseModel):
    """Time off request entity."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    id: UUID4 = Field(default_factory=uuid.uuid4)
    user_id: str = Field(min_length=1)
    business_id: UUID4
    
    # Request details (required fields first)
    time_off_type: Annotated[TimeOffType, BeforeValidator(validate_time_off_type)]
    start_date: date
    end_date: date
    
    # Optional request details
    reason: Optional[str] = None
    notes: Optional[str] = None
    
    # Approval workflow
    status: str = Field(default="pending", min_length=1)  # pending, approved, denied, cancelled
    requested_by: str = Field(default="", min_length=0)
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    denial_reason: Optional[str] = None
    
    # Impact on scheduling
    affects_scheduling: bool = True
    emergency_contact_allowed: bool = False
    
    # Metadata
    created_date: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    
    @model_validator(mode='after')
    def validate_time_off_request_rules(self):
        """Validate time off request business rules."""
        if self.end_date < self.start_date:
            raise ValueError("End date must be after or equal to start date")
        return self
    
    def get_duration_days(self) -> int:
        """Get duration in days."""
        return (self.end_date - self.start_date).days + 1
    
    def is_approved(self) -> bool:
        """Check if request is approved."""
        return self.status == "approved"
    
    def overlaps_with_date(self, check_date: date) -> bool:
        """Check if time off overlaps with a specific date."""
        return self.start_date <= check_date <= self.end_date


class WorkingHoursTemplate(BaseModel):
    """Template for working hours patterns."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    id: UUID4 = Field(default_factory=uuid.uuid4)
    name: str = Field(min_length=1)
    description: Optional[str] = None
    
    # Weekly schedule (day 0 = Monday, 6 = Sunday)
    monday_start: Optional[time] = None
    monday_end: Optional[time] = None
    tuesday_start: Optional[time] = None
    tuesday_end: Optional[time] = None
    wednesday_start: Optional[time] = None
    wednesday_end: Optional[time] = None
    thursday_start: Optional[time] = None
    thursday_end: Optional[time] = None
    friday_start: Optional[time] = None
    friday_end: Optional[time] = None
    saturday_start: Optional[time] = None
    saturday_end: Optional[time] = None
    sunday_start: Optional[time] = None
    sunday_end: Optional[time] = None
    
    # Break configurations
    break_duration_minutes: int = Field(default=30, ge=0)
    lunch_start_time: Optional[time] = None
    lunch_duration_minutes: int = Field(default=60, ge=0)
    
    # Flexibility settings
    allows_flexible_start: bool = False
    flexible_start_window_minutes: int = Field(default=30, ge=0)
    allows_overtime: bool = False
    max_overtime_hours_per_day: Decimal = Field(default=Decimal("2"), ge=0)
    
    def get_working_hours_for_day(self, day_of_week: int) -> Optional[tuple[time, time]]:
        """Get start and end times for a specific day of week."""
        day_mapping = {
            0: (self.monday_start, self.monday_end),
            1: (self.tuesday_start, self.tuesday_end),
            2: (self.wednesday_start, self.wednesday_end),
            3: (self.thursday_start, self.thursday_end),
            4: (self.friday_start, self.friday_end),
            5: (self.saturday_start, self.saturday_end),
            6: (self.sunday_start, self.sunday_end),
        }
        
        start_time, end_time = day_mapping.get(day_of_week, (None, None))
        if start_time and end_time:
            return (start_time, end_time)
        return None
    
    def is_working_day(self, day_of_week: int) -> bool:
        """Check if a day is a working day."""
        return self.get_working_hours_for_day(day_of_week) is not None
    
    def get_total_weekly_hours(self) -> Decimal:
        """Calculate total weekly working hours."""
        total_hours = Decimal("0")
        for day in range(7):
            hours = self.get_working_hours_for_day(day)
            if hours:
                start_time, end_time = hours
                daily_hours = Decimal(str((datetime.combine(date.today(), end_time) - 
                                         datetime.combine(date.today(), start_time)).total_seconds() / 3600))
                # Subtract break time
                daily_hours -= Decimal(str(self.break_duration_minutes / 60))
                if self.lunch_start_time:
                    daily_hours -= Decimal(str(self.lunch_duration_minutes / 60))
                total_hours += daily_hours
        return total_hours


class CalendarPreferences(BaseModel):
    """User calendar and scheduling preferences."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    user_id: str = Field(min_length=1)
    business_id: UUID4
    
    # Time zone and locale
    timezone: str = Field(default="UTC", min_length=1)
    date_format: str = Field(default="YYYY-MM-DD", min_length=1)
    time_format: str = Field(default="24h", pattern="^(12h|24h)$")  # 12h or 24h
    week_start_day: int = Field(default=0, ge=0, le=6)  # 0=Monday, 1=Tuesday, etc.
    
    # Scheduling preferences
    preferred_working_hours_template_id: Optional[UUID4] = None
    min_time_between_jobs_minutes: int = Field(default=30, ge=0)
    max_commute_time_minutes: int = Field(default=60, ge=0)
    allows_back_to_back_jobs: bool = False
    requires_prep_time_minutes: int = Field(default=15, ge=0)
    
    # Notification preferences
    job_reminder_minutes_before: List[int] = Field(default_factory=lambda: [60, 15])
    schedule_change_notifications: bool = True
    new_job_notifications: bool = True
    cancellation_notifications: bool = True
    
    # Availability preferences
    auto_accept_jobs_in_hours: bool = False
    auto_decline_outside_hours: bool = True
    emergency_availability_outside_hours: bool = False
    weekend_availability: bool = False
    holiday_availability: bool = False
    
    # Buffer times
    travel_buffer_percentage: Decimal = Field(default=Decimal("1.2"), gt=0)  # 20% buffer
    job_buffer_minutes: int = Field(default=15, ge=0)
    
    # Metadata
    created_date: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow) 