"""
Business Invitation Domain Entity

Represents an invitation for a user to join a business team.
"""

import uuid
import logging
from typing import Optional, List, Annotated
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator, UUID4, BeforeValidator

from ..exceptions.domain_exceptions import DomainValidationError
from .business_membership import BusinessRole, get_default_permissions_for_role

# Configure logging
logger = logging.getLogger(__name__)


# Custom Pydantic validators for automatic string-to-enum conversion
def validate_business_role(v) -> 'BusinessRole':
    """Convert string to BusinessRole enum."""
    if isinstance(v, str):
        return BusinessRole(v)
    return v

def validate_invitation_status(v) -> 'InvitationStatus':
    """Convert string to InvitationStatus enum."""
    if isinstance(v, str):
        return InvitationStatus(v)
    return v


class InvitationStatus(Enum):
    """Enumeration for invitation statuses."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class BusinessInvitation(BaseModel):
    """
    Business Invitation entity representing an invitation to join a business team.
    
    This entity contains business logic for invitation lifecycle management,
    validation, and expiry handling.
    """
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    id: UUID4 = Field(default_factory=uuid.uuid4)
    business_id: UUID4
    business_name: str = Field(min_length=1)
    invited_by: str = Field(min_length=1)
    invited_by_name: str = Field(min_length=1)
    role: Annotated[BusinessRole, BeforeValidator(validate_business_role)]
    permissions: List[str] = Field(default_factory=list)
    invitation_date: datetime = Field(default_factory=datetime.utcnow)
    expiry_date: datetime
    status: Annotated[InvitationStatus, BeforeValidator(validate_invitation_status)] = InvitationStatus.PENDING
    
    # Contact information (at least one required)
    invited_email: Optional[str] = None
    invited_phone: Optional[str] = None
    
    # Optional fields
    message: Optional[str] = None
    accepted_date: Optional[datetime] = None
    declined_date: Optional[datetime] = None
    
    @field_validator('invited_email')
    @classmethod
    def validate_email_format(cls, v):
        """Validate email format if provided."""
        if v and not cls._is_valid_email_static(v):
            raise ValueError("Invalid email format")
        return v
    
    @field_validator('invited_phone')
    @classmethod
    def validate_phone_format(cls, v):
        """Validate phone format if provided."""
        if v and not cls._is_valid_phone_static(v):
            raise ValueError("Invalid phone format")
        return v
    
    @model_validator(mode='before')
    @classmethod
    def set_default_permissions(cls, values):
        """Set default permissions if none provided."""
        if isinstance(values, dict):
            # Auto-assign default permissions if none provided
            if not values.get('permissions'):
                role = values.get('role')
                if role:
                    # Handle both enum and string values
                    if isinstance(role, str):
                        role = BusinessRole(role)
                    values['permissions'] = get_default_permissions_for_role(role)
        return values
    
    @model_validator(mode='after')
    def validate_invitation_rules(self):
        """Validate business rules after initialization."""
        self._validate_invitation_rules()
        return self
    
    def _validate_invitation_rules(self) -> None:
        """Validate core invitation business rules."""
        # At least one contact method required
        if not self.invited_email and not self.invited_phone:
            raise DomainValidationError("Invitation must have either email or phone")
        
        # Validate expiry date is in the future (only for new invitations)
        if self.status == InvitationStatus.PENDING and self.expiry_date <= datetime.utcnow():
            raise DomainValidationError("Expiry date must be in the future")
    
    @staticmethod
    def _is_valid_email_static(email: str) -> bool:
        """Basic email validation."""
        return "@" in email and "." in email.split("@")[-1]
    
    @staticmethod
    def _is_valid_phone_static(phone: str) -> bool:
        """Basic phone validation."""
        # Remove common phone formatting characters
        cleaned = phone.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        return cleaned.isdigit() and len(cleaned) >= 10
    
    # Instance methods for backward compatibility
    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation."""
        return self._is_valid_email_static(email)
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Basic phone validation."""
        return self._is_valid_phone_static(phone)
    
    @classmethod
    def create_invitation(cls, business_id: uuid.UUID, business_name: str, 
                         invited_by: str, invited_by_name: str, role: BusinessRole,
                         invited_email: Optional[str] = None, 
                         invited_phone: Optional[str] = None,
                         message: Optional[str] = None,
                         permissions: Optional[List[str]] = None,
                         expiry_days: int = 7) -> 'BusinessInvitation':
        """
        Create a new business invitation.
        
        Args:
            business_id: ID of the business
            business_name: Name of the business
            invited_by: ID of the user sending the invitation
            invited_by_name: Name of the user sending the invitation
            role: Role to assign to the invited user
            invited_email: Email address of the invited user
            invited_phone: Phone number of the invited user
            message: Optional message to include with the invitation
            permissions: Custom permissions (uses role defaults if not provided)
            expiry_days: Number of days until invitation expires
            
        Returns:
            New BusinessInvitation instance
        """
        now = datetime.utcnow()
        
        return cls(
            id=uuid.uuid4(),
            business_id=business_id,
            business_name=business_name,
            invited_by=invited_by,
            invited_by_name=invited_by_name,
            role=role,
            permissions=permissions or get_default_permissions_for_role(role),
            invitation_date=now,
            expiry_date=now + timedelta(days=expiry_days),
            invited_email=invited_email,
            invited_phone=invited_phone,
            message=message
        )
    
    def is_expired(self) -> bool:
        """Check if the invitation has expired."""
        return datetime.utcnow() > self.expiry_date
    
    def is_pending(self) -> bool:
        """Check if the invitation is still pending."""
        return self.status == InvitationStatus.PENDING and not self.is_expired()
    
    def can_be_accepted(self) -> bool:
        """Check if the invitation can be accepted."""
        return self.status == InvitationStatus.PENDING and not self.is_expired()
    
    def can_be_declined(self) -> bool:
        """Check if the invitation can be declined."""
        return self.status == InvitationStatus.PENDING and not self.is_expired()
    
    def can_be_cancelled(self) -> bool:
        """Check if the invitation can be cancelled."""
        return self.status == InvitationStatus.PENDING
    
    def can_be_resent(self) -> bool:
        """Check if the invitation can be resent."""
        return self.status in [InvitationStatus.PENDING, InvitationStatus.EXPIRED]
    
    def accept(self) -> 'BusinessInvitation':
        """
        Accept the invitation. Returns new BusinessInvitation instance.
        
        Raises:
            DomainValidationError: If invitation cannot be accepted
        """
        if not self.can_be_accepted():
            if self.is_expired():
                raise DomainValidationError("Cannot accept expired invitation")
            else:
                raise DomainValidationError(f"Cannot accept invitation with status: {self.status.value}")
        
        return self.model_copy(update={
            'status': InvitationStatus.ACCEPTED,
            'accepted_date': datetime.utcnow()
        })
    
    def decline(self) -> 'BusinessInvitation':
        """
        Decline the invitation. Returns new BusinessInvitation instance.
        
        Raises:
            DomainValidationError: If invitation cannot be declined
        """
        if not self.can_be_declined():
            if self.is_expired():
                raise DomainValidationError("Cannot decline expired invitation")
            else:
                raise DomainValidationError(f"Cannot decline invitation with status: {self.status.value}")
        
        return self.model_copy(update={
            'status': InvitationStatus.DECLINED,
            'declined_date': datetime.utcnow()
        })
    
    def cancel(self) -> 'BusinessInvitation':
        """
        Cancel the invitation. Returns new BusinessInvitation instance.
        
        Raises:
            DomainValidationError: If invitation cannot be cancelled
        """
        if not self.can_be_cancelled():
            raise DomainValidationError(f"Cannot cancel invitation with status: {self.status.value}")
        
        return self.model_copy(update={'status': InvitationStatus.CANCELLED})
    
    def mark_expired(self) -> 'BusinessInvitation':
        """Mark the invitation as expired. Returns new BusinessInvitation instance."""
        if self.status == InvitationStatus.PENDING:
            return self.model_copy(update={'status': InvitationStatus.EXPIRED})
        return self
    
    def extend_expiry(self, days: int = 7) -> 'BusinessInvitation':
        """
        Extend the invitation expiry date. Returns new BusinessInvitation instance.
        
        Args:
            days: Number of days to extend the expiry
            
        Raises:
            DomainValidationError: If invitation cannot be extended
        """
        if self.status != InvitationStatus.PENDING:
            raise DomainValidationError("Can only extend pending invitations")
        
        new_expiry = datetime.utcnow() + timedelta(days=days)
        update_data = {'expiry_date': new_expiry}
        
        # If invitation was expired, mark it as pending again
        if self.status == InvitationStatus.EXPIRED:
            update_data['status'] = InvitationStatus.PENDING
        
        return self.model_copy(update=update_data)
    
    def get_recipient_contact(self) -> str:
        """Get the primary contact method for the recipient."""
        if self.invited_email:
            return self.invited_email
        elif self.invited_phone:
            return self.invited_phone
        else:
            return "Unknown"
    
    def get_role_display(self) -> str:
        """Get a human-readable role name."""
        role_names = {
            BusinessRole.OWNER: "Owner",
            BusinessRole.ADMIN: "Administrator",
            BusinessRole.MANAGER: "Manager",
            BusinessRole.EMPLOYEE: "Employee",
            BusinessRole.CONTRACTOR: "Contractor",
            BusinessRole.VIEWER: "Viewer"
        }
        # Handle both enum and string values due to use_enum_values=True
        role_key = self.role if hasattr(self.role, 'value') else BusinessRole(self.role)
        return role_names.get(role_key, "Unknown")
    
    def get_status_display(self) -> str:
        """Get a human-readable status name."""
        status_names = {
            InvitationStatus.PENDING: "Pending",
            InvitationStatus.ACCEPTED: "Accepted",
            InvitationStatus.DECLINED: "Declined",
            InvitationStatus.EXPIRED: "Expired",
            InvitationStatus.CANCELLED: "Cancelled"
        }
        # Handle both enum and string values due to use_enum_values=True
        status_key = self.status if hasattr(self.status, 'value') else InvitationStatus(self.status)
        return status_names.get(status_key, "Unknown")
    
    def get_expiry_summary(self) -> str:
        """Get a human-readable expiry summary."""
        now = datetime.utcnow()
        
        if self.expiry_date < now:
            return "Expired"
        
        time_left = self.expiry_date - now
        days_left = time_left.days
        
        if days_left > 1:
            return f"Expires in {days_left} days"
        elif days_left == 1:
            return "Expires tomorrow"
        else:
            hours_left = time_left.seconds // 3600
            if hours_left > 1:
                return f"Expires in {hours_left} hours"
            else:
                return "Expires soon"
    
    def __str__(self) -> str:
        return f"BusinessInvitation({self.get_recipient_contact()} to {self.business_name})"
    
    def __repr__(self) -> str:
        return (f"BusinessInvitation(id={self.id}, business_id={self.business_id}, "
                f"invited_email='{self.invited_email}', role={self.role}, "
                f"status={self.status})") 