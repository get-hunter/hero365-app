"""
User Capabilities Domain Entity

Represents user skills, availability, and capacity for intelligent job scheduling.
Handles skill matching, availability windows, and workload capacity management.
"""

import uuid
import logging
from datetime import datetime, timedelta, time, date
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, model_validator, UUID4

from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError

# Import from separate domain entity files
from .skills import Skill, Certification, SkillLevel, SkillCategory
from .availability import AvailabilityWindow, WorkloadCapacity, AvailabilityType
from .calendar import (
    CalendarEvent, TimeOffRequest, WorkingHoursTemplate, CalendarPreferences,
    RecurrenceType, TimeOffType, CalendarEventType
)

# Configure logging
logger = logging.getLogger(__name__)


class UserCapabilities(BaseModel):
    """
    Enhanced User Capabilities entity with comprehensive calendar management.
    
    This entity manages user capabilities for intelligent job scheduling,
    including skills, availability, calendar events, and scheduling preferences.
    """
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    id: UUID4 = Field(default_factory=uuid.uuid4)
    business_id: UUID4
    user_id: str = Field(min_length=1)
    
    # Skills and certifications
    skills: List[Skill] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    
    # Calendar and availability
    availability_windows: List[AvailabilityWindow] = Field(default_factory=list)
    calendar_events: List[CalendarEvent] = Field(default_factory=list)
    time_off_requests: List[TimeOffRequest] = Field(default_factory=list)
    working_hours_template: Optional[WorkingHoursTemplate] = None
    calendar_preferences: Optional[CalendarPreferences] = None
    
    # Capacity and workload
    workload_capacity: WorkloadCapacity = Field(default_factory=WorkloadCapacity)
    
    # Location and mobility
    home_base_address: Optional[str] = None
    home_base_latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    home_base_longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    vehicle_type: Optional[str] = None
    has_vehicle: bool = True
    
    # Legacy scheduling preferences (maintained for backward compatibility)
    preferred_start_time: Optional[time] = None
    preferred_end_time: Optional[time] = None
    min_time_between_jobs_minutes: int = Field(default=30, ge=0)
    max_commute_time_minutes: int = Field(default=60, ge=0)
    
    # Performance metrics
    average_job_rating: Optional[Decimal] = Field(default=None, ge=0, le=5)
    completion_rate: Optional[Decimal] = Field(default=None, ge=0, le=100)
    punctuality_score: Optional[Decimal] = Field(default=None, ge=0, le=100)
    
    # Metadata
    created_date: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    @model_validator(mode='after')
    def validate_capabilities_and_init_preferences(self):
        """Validate user capabilities and initialize calendar preferences if needed."""
        self._validate_capabilities()
        
        # Initialize calendar preferences if not provided (using model_copy to maintain immutability)
        if not self.calendar_preferences:
            calendar_prefs = CalendarPreferences(
                user_id=self.user_id,
                business_id=self.business_id
            )
            # Note: In Pydantic v2, we can't modify self in model_validator(mode='after')
            # This initialization should be done in model_validator(mode='before') if needed
            # For now, we'll just validate and let the caller set preferences if needed
        
        return self
    
    def _validate_capabilities(self) -> None:
        """Validate core capabilities business rules."""
        if not self.business_id:
            raise DomainValidationError("User capabilities must belong to a business")
        if not self.user_id:
            raise DomainValidationError("User capabilities must have a user ID")
        
        # Validate location data consistency
        if (self.home_base_latitude is None) != (self.home_base_longitude is None):
            raise DomainValidationError("Both latitude and longitude must be provided or both must be None")
        
        if self.min_time_between_jobs_minutes < 0:
            raise DomainValidationError("Min time between jobs cannot be negative")
        if self.max_commute_time_minutes <= 0:
            raise DomainValidationError("Max commute time must be positive")
    
    # Skills management methods
    def add_skill(self, skill: Skill) -> 'UserCapabilities':
        """Add a skill to the user's capabilities. Returns new UserCapabilities instance."""
        # Check if skill already exists
        existing_skill = self.get_skill_by_id(skill.skill_id)
        if existing_skill:
            raise BusinessRuleViolationError(f"Skill {skill.skill_id} already exists")
        
        new_skills = self.skills + [skill]
        return self.model_copy(update={
            'skills': new_skills,
            'last_modified': datetime.utcnow()
        })
    
    def update_skill(self, skill_id: str, level: Optional[SkillLevel] = None, 
                    years_experience: Optional[Decimal] = None,
                    proficiency_score: Optional[Decimal] = None) -> 'UserCapabilities':
        """Update an existing skill. Returns new UserCapabilities instance."""
        skill = self.get_skill_by_id(skill_id)
        if not skill:
            raise BusinessRuleViolationError(f"Skill {skill_id} not found")
        
        # Create updated skill
        update_data = {}
        if level:
            update_data['level'] = level
        if years_experience is not None:
            update_data['years_experience'] = years_experience
        if proficiency_score is not None:
            update_data['proficiency_score'] = proficiency_score
        
        update_data['last_used'] = datetime.utcnow()
        updated_skill = skill.model_copy(update=update_data)
        
        # Create new skills list with updated skill
        new_skills = [updated_skill if s.skill_id == skill_id else s for s in self.skills]
        
        return self.model_copy(update={
            'skills': new_skills,
            'last_modified': datetime.utcnow()
        })
    
    def remove_skill(self, skill_id: str) -> 'UserCapabilities':
        """Remove a skill from the user's capabilities. Returns new UserCapabilities instance."""
        skill = self.get_skill_by_id(skill_id)
        if not skill:
            raise BusinessRuleViolationError(f"Skill {skill_id} not found")
        
        new_skills = [s for s in self.skills if s.skill_id != skill_id]
        return self.model_copy(update={
            'skills': new_skills,
            'last_modified': datetime.utcnow()
        })
    
    def get_skill_by_id(self, skill_id: str) -> Optional[Skill]:
        """Get a skill by its ID."""
        for skill in self.skills:
            if skill.skill_id == skill_id:
                return skill
        return None
    
    def get_skills_by_category(self, category: SkillCategory) -> List[Skill]:
        """Get all skills in a specific category."""
        return [skill for skill in self.skills if skill.category == category]
    
    def has_skill(self, skill_id: str, min_level: Optional[SkillLevel] = None) -> bool:
        """Check if user has a specific skill at minimum level."""
        skill = self.get_skill_by_id(skill_id)
        if not skill:
            return False
        
        if min_level:
            level_hierarchy = {
                SkillLevel.BEGINNER: 1,
                SkillLevel.INTERMEDIATE: 2,
                SkillLevel.ADVANCED: 3,
                SkillLevel.EXPERT: 4,
                SkillLevel.MASTER: 5
            }
            return level_hierarchy.get(skill.level, 0) >= level_hierarchy.get(min_level, 0)
        
        return True
    
    # Certification management methods
    def add_certification(self, certification: Certification) -> None:
        """Add a certification."""
        # Check if certification already exists
        existing_cert = self.get_certification_by_id(certification.certification_id)
        if existing_cert:
            raise BusinessRuleViolationError(f"Certification {certification.certification_id} already exists")
        
        self.certifications.append(certification)
        self.last_modified = datetime.utcnow()
    
    def get_certification_by_id(self, certification_id: str) -> Optional[Certification]:
        """Get a certification by its ID."""
        for cert in self.certifications:
            if cert.certification_id == certification_id:
                return cert
        return None
    
    def get_valid_certifications(self) -> List[Certification]:
        """Get all valid (non-expired) certifications."""
        return [cert for cert in self.certifications if cert.is_valid()]
    
    def get_expiring_certifications(self, days_ahead: int = 30) -> List[Certification]:
        """Get certifications expiring within specified days."""
        expiring = []
        for cert in self.certifications:
            if cert.is_valid():
                days_until_expiry = cert.days_until_expiry()
                if days_until_expiry is not None and days_until_expiry <= days_ahead:
                    expiring.append(cert)
        return expiring
    
    # Availability management methods
    def add_availability_window(self, window: AvailabilityWindow) -> None:
        """Add an availability window."""
        # Check for overlaps with existing windows
        for existing_window in self.availability_windows:
            if window.overlaps_with(existing_window):
                raise BusinessRuleViolationError(
                    f"Availability window overlaps with existing window on day {window.day_of_week}"
                )
        
        self.availability_windows.append(window)
        self.last_modified = datetime.utcnow()
    
    def remove_availability_window(self, day_of_week: int, start_time: time) -> None:
        """Remove an availability window."""
        window_to_remove = None
        for window in self.availability_windows:
            if window.day_of_week == day_of_week and window.start_time == start_time:
                window_to_remove = window
                break
        
        if window_to_remove:
            self.availability_windows.remove(window_to_remove)
            self.last_modified = datetime.utcnow()
        else:
            raise BusinessRuleViolationError("Availability window not found")
    
    def is_available_on_day(self, day_of_week: int) -> bool:
        """Check if user is available on a specific day of week."""
        return any(window.day_of_week == day_of_week for window in self.availability_windows)
    
    def get_available_hours_on_day(self, day_of_week: int) -> Decimal:
        """Get total available hours on a specific day."""
        total_hours = Decimal("0")
        for window in self.availability_windows:
            if window.day_of_week == day_of_week:
                duration = window.get_available_duration()
                total_hours += Decimal(str(duration.total_seconds() / 3600))
        return total_hours
    
    # Job matching methods
    def matches_job_requirements(self, required_skills: List[str], 
                                required_certifications: Optional[List[str]] = None) -> bool:
        """Check if user matches job skill and certification requirements."""
        # Check required skills
        for required_skill in required_skills:
            if not self.has_skill(required_skill):
                return False
        
        # Check required certifications
        if required_certifications:
            valid_cert_ids = [cert.certification_id for cert in self.get_valid_certifications()]
            for required_cert in required_certifications:
                if required_cert not in valid_cert_ids:
                    return False
        
        return True
    
    def get_skill_match_score(self, required_skills: List[str]) -> Decimal:
        """Calculate skill match score (0-1) for given requirements."""
        if not required_skills:
            return Decimal("1.0")
        
        total_score = Decimal("0")
        for required_skill in required_skills:
            skill = self.get_skill_by_id(required_skill)
            if skill:
                # Base score for having the skill
                score = Decimal("0.5")
                
                # Bonus for skill level
                level_bonus = {
                    SkillLevel.BEGINNER: Decimal("0.1"),
                    SkillLevel.INTERMEDIATE: Decimal("0.2"),
                    SkillLevel.ADVANCED: Decimal("0.3"),
                    SkillLevel.EXPERT: Decimal("0.4"),
                    SkillLevel.MASTER: Decimal("0.5")
                }
                score += level_bonus.get(skill.level, Decimal("0"))
                
                total_score += score
        
        return total_score / Decimal(str(len(required_skills)))
    
    def get_efficiency_for_job(self, required_skills: List[str]) -> Decimal:
        """Calculate efficiency multiplier for a job based on skills."""
        if not required_skills:
            return Decimal("1.0")
        
        total_efficiency = Decimal("0")
        for required_skill in required_skills:
            skill = self.get_skill_by_id(required_skill)
            if skill:
                total_efficiency += skill.get_efficiency_multiplier()
            else:
                total_efficiency += Decimal("0.5")  # Penalty for missing skill
        
        return total_efficiency / Decimal(str(len(required_skills)))
    
    def can_handle_workload(self, additional_jobs: int = 1) -> bool:
        """Check if user can handle additional workload."""
        # This would need to be implemented with current workload data
        # For now, just check against max concurrent jobs
        return self.workload_capacity.max_concurrent_jobs >= additional_jobs
    
    # Performance tracking methods
    def update_performance_metrics(self, job_rating: Optional[Decimal] = None,
                                 completion_status: Optional[bool] = None,
                                 was_punctual: Optional[bool] = None) -> None:
        """Update performance metrics based on job completion."""
        if job_rating is not None:
            if self.average_job_rating is None:
                self.average_job_rating = job_rating
            else:
                # Simple moving average (could be improved with weighted average)
                self.average_job_rating = (self.average_job_rating + job_rating) / Decimal("2")
        
        # Update completion rate and punctuality score
        # Implementation would depend on how these metrics are tracked
        
        self.last_modified = datetime.utcnow()
    
    # Status management methods
    def activate(self) -> None:
        """Activate user capabilities."""
        self.is_active = True
        self.last_modified = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate user capabilities."""
        self.is_active = False
        self.last_modified = datetime.utcnow()
    
    # Calendar management methods
    def add_calendar_event(self, event: CalendarEvent) -> None:
        """Add a calendar event."""
        # Check for conflicts with existing events
        for existing_event in self.calendar_events:
            if event.conflicts_with(existing_event):
                raise BusinessRuleViolationError(
                    f"Calendar event conflicts with existing event: {existing_event.title}"
                )
        
        self.calendar_events.append(event)
        self.last_modified = datetime.utcnow()
    
    def remove_calendar_event(self, event_id: uuid.UUID) -> None:
        """Remove a calendar event."""
        event_to_remove = None
        for event in self.calendar_events:
            if event.id == event_id:
                event_to_remove = event
                break
        
        if event_to_remove:
            self.calendar_events.remove(event_to_remove)
            self.last_modified = datetime.utcnow()
        else:
            raise BusinessRuleViolationError("Calendar event not found")
    
    def add_time_off_request(self, time_off: TimeOffRequest) -> None:
        """Add a time off request."""
        # Check for overlapping time off
        for existing_time_off in self.time_off_requests:
            if existing_time_off.is_approved():
                for check_date in self._date_range(time_off.start_date, time_off.end_date):
                    if existing_time_off.overlaps_with_date(check_date):
                        raise BusinessRuleViolationError(
                            f"Time off request overlaps with existing approved time off"
                        )
        
        self.time_off_requests.append(time_off)
        self.last_modified = datetime.utcnow()
    
    def is_available_on_datetime(self, check_datetime: datetime) -> bool:
        """Check if user is available at a specific datetime."""
        check_date = check_datetime.date()
        check_time = check_datetime.time()
        day_of_week = check_datetime.weekday()
        
        # Check time off
        for time_off in self.time_off_requests:
            if time_off.is_approved() and time_off.overlaps_with_date(check_date):
                return False
        
        # Check calendar events that block scheduling
        for event in self.calendar_events:
            if (event.blocks_scheduling and event.is_active_on_date(check_date) and
                event.start_datetime.time() <= check_time <= event.end_datetime.time()):
                return False
        
        # Check working hours template
        if self.working_hours_template:
            working_hours = self.working_hours_template.get_working_hours_for_day(day_of_week)
            if not working_hours:
                return False
            start_time, end_time = working_hours
            if not (start_time <= check_time <= end_time):
                return False
        
        # Check availability windows (legacy support)
        if self.availability_windows:
            for window in self.availability_windows:
                if (window.day_of_week == day_of_week and
                    window.start_time <= check_time <= window.end_time):
                    return True
            return False
        
        return True
    
    def get_available_time_slots_for_date(self, check_date: date, 
                                        slot_duration_minutes: int = 60,
                                        slot_interval_minutes: int = 30) -> List[tuple[datetime, datetime]]:
        """Get available time slots for a specific date."""
        day_of_week = check_date.weekday()
        available_slots = []
        
        # Get working hours for the day
        working_hours = None
        if self.working_hours_template:
            working_hours = self.working_hours_template.get_working_hours_for_day(day_of_week)
        
        if not working_hours:
            # Fall back to availability windows
            for window in self.availability_windows:
                if window.day_of_week == day_of_week:
                    working_hours = (window.start_time, window.end_time)
                    break
        
        if not working_hours:
            return []
        
        start_time, end_time = working_hours
        
        # Generate potential slots
        current_time = datetime.combine(check_date, start_time)
        end_datetime = datetime.combine(check_date, end_time)
        slot_duration = timedelta(minutes=slot_duration_minutes)
        slot_interval = timedelta(minutes=slot_interval_minutes)
        
        while current_time + slot_duration <= end_datetime:
            slot_end = current_time + slot_duration
            
            # Check if this slot is available
            if self._is_slot_available(current_time, slot_end):
                available_slots.append((current_time, slot_end))
            
            current_time += slot_interval
        
        return available_slots
    
    def _is_slot_available(self, start_datetime: datetime, end_datetime: datetime) -> bool:
        """Check if a specific time slot is available."""
        # Check time off
        for time_off in self.time_off_requests:
            if time_off.is_approved():
                for check_date in self._date_range(start_datetime.date(), end_datetime.date()):
                    if time_off.overlaps_with_date(check_date):
                        return False
        
        # Check calendar events
        for event in self.calendar_events:
            if event.blocks_scheduling and event.is_active_on_date(start_datetime.date()):
                event_start = datetime.combine(start_datetime.date(), event.start_datetime.time())
                event_end = datetime.combine(start_datetime.date(), event.end_datetime.time())
                
                # Check for overlap
                if not (end_datetime <= event_start or start_datetime >= event_end):
                    return False
        
        return True
    
    def _date_range(self, start_date: date, end_date: date):
        """Generate date range."""
        current_date = start_date
        while current_date <= end_date:
            yield current_date
            current_date += timedelta(days=1)
    
    def set_working_hours_template(self, template: WorkingHoursTemplate) -> None:
        """Set working hours template."""
        self.working_hours_template = template
        self.last_modified = datetime.utcnow()
    
    def update_calendar_preferences(self, preferences: CalendarPreferences) -> None:
        """Update calendar preferences."""
        self.calendar_preferences = preferences
        self.last_modified = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": str(self.business_id),
            "user_id": self.user_id,
            "skills": [
                {
                    "skill_id": skill.skill_id,
                    "name": skill.name,
                    "category": skill.category.value,
                    "level": skill.level.value,
                    "years_experience": float(skill.years_experience),
                    "proficiency_score": float(skill.proficiency_score) if skill.proficiency_score else None
                }
                for skill in self.skills
            ],
            "certifications": [
                {
                    "certification_id": cert.certification_id,
                    "name": cert.name,
                    "status": cert.status.value,
                    "is_valid": cert.is_valid()
                }
                for cert in self.certifications
            ],
            "availability_summary": {
                "total_windows": len(self.availability_windows),
                "days_available": len(set(window.day_of_week for window in self.availability_windows))
            },
            "workload_capacity": {
                "max_concurrent_jobs": self.workload_capacity.max_concurrent_jobs,
                "max_daily_hours": float(self.workload_capacity.max_daily_hours),
                "max_travel_distance_km": float(self.workload_capacity.max_travel_distance_km)
            },
            "performance_metrics": {
                "average_job_rating": float(self.average_job_rating) if self.average_job_rating else None,
                "completion_rate": float(self.completion_rate) if self.completion_rate else None,
                "punctuality_score": float(self.punctuality_score) if self.punctuality_score else None
            },
            "is_active": self.is_active,
            "created_date": self.created_date.isoformat(),
            "last_modified": self.last_modified.isoformat()
        } 