"""
Business Invitation Domain Entity

Represents an invitation for a user to join a business team.
"""

import uuid
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime, timedelta
from enum import Enum

from ..exceptions.domain_exceptions import DomainValidationError
from .business_membership import BusinessRole, DEFAULT_ROLE_PERMISSIONS


class InvitationStatus(Enum):
    """Enumeration for invitation statuses."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


@dataclass
class BusinessInvitation:
    """
    Business Invitation entity representing an invitation to join a business team.
    
    This entity contains business logic for invitation lifecycle management,
    validation, and expiry handling.
    """
    
    id: uuid.UUID
    business_id: uuid.UUID
    business_name: str
    invited_by: str
    invited_by_name: str
    role: BusinessRole
    permissions: List[str]
    invitation_date: datetime
    expiry_date: datetime
    status: InvitationStatus = InvitationStatus.PENDING
    
    # Contact information (at least one required)
    invited_email: Optional[str] = None
    invited_phone: Optional[str] = None
    
    # Optional fields
    message: Optional[str] = None
    accepted_date: Optional[datetime] = None
    declined_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate business rules after initialization."""
        self._validate_invitation_rules()
    
    def _validate_invitation_rules(self) -> None:
        """Validate core invitation business rules."""
        if not self.business_id:
            raise DomainValidationError("Invitation must have a business ID")
        
        if not self.business_name or len(self.business_name.strip()) == 0:
            raise DomainValidationError("Invitation must have a business name")
        
        if not self.invited_by:
            raise DomainValidationError("Invitation must have an inviter")
        
        if not self.invited_by_name or len(self.invited_by_name.strip()) == 0:
            raise DomainValidationError("Invitation must have an inviter name")
        
        # At least one contact method required
        if not self.invited_email and not self.invited_phone:
            raise DomainValidationError("Invitation must have either email or phone")
        
        # Validate email format if provided
        if self.invited_email and not self._is_valid_email(self.invited_email):
            raise DomainValidationError("Invalid email format")
        
        # Validate phone format if provided
        if self.invited_phone and not self._is_valid_phone(self.invited_phone):
            raise DomainValidationError("Invalid phone format")
        
        # Validate expiry date is in the future
        if self.expiry_date <= datetime.utcnow():
            raise DomainValidationError("Expiry date must be in the future")
        
        # Validate permissions are appropriate for role
        if not self.permissions:
            self.permissions = DEFAULT_ROLE_PERMISSIONS.get(self.role, []).copy()
    
    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation."""
        return "@" in email and "." in email.split("@")[-1]
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Basic phone validation."""
        # Remove common phone formatting characters
        cleaned = phone.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        return cleaned.isdigit() and len(cleaned) >= 10
    
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
            permissions=permissions or DEFAULT_ROLE_PERMISSIONS.get(role, []).copy(),
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
    
    def accept(self) -> None:
        """
        Accept the invitation.
        
        Raises:
            DomainValidationError: If invitation cannot be accepted
        """
        if not self.can_be_accepted():
            if self.is_expired():
                raise DomainValidationError("Cannot accept expired invitation")
            else:
                raise DomainValidationError(f"Cannot accept invitation with status: {self.status.value}")
        
        self.status = InvitationStatus.ACCEPTED
        self.accepted_date = datetime.utcnow()
    
    def decline(self) -> None:
        """
        Decline the invitation.
        
        Raises:
            DomainValidationError: If invitation cannot be declined
        """
        if not self.can_be_declined():
            if self.is_expired():
                raise DomainValidationError("Cannot decline expired invitation")
            else:
                raise DomainValidationError(f"Cannot decline invitation with status: {self.status.value}")
        
        self.status = InvitationStatus.DECLINED
        self.declined_date = datetime.utcnow()
    
    def cancel(self) -> None:
        """
        Cancel the invitation.
        
        Raises:
            DomainValidationError: If invitation cannot be cancelled
        """
        if not self.can_be_cancelled():
            raise DomainValidationError(f"Cannot cancel invitation with status: {self.status.value}")
        
        self.status = InvitationStatus.CANCELLED
    
    def mark_expired(self) -> None:
        """Mark the invitation as expired."""
        if self.status == InvitationStatus.PENDING:
            self.status = InvitationStatus.EXPIRED
    
    def extend_expiry(self, days: int = 7) -> None:
        """
        Extend the invitation expiry date.
        
        Args:
            days: Number of days to extend the expiry
            
        Raises:
            DomainValidationError: If invitation cannot be extended
        """
        if self.status != InvitationStatus.PENDING:
            raise DomainValidationError("Can only extend pending invitations")
        
        self.expiry_date = datetime.utcnow() + timedelta(days=days)
        
        # If invitation was expired, mark it as pending again
        if self.status == InvitationStatus.EXPIRED:
            self.status = InvitationStatus.PENDING
    
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
        return role_names.get(self.role, "Unknown")
    
    def get_status_display(self) -> str:
        """Get a human-readable status name."""
        status_names = {
            InvitationStatus.PENDING: "Pending",
            InvitationStatus.ACCEPTED: "Accepted",
            InvitationStatus.DECLINED: "Declined",
            InvitationStatus.EXPIRED: "Expired",
            InvitationStatus.CANCELLED: "Cancelled"
        }
        return status_names.get(self.status, "Unknown")
    
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