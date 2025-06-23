"""
User Capabilities Domain Entity

Represents user skills, availability, and capacity for intelligent job scheduling.
Handles skill matching, availability windows, and workload capacity management.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, time
from typing import Optional, List, Dict, Any
from enum import Enum
from decimal import Decimal

from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError


class SkillLevel(Enum):
    """Skill proficiency levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"


class SkillCategory(Enum):
    """Categories of skills for grouping."""
    TECHNICAL = "technical"
    MECHANICAL = "mechanical"
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    HVAC = "hvac"
    CARPENTRY = "carpentry"
    PAINTING = "painting"
    CLEANING = "cleaning"
    SECURITY = "security"
    ADMINISTRATIVE = "administrative"


class CertificationStatus(Enum):
    """Status of certifications."""
    ACTIVE = "active"
    EXPIRED = "expired"
    PENDING = "pending"
    SUSPENDED = "suspended"


class AvailabilityType(Enum):
    """Types of availability patterns."""
    REGULAR = "regular"  # Standard weekly pattern
    FLEXIBLE = "flexible"  # Variable availability
    ON_CALL = "on_call"  # Emergency availability
    PROJECT_BASED = "project_based"  # Specific project availability


@dataclass
class Skill:
    """Value object representing a user skill."""
    skill_id: str
    name: str
    category: SkillCategory
    level: SkillLevel
    years_experience: Decimal
    last_used: Optional[datetime] = None
    proficiency_score: Optional[Decimal] = None  # 0-100 score
    certification_required: bool = False
    
    def __post_init__(self):
        """Validate skill data."""
        if not self.name or not self.name.strip():
            raise DomainValidationError("Skill name is required")
        if self.years_experience < 0:
            raise DomainValidationError("Years of experience cannot be negative")
        if self.proficiency_score is not None and (self.proficiency_score < 0 or self.proficiency_score > 100):
            raise DomainValidationError("Proficiency score must be between 0 and 100")
    
    def is_expert_level(self) -> bool:
        """Check if skill is at expert level or above."""
        return self.level in [SkillLevel.EXPERT, SkillLevel.MASTER]
    
    def get_efficiency_multiplier(self) -> Decimal:
        """Get efficiency multiplier based on skill level."""
        multipliers = {
            SkillLevel.BEGINNER: Decimal("0.7"),
            SkillLevel.INTERMEDIATE: Decimal("0.85"),
            SkillLevel.ADVANCED: Decimal("1.0"),
            SkillLevel.EXPERT: Decimal("1.2"),
            SkillLevel.MASTER: Decimal("1.4")
        }
        return multipliers.get(self.level, Decimal("1.0"))


@dataclass
class Certification:
    """Value object representing a certification."""
    certification_id: str
    name: str
    issuing_authority: str
    issue_date: datetime
    expiry_date: Optional[datetime] = None
    status: CertificationStatus = CertificationStatus.ACTIVE
    verification_number: Optional[str] = None
    renewal_required: bool = True
    
    def __post_init__(self):
        """Validate certification data."""
        if not self.name or not self.name.strip():
            raise DomainValidationError("Certification name is required")
        if not self.issuing_authority or not self.issuing_authority.strip():
            raise DomainValidationError("Issuing authority is required")
        if self.expiry_date and self.expiry_date <= self.issue_date:
            raise DomainValidationError("Expiry date must be after issue date")
    
    def is_valid(self) -> bool:
        """Check if certification is currently valid."""
        if self.status != CertificationStatus.ACTIVE:
            return False
        if self.expiry_date and self.expiry_date < datetime.utcnow():
            return False
        return True
    
    def days_until_expiry(self) -> Optional[int]:
        """Get days until expiry."""
        if not self.expiry_date:
            return None
        return (self.expiry_date - datetime.utcnow()).days


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


@dataclass
class UserCapabilities:
    """
    User Capabilities entity representing skills, availability, and capacity.
    
    This entity manages user capabilities for intelligent job scheduling,
    including skill matching, availability windows, and workload management.
    """
    
    id: uuid.UUID
    business_id: uuid.UUID
    user_id: str
    
    # Skills and certifications
    skills: List[Skill] = field(default_factory=list)
    certifications: List[Certification] = field(default_factory=list)
    
    # Availability and capacity
    availability_windows: List[AvailabilityWindow] = field(default_factory=list)
    workload_capacity: WorkloadCapacity = field(default_factory=WorkloadCapacity)
    
    # Location and mobility
    home_base_address: Optional[str] = None
    home_base_latitude: Optional[float] = None
    home_base_longitude: Optional[float] = None
    vehicle_type: Optional[str] = None
    has_vehicle: bool = True
    
    # Scheduling preferences
    preferred_start_time: Optional[time] = None
    preferred_end_time: Optional[time] = None
    min_time_between_jobs_minutes: int = 30
    max_commute_time_minutes: int = 60
    
    # Performance metrics
    average_job_rating: Optional[Decimal] = None
    completion_rate: Optional[Decimal] = None
    punctuality_score: Optional[Decimal] = None
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.utcnow)
    last_modified: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    def __post_init__(self):
        """Validate user capabilities."""
        self._validate_capabilities()
    
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
    
    def add_skill(self, skill: Skill) -> None:
        """Add a skill to the user's capabilities."""
        # Check if skill already exists
        existing_skill = self.get_skill_by_id(skill.skill_id)
        if existing_skill:
            raise BusinessRuleViolationError(f"Skill {skill.skill_id} already exists")
        
        self.skills.append(skill)
        self.last_modified = datetime.utcnow()
    
    def update_skill(self, skill_id: str, level: Optional[SkillLevel] = None, 
                    years_experience: Optional[Decimal] = None,
                    proficiency_score: Optional[Decimal] = None) -> None:
        """Update an existing skill."""
        skill = self.get_skill_by_id(skill_id)
        if not skill:
            raise BusinessRuleViolationError(f"Skill {skill_id} not found")
        
        if level:
            skill.level = level
        if years_experience is not None:
            skill.years_experience = years_experience
        if proficiency_score is not None:
            skill.proficiency_score = proficiency_score
        
        skill.last_used = datetime.utcnow()
        self.last_modified = datetime.utcnow()
    
    def remove_skill(self, skill_id: str) -> None:
        """Remove a skill from the user's capabilities."""
        skill = self.get_skill_by_id(skill_id)
        if not skill:
            raise BusinessRuleViolationError(f"Skill {skill_id} not found")
        
        self.skills.remove(skill)
        self.last_modified = datetime.utcnow()
    
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
    
    def activate(self) -> None:
        """Activate user capabilities."""
        self.is_active = True
        self.last_modified = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate user capabilities."""
        self.is_active = False
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