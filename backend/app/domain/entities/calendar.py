"""
Calendar Domain Entities

Calendar management entities for user scheduling, time off, and availability.
Handles calendar events, working hours templates, and time off requests.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, time, date
from typing import Optional, List
from enum import Enum
from decimal import Decimal

from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError


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


@dataclass
class CalendarEvent:
    """Calendar event entity for user scheduling."""
    id: uuid.UUID
    user_id: str
    business_id: uuid.UUID
    
    # Event details
    title: str
    
    # Time information (required fields first)
    start_datetime: datetime
    end_datetime: datetime
    
    # Optional event details
    description: Optional[str] = None
    event_type: CalendarEventType = CalendarEventType.WORK_SCHEDULE
    is_all_day: bool = False
    timezone: str = "UTC"
    
    # Recurrence
    recurrence_type: RecurrenceType = RecurrenceType.NONE
    recurrence_end_date: Optional[date] = None
    recurrence_count: Optional[int] = None
    recurrence_interval: int = 1  # Every N days/weeks/months
    recurrence_days_of_week: List[int] = field(default_factory=list)  # 0=Monday, 6=Sunday
    
    # Availability impact
    blocks_scheduling: bool = True
    allows_emergency_override: bool = False
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.utcnow)
    last_modified: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    def __post_init__(self):
        """Validate calendar event."""
        if self.end_datetime <= self.start_datetime:
            raise DomainValidationError("End time must be after start time")
        
        if self.recurrence_type != RecurrenceType.NONE:
            if self.recurrence_type == RecurrenceType.WEEKLY and not self.recurrence_days_of_week:
                raise DomainValidationError("Weekly recurrence requires days of week")
    
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


@dataclass
class TimeOffRequest:
    """Time off request entity."""
    id: uuid.UUID
    user_id: str
    business_id: uuid.UUID
    
    # Request details (required fields first)
    time_off_type: TimeOffType
    start_date: date
    end_date: date
    
    # Optional request details
    reason: Optional[str] = None
    notes: Optional[str] = None
    
    # Approval workflow
    status: str = "pending"  # pending, approved, denied, cancelled
    requested_by: str = ""
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    denial_reason: Optional[str] = None
    
    # Impact on scheduling
    affects_scheduling: bool = True
    emergency_contact_allowed: bool = False
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.utcnow)
    last_modified: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate time off request."""
        if self.end_date < self.start_date:
            raise DomainValidationError("End date must be after or equal to start date")
    
    def get_duration_days(self) -> int:
        """Get duration in days."""
        return (self.end_date - self.start_date).days + 1
    
    def is_approved(self) -> bool:
        """Check if request is approved."""
        return self.status == "approved"
    
    def overlaps_with_date(self, check_date: date) -> bool:
        """Check if time off overlaps with a specific date."""
        return self.start_date <= check_date <= self.end_date


@dataclass
class WorkingHoursTemplate:
    """Template for working hours patterns."""
    id: uuid.UUID
    name: str
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
    break_duration_minutes: int = 30
    lunch_start_time: Optional[time] = None
    lunch_duration_minutes: int = 60
    
    # Flexibility settings
    allows_flexible_start: bool = False
    flexible_start_window_minutes: int = 30
    allows_overtime: bool = False
    max_overtime_hours_per_day: Decimal = Decimal("2")
    
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


@dataclass
class CalendarPreferences:
    """User calendar and scheduling preferences."""
    user_id: str
    business_id: uuid.UUID
    
    # Time zone and locale
    timezone: str = "UTC"
    date_format: str = "YYYY-MM-DD"
    time_format: str = "24h"  # 12h or 24h
    week_start_day: int = 0  # 0=Monday, 1=Tuesday, etc.
    
    # Scheduling preferences
    preferred_working_hours_template_id: Optional[uuid.UUID] = None
    min_time_between_jobs_minutes: int = 30
    max_commute_time_minutes: int = 60
    allows_back_to_back_jobs: bool = False
    requires_prep_time_minutes: int = 15
    
    # Notification preferences
    job_reminder_minutes_before: List[int] = field(default_factory=lambda: [60, 15])
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
    travel_buffer_percentage: Decimal = Decimal("1.2")  # 20% buffer
    job_buffer_minutes: int = 15
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.utcnow)
    last_modified: datetime = field(default_factory=datetime.utcnow) 