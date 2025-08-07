"""
Skills and Certifications Domain Entities

User skills, certifications, and competency management for job matching.
Handles skill levels, categories, certifications, and proficiency tracking.
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
def validate_skill_level(v) -> 'SkillLevel':
    """Convert string to SkillLevel enum."""
    if isinstance(v, str):
        return SkillLevel(v)
    return v

def validate_skill_category(v) -> 'SkillCategory':
    """Convert string to SkillCategory enum."""
    if isinstance(v, str):
        return SkillCategory(v)
    return v

def validate_certification_status(v) -> 'CertificationStatus':
    """Convert string to CertificationStatus enum."""
    if isinstance(v, str):
        return CertificationStatus(v)
    return v


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


class Skill(BaseModel):
    """Value object representing a user skill."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    skill_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    category: Annotated[SkillCategory, BeforeValidator(validate_skill_category)]
    level: Annotated[SkillLevel, BeforeValidator(validate_skill_level)]
    years_experience: Decimal = Field(ge=0)
    last_used: Optional[datetime] = None
    proficiency_score: Optional[Decimal] = Field(default=None, ge=0, le=100)  # 0-100 score
    certification_required: bool = False
    
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


class Certification(BaseModel):
    """Value object representing a certification."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    certification_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    issuing_authority: str = Field(min_length=1)
    issue_date: datetime
    expiry_date: Optional[datetime] = None
    status: Annotated[CertificationStatus, BeforeValidator(validate_certification_status)] = CertificationStatus.ACTIVE
    verification_number: Optional[str] = None
    renewal_required: bool = True
    
    @model_validator(mode='after')
    def validate_dates(self):
        """Validate certification dates."""
        if self.expiry_date and self.expiry_date <= self.issue_date:
            raise ValueError("Expiry date must be after issue date")
        return self
    
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