"""
Skills and Certifications Domain Entities

User skills, certifications, and competency management for job matching.
Handles skill levels, categories, certifications, and proficiency tracking.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, time, date
from typing import Optional, List
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