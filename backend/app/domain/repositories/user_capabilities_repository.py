"""
User Capabilities Repository

Repository interface for user capabilities management.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import uuid

from ..entities.user_capabilities import (
    UserCapabilities, CalendarEvent, TimeOffRequest, 
    WorkingHoursTemplate, CalendarPreferences
)


class UserCapabilitiesRepository(ABC):
    """Repository interface for user capabilities."""
    
    @abstractmethod
    async def create(self, user_capabilities: UserCapabilities) -> UserCapabilities:
        """Create new user capabilities."""
        pass
    
    @abstractmethod
    async def get_by_id(self, capabilities_id: uuid.UUID) -> Optional[UserCapabilities]:
        """Get user capabilities by ID."""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, business_id: uuid.UUID, user_id: str) -> Optional[UserCapabilities]:
        """Get user capabilities by user ID."""
        pass
    
    @abstractmethod
    async def get_by_business_id(self, business_id: uuid.UUID) -> List[UserCapabilities]:
        """Get all user capabilities for a business."""
        pass
    
    @abstractmethod
    async def update(self, user_capabilities: UserCapabilities) -> UserCapabilities:
        """Update user capabilities."""
        pass
    
    @abstractmethod
    async def delete(self, capabilities_id: uuid.UUID) -> bool:
        """Delete user capabilities."""
        pass
    
    @abstractmethod
    async def get_users_with_skills(self, business_id: uuid.UUID, required_skills: List[str]) -> List[UserCapabilities]:
        """Get users with specific skills."""
        pass
    
    @abstractmethod
    async def get_available_users_for_time_window(self, business_id: uuid.UUID, 
                                                 start_time: datetime, end_time: datetime) -> List[UserCapabilities]:
        """Get users available for a specific time window."""
        pass
    
    # Calendar management methods
    @abstractmethod
    async def add_calendar_event(self, user_id: str, business_id: uuid.UUID, 
                               event: CalendarEvent) -> CalendarEvent:
        """Add a calendar event for a user."""
        pass
    
    @abstractmethod
    async def update_calendar_event(self, event_id: uuid.UUID, event: CalendarEvent) -> CalendarEvent:
        """Update a calendar event."""
        pass
    
    @abstractmethod
    async def delete_calendar_event(self, event_id: uuid.UUID) -> bool:
        """Delete a calendar event."""
        pass
    
    @abstractmethod
    async def get_calendar_events(self, user_id: str, business_id: uuid.UUID,
                                start_date: date, end_date: date) -> List[CalendarEvent]:
        """Get calendar events for a user within date range."""
        pass
    
    @abstractmethod
    async def get_recurring_events(self, user_id: str, business_id: uuid.UUID) -> List[CalendarEvent]:
        """Get all recurring events for a user."""
        pass
    
    # Time off management
    @abstractmethod
    async def create_time_off_request(self, time_off: TimeOffRequest) -> TimeOffRequest:
        """Create a time off request."""
        pass
    
    @abstractmethod
    async def update_time_off_request(self, time_off_id: uuid.UUID, time_off: TimeOffRequest) -> TimeOffRequest:
        """Update a time off request."""
        pass
    
    @abstractmethod
    async def approve_time_off_request(self, time_off_id: uuid.UUID, approved_by: str) -> TimeOffRequest:
        """Approve a time off request."""
        pass
    
    @abstractmethod
    async def deny_time_off_request(self, time_off_id: uuid.UUID, denied_by: str, reason: str) -> TimeOffRequest:
        """Deny a time off request."""
        pass
    
    @abstractmethod
    async def get_time_off_requests(self, user_id: str, business_id: uuid.UUID,
                                  status: Optional[str] = None) -> List[TimeOffRequest]:
        """Get time off requests for a user."""
        pass
    
    @abstractmethod
    async def get_pending_time_off_requests(self, business_id: uuid.UUID) -> List[TimeOffRequest]:
        """Get all pending time off requests for a business."""
        pass
    
    # Working hours templates
    @abstractmethod
    async def create_working_hours_template(self, template: WorkingHoursTemplate) -> WorkingHoursTemplate:
        """Create a working hours template."""
        pass
    
    @abstractmethod
    async def get_working_hours_template(self, template_id: uuid.UUID) -> Optional[WorkingHoursTemplate]:
        """Get a working hours template by ID."""
        pass
    
    @abstractmethod
    async def get_business_working_hours_templates(self, business_id: uuid.UUID) -> List[WorkingHoursTemplate]:
        """Get all working hours templates for a business."""
        pass
    
    @abstractmethod
    async def update_working_hours_template(self, template: WorkingHoursTemplate) -> WorkingHoursTemplate:
        """Update a working hours template."""
        pass
    
    @abstractmethod
    async def delete_working_hours_template(self, template_id: uuid.UUID) -> bool:
        """Delete a working hours template."""
        pass
    
    # Calendar preferences
    @abstractmethod
    async def update_calendar_preferences(self, user_id: str, business_id: uuid.UUID,
                                        preferences: CalendarPreferences) -> CalendarPreferences:
        """Update user calendar preferences."""
        pass
    
    @abstractmethod
    async def get_calendar_preferences(self, user_id: str, business_id: uuid.UUID) -> Optional[CalendarPreferences]:
        """Get user calendar preferences."""
        pass
    
    # Availability queries
    @abstractmethod
    async def check_user_availability(self, user_id: str, business_id: uuid.UUID,
                                    start_datetime: datetime, end_datetime: datetime) -> bool:
        """Check if user is available for a specific time period."""
        pass
    
    @abstractmethod
    async def get_user_available_slots(self, user_id: str, business_id: uuid.UUID,
                                     date: date, slot_duration_minutes: int = 60,
                                     slot_interval_minutes: int = 30) -> List[Dict[str, datetime]]:
        """Get available time slots for a user on a specific date."""
        pass
    
    @abstractmethod
    async def get_team_availability_summary(self, business_id: uuid.UUID,
                                          start_date: date, end_date: date) -> Dict[str, Any]:
        """Get availability summary for all team members."""
        pass 