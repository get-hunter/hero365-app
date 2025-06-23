"""
Availability Domain Entities

User availability and scheduling entities for intelligent job scheduling.
Handles availability windows, workload capacity, and scheduling patterns.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, time, date
from typing import Optional, List
from enum import Enum
from decimal import Decimal

from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError


class AvailabilityType(Enum):
    """Types of availability patterns."""
    REGULAR = "regular"  # Standard weekly pattern
    FLEXIBLE = "flexible"  # Variable availability
    ON_CALL = "on_call"  # Emergency availability
    PROJECT_BASED = "project_based"  # Specific project availability


@dataclass
class AvailabilityWindow:
    """Value object representing availability time windows."""
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
    availability_type: AvailabilityType = AvailabilityType.REGULAR
    max_hours_per_day: Optional[Decimal] = None
    break_duration_minutes: int = 30
    
    def __post_init__(self):
        """Validate availability window."""
        if not 0 <= self.day_of_week <= 6:
            raise DomainValidationError("Day of week must be between 0 and 6")
        if self.end_time <= self.start_time:
            raise DomainValidationError("End time must be after start time")
        if self.max_hours_per_day is not None and self.max_hours_per_day <= 0:
            raise DomainValidationError("Max hours per day must be positive")
    
    def get_available_duration(self) -> timedelta:
        """Get total available duration for this window."""
        start_dt = datetime.combine(datetime.today(), self.start_time)
        end_dt = datetime.combine(datetime.today(), self.end_time)
        if end_dt < start_dt:  # Handle overnight shifts
            end_dt += timedelta(days=1)
        
        total_duration = end_dt - start_dt
        break_duration = timedelta(minutes=self.break_duration_minutes)
        
        return total_duration - break_duration
    
    def overlaps_with(self, other: 'AvailabilityWindow') -> bool:
        """Check if this window overlaps with another on the same day."""
        if self.day_of_week != other.day_of_week:
            return False
        
        return not (self.end_time <= other.start_time or other.end_time <= self.start_time)


@dataclass
class WorkloadCapacity:
    """Value object representing user's workload capacity."""
    max_concurrent_jobs: int = 3
    max_daily_hours: Decimal = Decimal("8")
    max_weekly_hours: Decimal = Decimal("40")
    preferred_job_types: List[str] = field(default_factory=list)
    max_travel_distance_km: Decimal = Decimal("50")
    overtime_willingness: bool = False
    emergency_availability: bool = False
    
    def __post_init__(self):
        """Validate capacity settings."""
        if self.max_concurrent_jobs <= 0:
            raise DomainValidationError("Max concurrent jobs must be positive")
        if self.max_daily_hours <= 0:
            raise DomainValidationError("Max daily hours must be positive")
        if self.max_weekly_hours <= 0:
            raise DomainValidationError("Max weekly hours must be positive")
        if self.max_travel_distance_km < 0:
            raise DomainValidationError("Max travel distance cannot be negative") 