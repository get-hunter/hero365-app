"""
Supabase User Capabilities Repository Implementation

Implementation of UserCapabilitiesRepository using Supabase.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date, time, timedelta
import uuid
import logging

from supabase import AsyncClient

from app.domain.repositories.user_capabilities_repository import UserCapabilitiesRepository
from app.domain.entities.user_capabilities import UserCapabilities
from app.domain.entities.calendar import (
    CalendarEvent, TimeOffRequest, WorkingHoursTemplate, CalendarPreferences
)
from app.domain.entities.skills import Skill, Certification
from app.domain.entities.availability import AvailabilityWindow, WorkloadCapacity
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, DomainValidationError

logger = logging.getLogger(__name__)


class SupabaseUserCapabilitiesRepository(UserCapabilitiesRepository):
    """Supabase implementation of UserCapabilitiesRepository."""
    
    def __init__(self, client: AsyncClient):
        self.client = client
    
    async def create(self, user_capabilities: UserCapabilities) -> UserCapabilities:
        """Create new user capabilities."""
        try:
            # Insert main user capabilities record
            capabilities_data = {
                "business_id": str(user_capabilities.business_id),
                "user_id": user_capabilities.user_id,
                "home_base_address": user_capabilities.home_base_address,
                "home_base_latitude": float(user_capabilities.home_base_latitude) if user_capabilities.home_base_latitude else None,
                "home_base_longitude": float(user_capabilities.home_base_longitude) if user_capabilities.home_base_longitude else None,
                "vehicle_type": user_capabilities.vehicle_type,
                "has_vehicle": user_capabilities.has_vehicle,
                "preferred_start_time": user_capabilities.preferred_start_time.isoformat() if user_capabilities.preferred_start_time else None,
                "preferred_end_time": user_capabilities.preferred_end_time.isoformat() if user_capabilities.preferred_end_time else None,
                "min_time_between_jobs_minutes": user_capabilities.min_time_between_jobs_minutes,
                "max_commute_time_minutes": user_capabilities.max_commute_time_minutes,
                "average_job_rating": float(user_capabilities.average_job_rating) if user_capabilities.average_job_rating else None,
                "completion_rate": float(user_capabilities.completion_rate) if user_capabilities.completion_rate else None,
                "punctuality_score": float(user_capabilities.punctuality_score) if user_capabilities.punctuality_score else None,
                "working_hours_template_id": str(user_capabilities.working_hours_template.id) if user_capabilities.working_hours_template else None,
                "is_active": user_capabilities.is_active
            }
            
            result = await self.client.table("user_capabilities").insert(capabilities_data).execute()
            if not result.data:
                raise DomainValidationError("Failed to create user capabilities")
            
            capabilities_id = uuid.UUID(result.data[0]["id"])
            user_capabilities.id = capabilities_id
            
            # Insert related entities
            await self._insert_skills(capabilities_id, user_capabilities.skills)
            await self._insert_certifications(capabilities_id, user_capabilities.certifications)
            await self._insert_availability_windows(capabilities_id, user_capabilities.availability_windows)
            if user_capabilities.workload_capacity:
                await self._insert_workload_capacity(capabilities_id, user_capabilities.workload_capacity)
            
            return user_capabilities
            
        except Exception as e:
            logger.error(f"Error creating user capabilities: {e}")
            raise DomainValidationError(f"Failed to create user capabilities: {e}")
    
    async def get_by_id(self, capabilities_id: uuid.UUID) -> Optional[UserCapabilities]:
        """Get user capabilities by ID."""
        try:
            result = await self.client.table("user_capabilities").select("*").eq("id", str(capabilities_id)).execute()
            if not result.data:
                return None
            
            return await self._build_user_capabilities_from_data(result.data[0])
            
        except Exception as e:
            logger.error(f"Error getting user capabilities by ID: {e}")
            raise
    
    async def get_by_user_id(self, business_id: uuid.UUID, user_id: str) -> Optional[UserCapabilities]:
        """Get user capabilities by user ID."""
        try:
            result = await self.client.table("user_capabilities").select("*").eq("business_id", str(business_id)).eq("user_id", user_id).execute()
            if not result.data:
                return None
            
            return await self._build_user_capabilities_from_data(result.data[0])
            
        except Exception as e:
            logger.error(f"Error getting user capabilities by user ID: {e}")
            raise
    
    async def get_by_business_id(self, business_id: uuid.UUID) -> List[UserCapabilities]:
        """Get all user capabilities for a business."""
        try:
            result = await self.client.table("user_capabilities").select("*").eq("business_id", str(business_id)).eq("is_active", True).execute()
            
            capabilities_list = []
            for data in result.data:
                capabilities = await self._build_user_capabilities_from_data(data)
                capabilities_list.append(capabilities)
            
            return capabilities_list
            
        except Exception as e:
            logger.error(f"Error getting user capabilities by business ID: {e}")
            raise
    
    async def update(self, user_capabilities: UserCapabilities) -> UserCapabilities:
        """Update user capabilities."""
        try:
            capabilities_data = {
                "home_base_address": user_capabilities.home_base_address,
                "home_base_latitude": float(user_capabilities.home_base_latitude) if user_capabilities.home_base_latitude else None,
                "home_base_longitude": float(user_capabilities.home_base_longitude) if user_capabilities.home_base_longitude else None,
                "vehicle_type": user_capabilities.vehicle_type,
                "has_vehicle": user_capabilities.has_vehicle,
                "preferred_start_time": user_capabilities.preferred_start_time.isoformat() if user_capabilities.preferred_start_time else None,
                "preferred_end_time": user_capabilities.preferred_end_time.isoformat() if user_capabilities.preferred_end_time else None,
                "min_time_between_jobs_minutes": user_capabilities.min_time_between_jobs_minutes,
                "max_commute_time_minutes": user_capabilities.max_commute_time_minutes,
                "average_job_rating": float(user_capabilities.average_job_rating) if user_capabilities.average_job_rating else None,
                "completion_rate": float(user_capabilities.completion_rate) if user_capabilities.completion_rate else None,
                "punctuality_score": float(user_capabilities.punctuality_score) if user_capabilities.punctuality_score else None,
                "working_hours_template_id": str(user_capabilities.working_hours_template.id) if user_capabilities.working_hours_template else None,
                "is_active": user_capabilities.is_active
            }
            
            result = await self.client.table("user_capabilities").update(capabilities_data).eq("id", str(user_capabilities.id)).execute()
            if not result.data:
                raise EntityNotFoundError("UserCapabilities", str(user_capabilities.id))
            
            # Update related entities
            await self._update_skills(user_capabilities.id, user_capabilities.skills)
            await self._update_certifications(user_capabilities.id, user_capabilities.certifications)
            await self._update_availability_windows(user_capabilities.id, user_capabilities.availability_windows)
            if user_capabilities.workload_capacity:
                await self._update_workload_capacity(user_capabilities.id, user_capabilities.workload_capacity)
            
            return user_capabilities
            
        except Exception as e:
            logger.error(f"Error updating user capabilities: {e}")
            raise
    
    async def delete(self, capabilities_id: uuid.UUID) -> bool:
        """Delete user capabilities."""
        try:
            result = await self.client.table("user_capabilities").delete().eq("id", str(capabilities_id)).execute()
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error deleting user capabilities: {e}")
            return False
    
    async def get_users_with_skills(self, business_id: uuid.UUID, required_skills: List[str]) -> List[UserCapabilities]:
        """Get users with specific skills."""
        try:
            # For now, get all users and filter in memory
            # TODO: Implement database function for better performance
            all_users = await self.get_by_business_id(business_id)
            matching_users = []
            
            for user in all_users:
                if all(user.has_skill(skill_id) for skill_id in required_skills):
                    matching_users.append(user)
            
            return matching_users
            
        except Exception as e:
            logger.error(f"Error getting users with skills: {e}")
            return []
    
    async def get_available_users_for_time_window(self, business_id: uuid.UUID, 
                                                 start_time: datetime, end_time: datetime) -> List[UserCapabilities]:
        """Get users available for a specific time window."""
        try:
            # For now, get all users and check availability in memory
            # TODO: Implement database function for better performance
            all_users = await self.get_by_business_id(business_id)
            available_users = []
            
            for user in all_users:
                if user.is_available_on_datetime(start_time):
                    available_users.append(user)
            
            return available_users
            
        except Exception as e:
            logger.error(f"Error getting available users: {e}")
            return []
    
    # Calendar management methods
    async def add_calendar_event(self, user_id: str, business_id: uuid.UUID, 
                               event: CalendarEvent) -> CalendarEvent:
        """Add a calendar event for a user."""
        try:
            event_data = {
                "user_id": user_id,
                "business_id": str(business_id),
                "title": event.title,
                "description": event.description,
                "event_type": event.event_type.value,
                "start_datetime": event.start_datetime.isoformat(),
                "end_datetime": event.end_datetime.isoformat(),
                "is_all_day": event.is_all_day,
                "timezone": event.timezone,
                "recurrence_type": event.recurrence_type.value,
                "recurrence_end_date": event.recurrence_end_date.isoformat() if event.recurrence_end_date else None,
                "recurrence_count": event.recurrence_count,
                "recurrence_interval": event.recurrence_interval,
                "recurrence_days_of_week": event.recurrence_days_of_week,
                "blocks_scheduling": event.blocks_scheduling,
                "allows_emergency_override": event.allows_emergency_override,
                "is_active": event.is_active
            }
            
            result = await self.client.table("calendar_events").insert(event_data).execute()
            if not result.data:
                raise DomainValidationError("Failed to create calendar event")
            
            event.id = uuid.UUID(result.data[0]["id"])
            return event
            
        except Exception as e:
            logger.error(f"Error adding calendar event: {e}")
            raise DomainValidationError(f"Failed to add calendar event: {e}")
    
    async def update_calendar_event(self, event_id: uuid.UUID, event: CalendarEvent) -> CalendarEvent:
        """Update a calendar event."""
        try:
            event_data = {
                "title": event.title,
                "description": event.description,
                "event_type": event.event_type.value,
                "start_datetime": event.start_datetime.isoformat(),
                "end_datetime": event.end_datetime.isoformat(),
                "is_all_day": event.is_all_day,
                "timezone": event.timezone,
                "recurrence_type": event.recurrence_type.value,
                "recurrence_end_date": event.recurrence_end_date.isoformat() if event.recurrence_end_date else None,
                "recurrence_count": event.recurrence_count,
                "recurrence_interval": event.recurrence_interval,
                "recurrence_days_of_week": event.recurrence_days_of_week,
                "blocks_scheduling": event.blocks_scheduling,
                "allows_emergency_override": event.allows_emergency_override,
                "is_active": event.is_active
            }
            
            result = await self.client.table("calendar_events").update(event_data).eq("id", str(event_id)).execute()
            if not result.data:
                raise EntityNotFoundError("CalendarEvent", str(event_id))
            
            return event
            
        except Exception as e:
            logger.error(f"Error updating calendar event: {e}")
            raise
    
    async def delete_calendar_event(self, event_id: uuid.UUID) -> bool:
        """Delete a calendar event."""
        try:
            result = await self.client.table("calendar_events").delete().eq("id", str(event_id)).execute()
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error deleting calendar event: {e}")
            return False
    
    async def get_calendar_events(self, user_id: str, business_id: uuid.UUID,
                                start_date: date, end_date: date) -> List[CalendarEvent]:
        """Get calendar events for a user within date range."""
        try:
            result = await self.client.table("calendar_events").select("*").eq("user_id", user_id).eq("business_id", str(business_id)).gte("start_datetime", start_date.isoformat()).lte("end_datetime", end_date.isoformat()).execute()
            
            events = []
            for event_data in result.data:
                events.append(self._build_calendar_event_from_data(event_data))
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting calendar events: {e}")
            return []
    
    async def get_recurring_events(self, user_id: str, business_id: uuid.UUID) -> List[CalendarEvent]:
        """Get all recurring events for a user."""
        try:
            result = await self.client.table("calendar_events").select("*").eq("user_id", user_id).eq("business_id", str(business_id)).neq("recurrence_type", "none").execute()
            
            events = []
            for event_data in result.data:
                events.append(self._build_calendar_event_from_data(event_data))
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting recurring events: {e}")
            return []
    
    # Time off management - implement remaining methods with similar patterns
    async def create_time_off_request(self, time_off: TimeOffRequest) -> TimeOffRequest:
        """Create a time off request."""
        # Implementation similar to calendar events
        pass
    
    async def update_time_off_request(self, time_off_id: uuid.UUID, time_off: TimeOffRequest) -> TimeOffRequest:
        """Update a time off request."""
        pass
    
    async def approve_time_off_request(self, time_off_id: uuid.UUID, approved_by: str) -> TimeOffRequest:
        """Approve a time off request."""
        pass
    
    async def deny_time_off_request(self, time_off_id: uuid.UUID, denied_by: str, reason: str) -> TimeOffRequest:
        """Deny a time off request."""
        pass
    
    async def get_time_off_requests(self, user_id: str, business_id: uuid.UUID,
                                  status: Optional[str] = None) -> List[TimeOffRequest]:
        """Get time off requests for a user."""
        pass
    
    async def get_pending_time_off_requests(self, business_id: uuid.UUID) -> List[TimeOffRequest]:
        """Get all pending time off requests for a business."""
        pass
    
    # Working hours templates - implement remaining methods
    async def create_working_hours_template(self, template: WorkingHoursTemplate) -> WorkingHoursTemplate:
        """Create a working hours template."""
        pass
    
    async def get_working_hours_template(self, template_id: uuid.UUID) -> Optional[WorkingHoursTemplate]:
        """Get a working hours template by ID."""
        pass
    
    async def get_business_working_hours_templates(self, business_id: uuid.UUID) -> List[WorkingHoursTemplate]:
        """Get all working hours templates for a business."""
        pass
    
    async def update_working_hours_template(self, template: WorkingHoursTemplate) -> WorkingHoursTemplate:
        """Update a working hours template."""
        pass
    
    async def delete_working_hours_template(self, template_id: uuid.UUID) -> bool:
        """Delete a working hours template."""
        pass
    
    # Calendar preferences
    async def update_calendar_preferences(self, user_id: str, business_id: uuid.UUID,
                                        preferences: CalendarPreferences) -> CalendarPreferences:
        """Update user calendar preferences."""
        pass
    
    async def get_calendar_preferences(self, user_id: str, business_id: uuid.UUID) -> Optional[CalendarPreferences]:
        """Get user calendar preferences."""
        pass
    
    # Availability queries
    async def check_user_availability(self, user_id: str, business_id: uuid.UUID,
                                    start_datetime: datetime, end_datetime: datetime) -> bool:
        """Check if user is available for a specific time period."""
        try:
            user_capabilities = await self.get_by_user_id(business_id, user_id)
            if not user_capabilities:
                return False
            
            return user_capabilities.is_available_on_datetime(start_datetime)
            
        except Exception as e:
            logger.error(f"Error checking user availability: {e}")
            return False
    
    async def get_user_available_slots(self, user_id: str, business_id: uuid.UUID,
                                     date: date, slot_duration_minutes: int = 60,
                                     slot_interval_minutes: int = 30) -> List[Dict[str, datetime]]:
        """Get available time slots for a user on a specific date."""
        try:
            user_capabilities = await self.get_by_user_id(business_id, user_id)
            if not user_capabilities:
                return []
            
            slots = user_capabilities.get_available_time_slots_for_date(
                date, slot_duration_minutes, slot_interval_minutes
            )
            
            return [{"start": start, "end": end} for start, end in slots]
            
        except Exception as e:
            logger.error(f"Error getting user available slots: {e}")
            return []
    
    async def get_team_availability_summary(self, business_id: uuid.UUID,
                                          start_date: date, end_date: date) -> Dict[str, Any]:
        """Get availability summary for all team members."""
        try:
            all_users = await self.get_by_business_id(business_id)
            
            summary = {
                "total_team_members": len(all_users),
                "active_members": len([u for u in all_users if u.is_active]),
                "availability_by_day": {},
                "skills_summary": {}
            }
            
            # Calculate availability by day
            current_date = start_date
            while current_date <= end_date:
                day_of_week = current_date.weekday()
                available_count = sum(1 for user in all_users if user.is_available_on_day(day_of_week))
                summary["availability_by_day"][current_date.isoformat()] = available_count
                current_date += timedelta(days=1)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting team availability summary: {e}")
            return {}
    
    # Helper methods for building domain objects from database data
    async def _build_user_capabilities_from_data(self, data: Dict) -> UserCapabilities:
        """Build UserCapabilities object from database data."""
        capabilities_id = uuid.UUID(data["id"])
        
        # Get related data
        skills = await self._get_skills(capabilities_id)
        certifications = await self._get_certifications(capabilities_id)
        availability_windows = await self._get_availability_windows(capabilities_id)
        workload_capacity = await self._get_workload_capacity(capabilities_id)
        working_hours_template = await self._get_working_hours_template(data.get("working_hours_template_id"))
        
        return UserCapabilities(
            id=capabilities_id,
            business_id=uuid.UUID(data["business_id"]),
            user_id=data["user_id"],
            home_base_address=data.get("home_base_address"),
            home_base_latitude=data.get("home_base_latitude"),
            home_base_longitude=data.get("home_base_longitude"),
            vehicle_type=data.get("vehicle_type"),
            has_vehicle=data.get("has_vehicle", True),
            preferred_start_time=datetime.fromisoformat(data["preferred_start_time"]).time() if data.get("preferred_start_time") else None,
            preferred_end_time=datetime.fromisoformat(data["preferred_end_time"]).time() if data.get("preferred_end_time") else None,
            min_time_between_jobs_minutes=data.get("min_time_between_jobs_minutes", 30),
            max_commute_time_minutes=data.get("max_commute_time_minutes", 60),
            average_job_rating=data.get("average_job_rating"),
            completion_rate=data.get("completion_rate"),
            punctuality_score=data.get("punctuality_score"),
            skills=skills,
            certifications=certifications,
            availability_windows=availability_windows,
            workload_capacity=workload_capacity,
            working_hours_template=working_hours_template,
            created_date=datetime.fromisoformat(data["created_date"]) if data.get("created_date") else None,
            last_modified=datetime.fromisoformat(data["last_modified"]) if data.get("last_modified") else None,
            is_active=data.get("is_active", True)
        )
    
    # Helper methods for related entities (implement basic versions)
    async def _get_skills(self, capabilities_id: uuid.UUID) -> List[Skill]:
        """Get skills for user capabilities."""
        # Basic implementation - return empty list for now
        return []
    
    async def _get_certifications(self, capabilities_id: uuid.UUID) -> List[Certification]:
        """Get certifications for user capabilities."""
        return []
    
    async def _get_availability_windows(self, capabilities_id: uuid.UUID) -> List[AvailabilityWindow]:
        """Get availability windows for user capabilities."""
        return []
    
    async def _get_workload_capacity(self, capabilities_id: uuid.UUID) -> WorkloadCapacity:
        """Get workload capacity for user capabilities."""
        return WorkloadCapacity()
    
    async def _get_working_hours_template(self, template_id: Optional[str]) -> Optional[WorkingHoursTemplate]:
        """Get working hours template by ID."""
        return None
    
    async def _insert_skills(self, capabilities_id: uuid.UUID, skills: List[Skill]):
        """Insert skills for user capabilities."""
        pass
    
    async def _insert_certifications(self, capabilities_id: uuid.UUID, certifications: List[Certification]):
        """Insert certifications for user capabilities."""
        pass
    
    async def _insert_availability_windows(self, capabilities_id: uuid.UUID, windows: List[AvailabilityWindow]):
        """Insert availability windows for user capabilities."""
        pass
    
    async def _insert_workload_capacity(self, capabilities_id: uuid.UUID, capacity: WorkloadCapacity):
        """Insert workload capacity for user capabilities."""
        pass
    
    async def _update_skills(self, capabilities_id: uuid.UUID, skills: List[Skill]):
        """Update skills for user capabilities."""
        pass
    
    async def _update_certifications(self, capabilities_id: uuid.UUID, certifications: List[Certification]):
        """Update certifications for user capabilities."""
        pass
    
    async def _update_availability_windows(self, capabilities_id: uuid.UUID, windows: List[AvailabilityWindow]):
        """Update availability windows for user capabilities."""
        pass
    
    async def _update_workload_capacity(self, capabilities_id: uuid.UUID, capacity: WorkloadCapacity):
        """Update workload capacity for user capabilities."""
        pass
    
    def _build_calendar_event_from_data(self, data: Dict) -> CalendarEvent:
        """Build CalendarEvent from database data."""
        # Basic implementation
        from app.domain.entities.calendar import CalendarEventType, RecurrenceType
        
        return CalendarEvent(
            id=uuid.UUID(data["id"]),
            title=data["title"],
            description=data.get("description"),
            event_type=CalendarEventType(data["event_type"]),
            start_datetime=datetime.fromisoformat(data["start_datetime"]),
            end_datetime=datetime.fromisoformat(data["end_datetime"]),
            is_all_day=data.get("is_all_day", False),
            timezone=data.get("timezone", "UTC"),
            recurrence_type=RecurrenceType(data.get("recurrence_type", "none")),
            blocks_scheduling=data.get("blocks_scheduling", True),
            allows_emergency_override=data.get("allows_emergency_override", False),
            is_active=data.get("is_active", True)
        ) 