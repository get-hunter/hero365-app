"""
Availability Domain Entities

User availability and scheduling entities for intelligent job scheduling.
Handles availability windows, workload capacity, and scheduling patterns.
"""

import uuid
import logging
from datetime import datetime, timedelta, time, date
from typing import Optional, List, Annotated
from enum import Enum
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, model_validator, BeforeValidator

from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError

# Configure logging
logger = logging.getLogger(__name__)


# Custom Pydantic validators for automatic string-to-enum conversion
def validate_availability_type(v) -> 'AvailabilityType':
    """Convert string to AvailabilityType enum."""
    if isinstance(v, str):
        return AvailabilityType(v)
    return v


class AvailabilityType(Enum):
    """Types of availability patterns."""
    REGULAR = "regular"  # Standard weekly pattern
    FLEXIBLE = "flexible"  # Variable availability
    ON_CALL = "on_call"  # Emergency availability
    PROJECT_BASED = "project_based"  # Specific project availability


class AvailabilityWindow(BaseModel):
    """Value object representing availability time windows."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    day_of_week: int = Field(ge=0, le=6)  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
    availability_type: Annotated[AvailabilityType, BeforeValidator(validate_availability_type)] = AvailabilityType.REGULAR
    max_hours_per_day: Optional[Decimal] = Field(default=None, gt=0)
    break_duration_minutes: int = Field(default=30, ge=0)
    
    @model_validator(mode='after')
    def validate_time_window(self):
        """Validate time window constraints."""
        if self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")
        return self
    
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


class WorkloadCapacity(BaseModel):
    """Value object representing user's workload capacity."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    max_concurrent_jobs: int = Field(default=3, gt=0)
    max_daily_hours: Decimal = Field(default=Decimal("8"), gt=0)
    max_weekly_hours: Decimal = Field(default=Decimal("40"), gt=0)
    preferred_job_types: List[str] = Field(default_factory=list)
    max_travel_distance_km: Decimal = Field(default=Decimal("50"), ge=0)
    overtime_willingness: bool = False
    emergency_availability: bool = False 